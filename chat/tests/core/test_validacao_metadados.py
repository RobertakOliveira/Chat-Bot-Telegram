import pandas as pd
from datetime import datetime
import traceback
from collections import defaultdict
from chat.core.pdf_processing import process_pdf_from_s3, list_pdfs_in_bucket


def validate_pdf_processing(bucket: str) -> pd.DataFrame:
    """
    Processa todos os PDFs no bucket e valida a extração de metadados.
    Retorna um DataFrame com os resultados da validação.
    """
    pdf_files = list_pdfs_in_bucket(bucket)
    validation_results = []

    for pdf in pdf_files:
        try:
            docs = process_pdf_from_s3(pdf['bucket'], pdf['key'])
            if not docs:
                validation_results.append({
                    'file': pdf['key'],
                    'status': 'ERROR',
                    'issues': 'No documents extracted'
                })
                continue

            # Coleta metadados do primeiro chunk (representativo)
            metadata = docs[0].metadata
            issues = []

            # Validação do doc_subtype
            expected_type = _get_expected_doc_type(pdf['key'])
            if metadata.get('doc_subtype') != expected_type:
                issues.append(
                    f"doc_subtype mismatch: expected {expected_type}, got {metadata.get('doc_subtype')}")

            # Validação de jurisdiction e court_level
            if not metadata.get('jurisdiction') or metadata.get('jurisdiction') == 'NÃO IDENTIFICADO':
                issues.append("jurisdiction not identified")

            if not metadata.get('court_level') or metadata.get('court_level') == 'NÃO IDENTIFICADO':
                issues.append("court_level not identified")

            # Validação de campos obrigatórios
            required_fields = ['process_number', 'source', 's3_uri', 'year']
            for field in required_fields:
                if field not in metadata:
                    issues.append(f"missing {field}")

            validation_results.append({
                'file': pdf['key'],
                'status': 'OK' if not issues else 'WARNING',
                'issues': '; '.join(issues) if issues else 'All metadata correct',
                'doc_subtype': metadata.get('doc_subtype'),
                'jurisdiction': metadata.get('jurisdiction'),
                'court_level': metadata.get('court_level'),
                'process_number': metadata.get('process_number'),
                'year': metadata.get('year'),
                'pages': len(docs),
                'text_length': sum(len(d.page_content) for d in docs)
            })

        except Exception as e:
            validation_results.append({
                'file': pdf['key'],
                'status': 'ERROR',
                'issues': str(e)
            })

    return pd.DataFrame(validation_results)


def _get_expected_doc_type(filename: str) -> str:
    """Determina o tipo de documento esperado baseado no nome do arquivo"""
    filename_lower = filename.lower()

    if 'acordao-recorrido' in filename_lower or 'acordão_recorrido' in filename_lower:
        return 'acordao_recorrido'
    elif 'acordao-embargos' in filename_lower or 'acordão_embargos' in filename_lower:
        return 'acordao_embargos'
    elif 'recurso-extraordinario' in filename_lower or 'recurso_extraordinário' in filename_lower:
        return 'recurso_extraordinario'
    elif 'decisao-admissibilidade' in filename_lower:
        return 'decisao_admissibilidade'
    elif 'agravo' in filename_lower:
        return 'agravo'
    return 'outros'


if __name__ == "__main__":
    print("=== TESTE DE METADADOS ===")
    print(f"Iniciando processamento em {datetime.now().isoformat()}")

    try:
        results = validate_pdf_processing('consultor-juridico')
        results.to_csv('metadata_validation_report.csv', index=False)

        print("\n=== RESUMO EXECUTIVO ===")
        print(f"Total de arquivos: {len(results)}")
        print(f"Sucesso: {len(results[results['status'] == 'OK'])}")
        print(f"Avisos: {len(results[results['status'] == 'WARNING'])}")
        print(f"Erros: {len(results[results['status'] == 'ERROR'])}")

        print("\n=== DETALHES ===")
        print(results.groupby(['doc_subtype', 'status']
                              ).size().unstack(fill_value=0))

        problem_files = results[results['status'] != 'OK']
        if not problem_files.empty:
            print("\n=== ARQUIVOS COM PROBLEMAS ===")
            for _, row in problem_files.iterrows():
                print(f"\n{row['file']} [{row['status']}]")
                print(f"Problemas: {row['issues']}")
                if pd.notna(row.get('jurisdiction')):
                    print(f"Jurisdição: {row['jurisdiction']}")
        else:
            print("\nTodos os arquivos processados com sucesso!")

    except Exception as e:
        print(f"\nERRO GLOBAL: {str(e)}")
        traceback.print_exc()

# Navegue até a pasta raiz e execute:
#     python -m chat.tests.core.test_validacao_metadados

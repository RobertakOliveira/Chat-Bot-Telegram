import pandas as pd
import re
import os
from datetime import datetime
import traceback
from chat.core.pdf_processing import process_pdf_from_s3, list_pdfs_in_bucket


def validate_pdf_processing(bucket: str) -> pd.DataFrame:
    """
    Processa todos os PDFs no bucket e valida a extração de metadados.
    Retorna um DataFrame com os resultados da validação.
    """
    pdf_files = list_pdfs_in_bucket(bucket)
    validation_results = []

    # Campos obrigatórios conforme implementação real
    REQUIRED_FIELDS = ['doc_type', 'source', 'page']

    for pdf in pdf_files:
        try:
            file_key = pdf['key']
            docs = process_pdf_from_s3(pdf['bucket'], file_key)

            if not docs:
                validation_results.append({
                    'file': file_key,
                    'status': 'ERROR',
                    'issues': 'No documents extracted',
                    'chunks': 0
                })
                continue

            # Validação em uma amostra de chunks
            sample_chunks = docs[:3]  # Verifica primeiros 3 chunks
            issues = []
            metadata = sample_chunks[0].metadata

            # 1. Validação do tipo documental
            expected_type = _get_expected_doc_type(file_key)
            if metadata.get('doc_type') != expected_type:
                issues.append(
                    f"Type mismatch: {metadata.get('doc_type')} vs {expected_type}")

            # 2. Campos obrigatórios
            for field in REQUIRED_FIELDS:
                if field not in metadata:
                    issues.append(f"Missing {field}")
                elif not metadata[field]:  # Verifica valores vazios
                    issues.append(f"Empty {field}")

            # 3. Consistência entre chunks
            for doc in sample_chunks[1:]:
                if doc.metadata.get('doc_type') != metadata['doc_type']:
                    issues.append("Inconsistent doc_type between chunks")
                    break

            # 4. Validação numérica da página
            try:
                if not (1 <= metadata.get('page', 0) <= 1000):  # Faixa razoável
                    issues.append(
                        f"Invalid page number: {metadata.get('page')}")
            except TypeError:
                issues.append("Page number not numeric")

            validation_results.append({
                'file': file_key,
                'status': 'OK' if not issues else 'WARNING',
                'issues': '; '.join(issues) if issues else 'All metadata valid',
                'doc_type': metadata.get('doc_type'),
                'source': metadata.get('source'),
                'page': metadata.get('page'),
                'chunks': len(docs),
                'text_length': sum(len(d.page_content) for d in docs)
            })

        except Exception as e:
            validation_results.append({
                'file': file_key,
                'status': 'ERROR',
                'issues': f"Processing error: {str(e)}",
                'chunks': 0
            })

    return pd.DataFrame(validation_results)


def _get_expected_doc_type(filename: str) -> str:
    """Determina o tipo de documento esperado baseado no nome do arquivo"""
    filename = os.path.basename(filename).lower().replace('.pdf', '')

    # Padrão igual ao usado no PDF Processing
    match = re.search(r'^\d+-(.+)$', filename)

    if match:
        doc_type = match.group(1).replace('-', ' ').title()
    else:
        doc_type = "outros"

    return doc_type


if __name__ == "__main__":
    print("=== VALIDAÇÃO DE METADADOS (v2) ===")
    print(f"Iniciando processamento em {datetime.now().isoformat()[:19]}")

    try:
        results = validate_pdf_processing('consultor-juridico')
        results.to_csv('metadata_validation_report.csv', index=False)

        print("\n=== RESUMO EXECUTIVO ===")
        # Análise otimizada
        stats = results.groupby('status').size()
        print(f"\n● Arquivos processados: {len(results)}")
        print(f"● Sucesso: {stats.get('OK', 0)}")
        print(f"● Avisos: {stats.get('WARNING', 0)}")
        print(f"● Erros: {stats.get('ERROR', 0)}")

        # Detalhamento de problemas
        if not results[results['status'] == 'OK'].empty:
            print("\n🔍 Principais problemas:")
            problem_df = results[results['status'] != 'OK']
            print(problem_df[['file', 'issues']].head(
                5).to_string(index=False))

        print(f"\nRelatório completo salvo em: metadata_validation_report.csv")

    except Exception as e:
        print(f"\n❌ ERRO GLOBAL: {str(e)}")
        traceback.print_exc()

# Navegue até a pasta raiz e execute:
#     python -m chat.tests.core.test_validacao_metadados

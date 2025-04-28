# test_chroma_retrieval.py
import chromadb
import os
from rich.console import Console
from rich.table import Table
from rich import box
from rich.panel import Panel
from chat.core.query_processing import preprocess_query
from chat.utils.logger import get_logger
from chat.utils.config import config

console = Console()
logger = get_logger("test_chroma_retrieval")

TEST_QUERIES = {
    "Agravo": [
        "Qual o prazo para interposição de agravo de instrumento?",
        "Quais os requisitos para cabimento de agravo interno?",
        "Quem é o remetente deste agravo?",
        "Qual o número do processo associado a este agravo?",
        "Contra qual decisão este agravo está sendo interposto?",
        "A qual instância superior este agravo é direcionado?",
        "Qual o fundamento legal para a interposição deste agravo?",
        "Em que data foi elaborado este agravo?",
        "Quem é o advogado que assina este agravo?",
        "Qual o número da OAB do advogado?",
        "O agravante alega qual tipo de violação constitucional?",
        "O que o agravante alega sobre a intimação para o julgamento do recurso de apelação?",
        "Quais são os pedidos do agravante neste documento?"
    ],
    "Recurso Extraordinario": [
        "Como fundamentar um recurso extraordinário com base no art. 102 da CF?",
        "Quais são os pressupostos de admissibilidade do RE?"
    ],
    "Acordao Recorrido": [
        "Cite os principais fundamentos de um acórdão recorrido sobre furto qualificado.",
        "Como contestar um acórdão que aplicou a majorante de reincidência?"
    ],
    "Acordao Embargos": [
        "Qual a diferença entre embargos de declaração e embargos infringentes?",
        "Em que casos os embargos de declaração são cabíveis?"
    ],
    "Decisao Admissibilidade": [
        "Quais os critérios para uma decisão de admissibilidade em recurso especial?",
        "Como recorrer de uma decisão que negou seguimento a um recurso?"
    ]
}


def display_results(query: str, results: dict):
    """Exibe os documentos recuperados em formato rico"""
    console.print(
        Panel.fit(f"[bold]🔍 Resultados para:[/bold] [cyan]'{query}'[/cyan]"))

    for i, (doc, meta) in enumerate(zip(results['documents'][0], results['metadatas'][0]), 1):
        table = Table.grid(padding=(0, 2))
        table.add_column(style="bold blue", width=15)
        table.add_column(style="green")

        table.add_row("→ Documento", f"[bold]#{i}[/bold]")
        table.add_row("Tipo:", meta.get('doc_type', 'N/A'))
        table.add_row("Fonte:", meta.get('source', 'N/A'))
        table.add_row("Conteúdo:", f"[dim]{doc[:200]}...[/dim]")

        console.print(table)
        console.print("─" * 50)


def run_query_tests(collection):
    total_success = 0
    total_failures = 0

    for doc_type, queries in TEST_QUERIES.items():
        console.rule(f"[bold blue]🔍 TESTANDO TIPO: {doc_type}")

        summary_table = Table(
            show_header=True, header_style="bold magenta", box=box.SIMPLE)
        summary_table.add_column("📌 Pergunta", style="dim", overflow="fold")
        summary_table.add_column("↓ Tipo Detectado")
        summary_table.add_column("↓ Resultado")

        for query in queries:
            try:
                processed = preprocess_query(query)
                detected_type = processed["document_type"] or "Não detectado"

                results = collection.query(
                    query_embeddings=[processed["embedding"]],
                    where=processed["search_filters"],
                    n_results=2
                )

                if not results['documents'][0]:
                    summary_table.add_row(
                        query, detected_type, "[red]⚠️ Nenhum documento")
                    total_failures += 1
                else:
                    summary_table.add_row(
                        query, detected_type, "[green]✅ Encontrado")
                    total_success += 1
                    # Exibe os chunks encontrados
                    display_results(query, results)

            except Exception as e:
                summary_table.add_row(query, "Erro", f"[bold red]🔥 {str(e)}")
                total_failures += 1

        console.print(summary_table)

    console.rule("[bold green]Resumo Final")
    console.print(f"✅ Sucessos: [bold green]{total_success}")
    console.print(f"❌ Falhas: [bold red]{total_failures}")
    console.print(
        f"🔍 Total de perguntas testadas: [bold blue]{total_success + total_failures}")


def main():
    try:
        chroma_client = chromadb.PersistentClient(path=config.CHROMA_DB_PATH)
        collection = chroma_client.get_collection(name="collection_85283")

        logger.info("Conexão com ChromaDB estabelecida com sucesso")
        console.print(Panel.fit(
            f"[bold yellow]🔍 Diagnóstico Inicial[/bold yellow]\n"
            f"Documentos na coleção: [cyan]{collection.count()}[/cyan]\n"
            f"Tipos encontrados: [cyan]{set(meta.get('doc_type') for meta in collection.get(include=['metadatas'])['metadatas'])}[/cyan]",
            subtitle="[dim]Pré-teste[/dim]"
        ))

        run_query_tests(collection)

    except Exception as e:
        console.print(Panel.fit(
            f"[bold red]🔥 Erro crítico[/bold red]\n{str(e)}",
            subtitle="[dim]Dicas[/dim]"
        ))
        console.print("1. Verifique o nome da collection")
        console.print(
            f"2. Confira o diretório: [cyan]{os.path.abspath(config.CHROMA_DB_PATH)}[/cyan]")


if __name__ == "__main__":
    main()

# Navegue até a pasta raiz e execute:
#     python -m chat.tests.core.test_chroma_retrieval

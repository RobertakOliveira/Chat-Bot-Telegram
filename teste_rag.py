from chat.scripts.rag_flow import rag_chain

def interactive_test():
    print("Teste interativo iniciado. Você pode digitar 'sair' para encerrar.")
    
    while True:
        # Solicita uma pergunta
        query = input("Digite sua pergunta: ")
        
        # Se o usuário digitar 'sair', o loop será encerrado
        if query.lower() == 'sair':
            print("Saindo do teste interativo...")
            break
        
        # Chama a função rag_chain para obter a resposta
        result = rag_chain(query)
        
        # Exibe a resposta gerada
        print(f"Resposta gerada: {result}")

interactive_test()
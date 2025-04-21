def handler(event, context):
    return {
        "statusCode": 200,
        "body": f"Fluxo finalizado com sucesso. Último status: {event.get('etapa')}"
    }

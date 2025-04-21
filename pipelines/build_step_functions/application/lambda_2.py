def handler(event, context):
    event["etapa"] = "Lambda 2 completada"
    return event

def handler(event, context):
    event["etapa"] = "Lambda 3 completada"
    return event

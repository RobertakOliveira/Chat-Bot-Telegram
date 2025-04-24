import json
from send_Reply  import sendReply
def lambda_handler(event, context):
    body = json.loads(event['body'])

    print("*** Received event")

    chat_id = body['message']['chat']['id']
    user_name = body['message']['from']['username']
    message_text = body['message']['text']
    message_id = body['message']['message_id'] 

    print(f"*** chat id: {chat_id}")
    print(f"*** user name: {user_name}")
    print(f"*** message text: {message_text}")
    print(json.dumps(body))

    # aqui chama o rag 
    reply_message = message_text
    

    sendReply(chat_id, reply_message,message_id)

    return {
        'statusCode': 200,
        'body': json.dumps('Message processed successfully')
    }    
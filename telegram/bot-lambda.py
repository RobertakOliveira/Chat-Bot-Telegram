import json
import urllib3

#token do bot
BOT_TOKEN="SEU-TOKEN-AQUI"

#resposta para cada request enviado pelo usuario do bot
def sendReply(chat_id, message):
    reply = {
        "chat_id": chat_id,
        "text": message#retorna a mensagem enviada pelo usuario
    }

    http = urllib3.PoolManager()
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    encoded_data = json.dumps(reply).encode('utf-8')
    http.request('POST', url, body=encoded_data, headers={'Content-Type': 'application/json'})
    #print para monitorar o retorno do bot
    print(f"*** Reply : {encoded_data}")

#função principal que recebe o evento do telegram extraindo a mensagem enviada pelo usuario.
def lambda_handler(event, context):
    body = json.loads(event['body'])

    print("*** Received event")

    chat_id = body['message']['chat']['id']
    user_name = body['message']['from']['username']
    message_text = body['message']['text']

    print(f"*** chat id: {chat_id}")
    print(f"*** user name: {user_name}")
    print(f"*** message text: {message_text}")
    print(json.dumps(body))

    reply_message = f"Reply to {message_text}"

    sendReply(chat_id, reply_message)

    return {
        'statusCode': 200,
        'body': json.dumps('Message processed successfully')
    }    
import json
import urllib3
import time

BOT_TOKEN=""


http = urllib3.PoolManager()


def sendReply(chat_id, full_message, _original_message_id):
    # Envia mensagem inicial vazia
    url_send = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    initial_data = {
        "chat_id": chat_id,
        "text": full_message # pode deixar três pontinhos pra parecer digitando
    }
    encoded_data = json.dumps(initial_data).encode('utf-8')
    response = http.request('POST', url_send, body=encoded_data, headers={'Content-Type': 'application/json'})

    # Decodifica e trata a resposta
    resp_json = json.loads(response.data.decode('utf-8'))

    # Verifica se a resposta contém o campo "result"
    if "result" not in resp_json:
        print("*** Erro ao enviar mensagem inicial:")
        print(resp_json)
        return

    #message_id = resp_json["result"]["message_id"]

    # Agora edita a mensagem palavra por palavra
    #words = full_message.split()
    #current_text = ""

    #for word in words:
    #    current_text += word + " "

        #edit_data = {
        #    "chat_id": chat_id,
        #    "message_id": message_id,
        #    "text": current_text.strip()
        #}

        #encoded_edit = json.dumps(edit_data).encode('utf-8')
        #url_edit = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
        #http.request('POST', url_edit, body=encoded_edit, headers={'Content-Type': 'application/json'})

        #time.sleep(0.1)  # Delay entre palavras

    #print(f"*** Streamed message: {full_message}")

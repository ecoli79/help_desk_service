import requests
import time
import db_working
import config

# Token for bot
bot_token = config.get_config_data('telegram_bot')['token']
base_url = f"https://api.telegram.org/bot{bot_token}"

def get_data_and_send_message():
    try:
        tickets = db_working.get_tickets_for_send()
        
        for ticket in tickets:
            chat_id = ticket[1]
            message_text = (ticket[2] or '') + '\n'
            
            if message_text == '\n':
                message_text = 'Ваша заявка закрыта. Спасибо за Ваше обращение.'

            # Sending the message
            send_message_url = f"{base_url}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': message_text,
                'reply_to_message_id': ticket[3]
            }
            response = requests.post(send_message_url, data=payload)
            
            if response.status_code == 200:
                db_working.update_ticket(ticketId=ticket[0], sended=True)
            else:
                print(f"Failed to send message: {response.text}")

    except Exception as e:
        print(e)

# Schedule-like loop
while True:
    time.sleep(5)
    get_data_and_send_message()
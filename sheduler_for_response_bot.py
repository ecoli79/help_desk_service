import telegram
import psycopg2
import schedule
import time
# local module
import config
import db_working

#token for bot
bot_token = config.get_config_data('telegram_bot')['token']

# bot for send messages
bot = telegram.Bot(token = bot_token)


def get_data_and_send_message():
    try:
        tickets = db_working.get_tickets_for_send()
        
        for ticket in tickets:
        
            message_text = ticket[2] + '\n'
            bot.send_message(chat_id=ticket[1], text=message_text, reply_to_message_id=ticket[3])
            
            db_working.update_ticket(ticket_id = ticket[0], sended = True)
    
    except Exception as e:
        print(e)


#schedule.every().day.at("10:00").do(get_data_and_send_message)

# цикл выполнения заданий по графику
while True:
    #schedule.run_pending() # проверяем, есть ли задания, которые нужно выполнить
    time.sleep(5)
    get_data_and_send_message()

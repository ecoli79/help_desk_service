from telegram import ReplyKeyboardMarkup, Message
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters
import config
import db_working
bot_token = config.get_config_data('telegram_bot')['token']


# function for get attachment from messaage
def get_attachment(message: Message):
    """
    Checking any attachment
    """
    if message.document is not None:
        return message.document
    elif message.photo:
        # Получаем фото с максимальным размером
        return message.photo[-1]
    elif message.video is not None:
        return message.video
    elif message.audio is not None:
        return message.audio
    elif message.voice is not None:
        return message.voice
    elif message.sticker is not None:
        return message.sticker
    else:
        return None

def save_ticket(chat_id, message_id, ticket_text, ticket_type, image_path, user_data):
    """save ticket info to disk

    Args:
        chat_id (int): _description_
        ticket_text (str): _description_
        ticket_type (int): _description_
        image_path (str): _description_
    """
    
    db_working.insert_ticket(user_data.get('username'),
                             user_data.get('full_name'),
                             ticket_type,
                             ticket_text,
                             chat_id,
                             message_id,
                             image_path)


# keyboard for type of tickets

reply_keyboard_type_tickets = [['Подписание', 'Оборудование', 'Другое']]
markup_type_tickets = ReplyKeyboardMarkup(reply_keyboard_type_tickets, one_time_keyboard=True)

# Создаем список состояний диалога
TYPE, IMAGE, TEXT = range(3)


# Функция-обработчик команды /start
def start(update, context):
    
    update.message.reply_text('Для создания новой заявки\nнеобходиом выбрать тип заявки.', reply_markup = markup_type_tickets)
    
    context.user_data['chat_id'] = update.effective_chat.id
    
    return TYPE


# Функция-обработчик шага 1. Получаем имя пользователя
def first_step(update, context):
 
    context.user_data['ticket_type_name'] = update.message.text
    
    #context.user_data['name'] = update.message.text
    update.message.reply_text("""Если есть картинка с ошибкой можете прикрепить ее через скрепку
                              Если картинки просто отправьте любой текст например 'нет'""")
    return IMAGE


def second_step(update, context):
    
    attachment  = get_attachment(update.message)
    
    if attachment:
        file = context.bot.getFile(attachment.file_id)
        if file: 
            ext = file.file_path.split('/')[-1].split('.')[-1]
            image_name = f'{file.file_unique_id}.{ext}'
            image_path = image_name #f'./img/{image_name}'
            context.user_data['image_path'] = image_path
            file.download('./static/img/' + image_path)
    else:
        context.user_data['image_path'] = ''
                
    update.message.reply_text('Ок, теперь опишите ошибку. Можно голосом надиктовать.')
    
    return TEXT


# Функция-обработчик шага 2. Получаем возраст пользователя
def third_step(update, context):
    context.user_data['age'] = update.message.text
    update.message.reply_text(f'Спасибо за вашу заяву! Ответ будет в этом чате.')
    
    
    # save data to db
    ticket_text = update.message.text
    message_id = update.effective_message.message_id
        
    user_data = {'full_name': f'{update.effective_chat.first_name} {update.effective_chat.last_name}', 
                    'username': update.effective_chat.username,
                    }
    
    save_ticket(context.user_data.get('chat_id', ''),
                    message_id,
                    ticket_text, 
                    context.user_data.get('ticket_type_name',''),
                    context.user_data.get('image_path',''),
                    user_data)
    
    update.message.reply_text('Сделать новую заявку?', reply_markup = markup_type_tickets)
    # update.message.reply_text('Сделать новую заявку?', reply_markup={
    #     'keyboard': [['Новая заявка']],
    #     'one_time_keyboard': True,
    # })
    return TYPE


# Функция-обработчик ответа пользователя на запрос повтора диалога
def restart(update, context):
    # text = update.message.text.lower()
    # if text == 'новая заявка':
    return start(update, context)
    # else:
    #     update.message.reply_text('Хорошо, мы заканчиваем диалог.')
    #     return ConversationHandler.END


# Функция-обработчик прерывания диалога с помощью команды /cancel
def cancel(update, context):
    update.message.reply_text('Диалог отменен')
    return ConversationHandler.END


def main():
    # Создаем объект класса Updater и получаем токен бота
    updater = Updater(bot_token, use_context=True)

    # Создаем обработчики команд и сообщений и добавляем их в Dispatcher
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            TYPE: [MessageHandler(Filters.text, first_step)],
            IMAGE: [MessageHandler(Filters.all, second_step)],
            TEXT: [MessageHandler(Filters.text, third_step)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, restart))

    # Запускаем бота с бесконечным циклом работы
    updater.start_polling()
    #updater.idle()


if __name__ == '__main__':
    main()

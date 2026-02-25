import time
import telegram
from telegram  import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, Message, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, CommandHandler, Updater, MessageHandler, Filters, ConversationHandler, JobQueue
import logging
import db_working

# local module
import config


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

#token for bot
bot_token = config.get_config_data('telegram_bot')['token']

# bot for send messages
#bot = telegram.bot(token = bot_token)



TYPE, IMAGE, TICKET_TEXT = range(3)

updater = Updater(token=bot_token)
dispatcher = updater.dispatcher

reply_keyboard = [['Подписание', 'Оборудование', 'Другое']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


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



def start(update, context):
       
    # update.message.reply_text('Нажмите на кнопку, чтобы начать диалог', reply_markup=reply_markup)
    keyboard =[[ InlineKeyboardButton('Создать заявку', callback_data=str(TYPE)),]]
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Чтобы сделать новую заявку нажмите кнопку\n"Создать заявку"', reply_markup = reply_markup)
                            #    reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                            #                                     #one_time_keyboard=True,
                            #                                     input_field_placeholder='Выберите тип заявки'))
    context.user_data['chat_id'] = update.effective_chat.id
     
# def start(update, _):
#     """Вызывается по команде `/start`."""
#     # Получаем пользователя, который запустил команду `/start`
#     user = update.message.from_user
#     #logger.info("Пользователь %s начал разговор", user.first_name)
#     # Создаем `InlineKeyboard`, где каждая кнопка имеет 
#     # отображаемый текст и строку `callback_data`
#     # Клавиатура - это список строк кнопок, где каждая строка, 
#     # в свою очередь, является списком `[[...]]`
#     keyboard = [
#         [
#             InlineKeyboardButton("1", callback_data=str(TYPE)),
#             InlineKeyboardButton("2", callback_data=str(TICKET_TEXT)),
#         ]
#     ]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     # Отправляем сообщение с текстом и добавленной клавиатурой `reply_markup`
#     update.message.reply_text(
#         text="Запустите обработчик, выберите маршрут", reply_markup=reply_markup
#     )
#     # Сообщаем `ConversationHandler`, что сейчас состояние `FIRST`
    
    return TYPE

# def button_callback(update, context):
#     query = update.callback_query
#     query.answer()
    
    
#     keyboard = [['Подать заявку']]
    
#     reply_markup = InlineKeyboardMarkup(keyboard)
    
#     query.edit_message_text(text="Хорошо, начнем!", reply_markup = reply_markup)
    
#     context.user_data['chat_id'] = update.effective_chat.id
    
#     #return type_tiket(update, context)
#     return TYPE


def type_tiket(update, context):
    ticket_type = 0
    if update.message.text == 'Подписание':
        ticket_type = 0
    if update.message.text == 'Оборудование':
        ticket_type = 1
    if update.message.text == 'Другое':
        ticket_type = 2
    
    context.user_data['ticket_type'] = ticket_type
    context.user_data['ticket_type_name'] = update.message.text
    update.message.reply_text('Есть картинка с ошибкой? Если есть отправьте. Если картинки нет напишите нет.')
            
    return IMAGE

def image(update, context):
    """receive image from user and save it in IMAGE_PATH
    """
    attachment  = get_attachment(update.message)
    
    if attachment:
        file = context.bot.getFile(attachment.file_id)
        if file: 
            ext = file.file_path.split('/')[-1].split('.')[-1]
            image_name = f'{file.file_unique_id}.{ext}'
            image_path = image_name #f'./img/{image_name}'
            context.user_data['image_path'] = image_path
            file.download('./static/img/' + image_path)
                
    update.message.reply_text('Ок, теперь опишите ошибку. Можно голосом надиктовать.')
      
    return TICKET_TEXT

def skip_image(update, context):
    update.message.reply_text('Ок, давайте без картинки.')
    
    update.messaage.reply_text('Ок, теперь опишите ошибку. Можно голосом надиктовать.')
    
    return TICKET_TEXT

def text_ticket(update, context):
    
    attachment = get_attachment(update.message)
    
    if attachment:
        if update.message.audio is not None:
            file = context.bot.getFile(update.message.document.file_id)
            if file: 
                ext = file.file_path.split('/')[-1].split('.')[-1]
                audio_name = f'{file.file_unique_id}.{ext}'
                audio_path = f'./audio/{audio_name}'
                file.download(audio_path)
    else:        
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
        
    update.message.reply_text('Ваша заявка отправлена. Ждите ответа в этом чате.')
    
    return ConversationHandler.END
    

def cancel(update, context):
    update.message.reply_text('Ну ладно, не сегодня так не сегодня))', reply_markup=ReplyKeyboardRemove())
   
    return ConversationHandler.END
           
  
# def send_message(update, context, chat_id, text_message):
#     time.sleep(10)
#     context.bot.send_message(chat_id=chat_id, text=text_message)
    

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
    
    
    # with open('data.txt', 'a+') as f:
    #     row = f'chat_id:{chat_id} ticket_type:{ticket_type} ticket_text:{ticket_text} image_path:{image_path}\n'
    #     f.write(row)


  
conv_handler = ConversationHandler(
               entry_points=[CommandHandler('start', start)],
               #entry_points=[CallbackQueryHandler(type_tiket, pattern='^type_tiket$')],
               states={
                     TYPE: [MessageHandler(Filters.text, type_tiket)],
                     IMAGE: [MessageHandler(Filters.all, image), CommandHandler('skip', skip_image)],
                     TICKET_TEXT: [MessageHandler(Filters.text, text_ticket)]
               },
                fallbacks=[CommandHandler('cancel', cancel)]
)

dispatcher.add_handler(conv_handler)
#dispatcher.add_handler(CallbackQueryHandler(button_callback))
  
updater.start_polling()
import telebot
from telebot import types, formatting
import config
import db_working
import re

bot_token = config.get_config_data('telegram_bot')['token']

bot =telebot.TeleBot(bot_token)


class File():
    def __init__(self, message, bot):
        self.content_type = message.content_type 
        self.file_id = ''
        
        if self.content_type == 'photo':
            self.file_id = message.photo[-1].file_id
        
        if self.content_type == 'document':
            self.file_id = message.document.file_id
        
        if self.content_type == 'voice':
            voice_info = message.voice
            self.file_id = voice_info.file_id
        
        if self.content_type == 'audio':
            audio_info = message.audio
            self.file_id = audio_info.file_id
            
        self.file_info = bot.get_file(self.file_id)
        self.file_path_server = self.file_info.file_path
        self.file_name = f"{self.file_info.file_unique_id}.{self.file_path_server.split('.')[-1]}"
        
        
    def save(self):
        if self.content_type == 'photo' or self.content_type == 'document':
            item_file = bot.download_file(self.file_path_server)
            with open(f"./static/img/{self.file_name}", 'wb') as f:
                f.write(item_file)
        
        if self.content_type == 'voice' or self.content_type == 'audio':
            file_bytes = bot.download_file(self.file_path_server)
            self.file_name = self.file_name.split('.')[0] + '.wav'             
            with open(f"./static/audio/{self.file_name}", 'wb') as f:
                f.write(file_bytes)
                      
        return self.file_name
        
    def voice_to_text(self):
        if self.content_type == 'voice':
            pass


class Ticket():
    def __init__(self, chat_id, message_id, username, user_fullname, ticket_type, ticket_text, image_path, voice_path):
        self.chat_id = chat_id
        self.message_id = message_id
        self.username = username
        self.user_fullname = user_fullname
        self.ticket_type = ticket_type
        self.ticket_text = ticket_text
        self.image_path = image_path
        self.voice_path = voice_path
        
    def ticket_save(self):
        
        try:        
            db_working.insert_ticket(self.username, 
                                    self.user_fullname,
                                    self.ticket_type,
                                    self.ticket_text,
                                    self.chat_id,
                                    self.message_id,
                                    self.image_path,
                                    self.voice_path)
            
            return True
        
        except (Exception) as error:
            print(error)
            return False
       
def cat_long_ticket_text(text):
    if len(text) > 38:
        text = text[:39] + '\.\.\.'
    
    return text        

  
ticket_types = ['Подписание', 'Оборудование', 'Доступ к системам', 'Другое']
start_buttons = ['Новая заявка']

Keys_for_tickets = [types.KeyboardButton(ticket_type) for ticket_type in ticket_types]
Keys_for_start = [types.KeyboardButton(ticket_type) for ticket_type in start_buttons]


markup_ticket_types = types.ReplyKeyboardMarkup(resize_keyboard = True, one_time_keyboard=True)
markup_start_buttons = types.ReplyKeyboardMarkup()


for key in Keys_for_tickets:
    markup_ticket_types.add(key)

text_for_desctiption = """
Если у вас есть картинка или фотография ошибки, прикрепите ее через скрепку.
После этого опишите свою проблему как можно подробнее,
например: Не печатает принтер в поликлинике № 3 каб 30 Телефон для связи 99999999"""

text_for_description2 = """
Теперь опишите свою проблему максимально подробно,
например: Поликлиника Гашкова 41, каб. 13, не включается компьютер. Телефон для связи 99999999."""

data = {'ticket_type': '',
        'ticket_text': '',
        'image_path': '',
        'voice_path': ''}

@bot.message_handler(commands= ['start'])
def start_conversation(message):
    bot.send_message(message.chat.id, 'Создание новой заявки. Выберите тип заявки, которую Вы хотите создать', reply_markup = markup_ticket_types)
   

@bot.message_handler(func=lambda message: message.text in ticket_types)
def second_step(message):
    text_message = message.text
    if text_message == 'Подписание':
        text_for_reply = formatting.mbold(text_message)
        data['ticket_type'] = text_message
        bot.send_message(message.chat.id, f'Вы выбрали тип заявки: {text_for_reply}' + text_for_desctiption, parse_mode = 'Markdown', reply_markup = markup_ticket_types)
    if text_message == 'Оборудование':
        text_for_reply = formatting.mbold(text_message)
        data['ticket_type'] = text_message
        bot.send_message(message.chat.id, f'Вы выбрали тип заявки: {text_for_reply}' + text_for_desctiption, parse_mode='Markdown', reply_markup = markup_ticket_types)
    if text_message == 'Доступ к системам':
        text_for_reply = formatting.mbold(text_message)
        data['ticket_type'] = text_message
        bot.send_message(message.chat.id, f'Вы выбрали тип заявки: {text_for_reply}' + text_for_desctiption, parse_mode='Markdown', reply_markup = markup_ticket_types)
    if text_message == 'Другое':
        text_for_reply = formatting.mbold(text_message)
        data['ticket_type'] = text_message
        bot.send_message(message.chat.id, f'Вы выбрали тип заявки: {text_for_reply}' + text_for_desctiption, parse_mode='Markdown', reply_markup = markup_ticket_types)


@bot.message_handler(content_types=['text'])
def final_step(message):
    if len(data['ticket_type']) == 0:
        bot.send_message(message.chat.id, 'Вы не выбрали тип заявки. Сначала нужно выбрать тип заявки.', reply_markup = markup_ticket_types) 
    else:
        text_for_reply = cat_long_ticket_text(message.text)
        if len(data['ticket_text']) == 0:
            text_for_reply = formatting.mbold(text_for_reply)
            data['ticket_text'] = message.text
            ticket = Ticket(message.chat.id,
                            message.id,
                            message.from_user.username,
                            message.from_user.full_name,
                            data.get('ticket_type'),
                            data.get('ticket_text'),
                            data.get('image_path'),
                            data.get('voice_path'))
            ticket.ticket_save()
            data['ticket_type'], data['ticket_text'], data['image_path'], data['voice_path'] = ('', '' , '', '')
            
            bot.send_message(message.chat.id, f'Ваша заявка: {text_for_reply} принята', parse_mode = 'Markdown', reply_markup = markup_ticket_types )          
    
@bot.message_handler(content_types=['photo', 'document'])
def save_image(message):
    
    if message.content_type == 'photo' or message.document.mime_type.startswith('image/'):
        
        file = File(message, bot)
        data['image_path'] = file.save()
                
        bot.send_message(message.chat.id, 'Картинка загружена.' + text_for_description2, reply_markup = markup_ticket_types)
    else:
        bot.send_message(message.chat.id, f'Вы приложили НЕ картинку. Попробуйте еще раз.', reply_markup = markup_ticket_types)
    
@bot.message_handler(content_types=['voice', 'audio'])
def save_voice_audio(message):
    
    if message.content_type == 'voice' or message.content_type == 'audio':
        file = File(message, bot)
        data['voice_path'] = file.save()
        if data.get('ticket_type'):
            data['ticket_text'] = 'Описание проблемы в голосовом сообщении. Смотри вложение в заявке.'
            ticket = Ticket(message.chat.id,
                            message.id,
                            message.from_user.username,
                            message.from_user.full_name,
                            data.get('ticket_type'),
                            data.get('ticket_text'),
                            data.get('image_path'),
                            data.get('voice_path'))
            ticket.ticket_save()
            data['ticket_type'], data['ticket_text'], data['image_path'], data['voice_path'] = ('', '' , '', '')
        
        bot.send_message(message.chat.id, 'Голосовое сообщение загружено. Ваша заявка принята в работу.', reply_markup = markup_ticket_types)

    
bot.infinity_polling()



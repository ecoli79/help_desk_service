from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

import config
bot_token = config.get_config_data('telegram_bot')['token']

# создаем список состояний диалога
FIRST, SECOND = range(2)

def start(update, context):
    # показываем пользователю клавиатуру с двумя кнопками: "Первый шаг" и "Отмена"
    buttons = [['Первый шаг'], ['Отмена']]
    reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True)
    update.message.reply_text('Начало диалога. Выберите первый шаг:',
                              reply_markup=reply_markup)

    # переводим бота в режим ожидания ответа пользователя на сообщение с клавиатурой
    return FIRST

def first_step(update, context):
    # показываем пользователю сообщение с результатом выбора первого шага и клавиатуру с двумя кнопками: "Второй шаг" и "Отмена"
    buttons = [['Второй шаг'], ['Отмена']]
    reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True)
    update.message.reply_text(f'Вы выбрали {update.message.text}. Выберите следующий шаг:',
                              reply_markup=reply_markup)

    # переводим бота в режим ожидания ответа пользователя на сообщение с клавиатурой
    return SECOND

def second_step(update, context):
    # показываем пользователю сообщение с результатом выбора второго шага и убираем клавиатуру
    update.message.reply_text(f'Вы выбрали {update.message.text}.',
                              reply_markup=ReplyKeyboardRemove())

    # переводим бота в режим ожидания нового диалога или завершения текущего
    return start

def cancel(update, context):
    # показываем пользователю сообщение об отмене текущего диалога и убираем клавиатуру
    update.message.reply_text('Диалог отменен.', reply_markup=ReplyKeyboardRemove())

    # переводим бота в режим ожидания нового диалога или завершения текущего
    return ConversationHandler.END

def main():
    # создаем объект класса Updater и получаем токен бота
    updater = Updater(bot_token, use_context=True)

    # создаем обработчики команд и сообщений и добавляем их в Dispatcher
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            FIRST: [MessageHandler(Filters.regex('^Первый шаг$'), first_step)],
            SECOND: [MessageHandler(Filters.regex('^Второй шаг$'), second_step)]
        },
        fallbacks=[MessageHandler(Filters.regex('^Отмена$'), cancel)]
    )

    dispatcher.add_handler(conv_handler)

    # запускаем бота с бесконечным циклом работы
    updater.start_polling()
    #updater.idle()

if __name__ == '__main__':
    main()

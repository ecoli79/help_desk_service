import asyncio
import logging
import aiohttp
import os

from maxapi import Bot, Dispatcher, F
from maxapi.context import MemoryContext, State, StatesGroup
from maxapi.types import (
    BotStarted,
    Command,
    MessageCreated,
    CallbackButton,
    MessageCallback,
)
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from maxapi.enums.attachment import AttachmentType

import config
import db_working

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

botToken = config.get_config_data('max_bot')['token']

bot = Bot(botToken)
dp = Dispatcher()


class TicketForm(StatesGroup):
    waitingForType = State()
    waitingForDescription = State()


TEXT_FOR_DESCRIPTION = (
    'Если у вас есть картинка или фотография ошибки, прикрепите ее через скрепку.\n'
    'После этого опишите свою проблему как можно подробнее,\n'
    'например: Не печатает принтер в поликлинике № 3 каб 30 Телефон для связи 99999999'
)

TEXT_FOR_DESCRIPTION_AFTER_IMAGE = (
    'Теперь опишите свою проблему максимально подробно,\n'
    'например: Поликлиника Гашкова 41, каб. 13, не включается компьютер. '
    'Телефон для связи 99999999.'
)


def _getTicketTypes():
    return db_working.get_ticket_types_list()


def buildTicketTypeKeyboard():
    ticketTypes = _getTicketTypes()
    builder = InlineKeyboardBuilder()
    row = []
    for typeName in ticketTypes:
        row.append(CallbackButton(text=typeName, payload=typeName))
        if len(row) == 2:
            builder.row(*row)
            row = []
    if row:
        builder.row(*row)
    return builder.as_markup()


def cutLongTicketText(text):
    if len(text) > 38:
        text = text[:39] + '...'
    return text


async def downloadFile(url, savePath):
    downloadVariants = [
        {'Authorization': botToken},
        {'Authorization': f'Bearer {botToken}'},
        {},
    ]
    print(f'[DOWNLOAD] Trying URL: {url}')
    print(f'[DOWNLOAD] Save path: {savePath}')
    for idx, headers in enumerate(downloadVariants):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as resp:
                    print(f'[DOWNLOAD] Attempt {idx+1} status={resp.status} content-type={resp.content_type}')
                    if resp.status == 200:
                        fileBytes = await resp.read()
                        print(f'[DOWNLOAD] Got {len(fileBytes)} bytes')
                        if len(fileBytes) == 0:
                            continue
                        os.makedirs(os.path.dirname(savePath), exist_ok=True)
                        with open(savePath, 'wb') as f:
                            f.write(fileBytes)
                        print(f'[DOWNLOAD] SUCCESS saved to {savePath}')
                        return True
                    else:
                        body = await resp.text()
                        print(f'[DOWNLOAD] Attempt {idx+1} failed: {body[:300]}')
        except Exception as e:
            print(f'[DOWNLOAD] Attempt {idx+1} exception: {e}')
    print('[DOWNLOAD] ALL attempts failed')
    return False


def getAttachmentByType(attachments, *targetTypes):
    if not attachments:
        return None
    for att in attachments:
        if att.type in targetTypes:
            return att
    return None


class TicketData:
    def __init__(self, chatId, messageId, username, userFullname, ticketType, ticketText, imagePath, voicePath, maxMessageId=None):
        self.chatId = chatId
        self.messageId = messageId
        self.username = username
        self.userFullname = userFullname
        self.ticketType = ticketType
        self.ticketText = ticketText
        self.imagePath = imagePath
        self.voicePath = voicePath
        self.maxMessageId = maxMessageId

    def save(self):
        try:
            db_working.insert_ticket(
                self.username,
                self.userFullname,
                self.ticketType,
                self.ticketText,
                self.chatId,
                self.messageId,
                self.imagePath,
                self.voicePath,
                maxMessageId=self.maxMessageId,
            )
            return True
        except Exception as error:
            print(error)
            return False


@dp.bot_started()
async def botStarted(event: BotStarted):
    await event.bot.send_message(
        chat_id=event.chat_id,
        text='Создание новой заявки. Выберите тип заявки, которую Вы хотите создать',
        attachments=[buildTicketTypeKeyboard()],
    )


@dp.message_created(Command('start'))
async def startCommand(event: MessageCreated, context: MemoryContext):
    await context.clear()
    await context.set_state(TicketForm.waitingForType)
    await event.message.answer(
        text='Создание новой заявки. Выберите тип заявки, которую Вы хотите создать',
        attachments=[buildTicketTypeKeyboard()],
    )


@dp.message_callback()
async def ticketTypeSelected(event: MessageCallback, context: MemoryContext):
    ticketTypeName = event.callback.payload
    if ticketTypeName not in _getTicketTypes():
        return

    await context.set_state(TicketForm.waitingForDescription)
    await context.update_data(
        ticketType=ticketTypeName,
        imagePath='',
        voicePath='',
    )

    await event.message.answer(
        text=f'Вы выбрали тип заявки: *{ticketTypeName}*\n{TEXT_FOR_DESCRIPTION}',
        attachments=[buildTicketTypeKeyboard()],
    )


@dp.message_created(TicketForm.waitingForDescription)
async def handleDescriptionMessage(event: MessageCreated, context: MemoryContext):
    data = await context.get_data()
    ticketType = data.get('ticketType', '')
    messageAttachments = event.message.body.attachments or []
    messageText = event.message.body.text

    print(f'[HANDLER] waitingForDescription fired')
    print(f'[HANDLER] text={messageText!r}')
    print(f'[HANDLER] attachments count={len(messageAttachments)}')
    for att in messageAttachments:
        print(f'[HANDLER] att.type={att.type!r} att.__class__={att.__class__.__name__} payload={att.payload}')

    if not ticketType:
        await event.message.answer(
            text='Вы не выбрали тип заявки. Сначала нужно выбрать тип заявки.',
            attachments=[buildTicketTypeKeyboard()],
        )
        return

    chatId = event.message.recipient.chat_id
    maxMid = event.message.body.mid
    username = event.message.sender.username or event.message.sender.full_name
    userFullname = event.message.sender.full_name

    imagePath = data.get('imagePath', '')
    voicePath = data.get('voicePath', '')

    imageAtt = getAttachmentByType(messageAttachments, AttachmentType.IMAGE)
    fileAtt = getAttachmentByType(messageAttachments, AttachmentType.FILE)
    audioAtt = getAttachmentByType(messageAttachments, AttachmentType.AUDIO)

    if imageAtt or fileAtt:
        att = imageAtt or fileAtt
        print(f'[IMG] type={att.type} class={att.__class__.__name__} payload={att.payload}')
        attUrl = getattr(att.payload, 'url', None)
        attToken = getattr(att.payload, 'token', None)
        attFilename = getattr(att, 'filename', None)

        isImage = att.type == AttachmentType.IMAGE
        if not isImage and attFilename:
            isImage = attFilename.lower().rsplit('.', 1)[-1] in ('jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp')

        if not isImage and not attFilename:
            isImage = True

        if isImage and attUrl:
            fileExt = 'jpg'
            if attFilename and '.' in attFilename:
                fileExt = attFilename.rsplit('.', 1)[-1]
            elif att.type == AttachmentType.IMAGE:
                fileExt = 'jpg'
            fileName = f'{maxMid}.{fileExt}'
            savePath = f'./static/img/{fileName}'

            downloaded = await downloadFile(attUrl, savePath)
            if not downloaded and attToken:
                urlWithToken = f'{attUrl}{"&" if "?" in attUrl else "?"}token={attToken}'
                downloaded = await downloadFile(urlWithToken, savePath)

            if downloaded:
                imagePath = fileName
                await context.update_data(imagePath=imagePath)
                print(f'[IMG] Saved as {fileName}')
            else:
                await event.message.answer(
                    text='Не удалось загрузить картинку. Попробуйте еще раз.',
                    attachments=[buildTicketTypeKeyboard()],
                )
                return
        else:
            await event.message.answer(
                text='Вы приложили НЕ картинку. Попробуйте еще раз.',
                attachments=[buildTicketTypeKeyboard()],
            )
            return

        if messageText:
            shortText = cutLongTicketText(messageText)
            ticket = TicketData(
                chatId=chatId, messageId=0, username=username,
                userFullname=userFullname, ticketType=ticketType,
                ticketText=messageText, imagePath=imagePath, voicePath=voicePath,
                maxMessageId=maxMid,
            )
            ticket.save()
            await context.clear()
            await context.set_state(TicketForm.waitingForType)
            await event.message.answer(
                text=f'Ваша заявка: *{shortText}* принята',
                attachments=[buildTicketTypeKeyboard()],
            )
        else:
            await event.message.answer(
                text=f'Картинка загружена.\n{TEXT_FOR_DESCRIPTION_AFTER_IMAGE}',
                attachments=[buildTicketTypeKeyboard()],
            )
        return

    if audioAtt:
        print(f'[AUDIO] payload={audioAtt.payload}')
        audioUrl = getattr(audioAtt.payload, 'url', None)
        audioToken = getattr(audioAtt.payload, 'token', None)

        if audioUrl:
            fileName = f'{maxMid}.wav'
            savePath = f'./static/audio/{fileName}'
            downloaded = await downloadFile(audioUrl, savePath)
            if not downloaded and audioToken:
                urlWithToken = f'{audioUrl}{"&" if "?" in audioUrl else "?"}token={audioToken}'
                downloaded = await downloadFile(urlWithToken, savePath)

            if downloaded:
                ticketText = messageText or 'Описание проблемы в голосовом сообщении. Смотри вложение в заявке.'
                ticket = TicketData(
                    chatId=chatId, messageId=0, username=username,
                    userFullname=userFullname, ticketType=ticketType,
                    ticketText=ticketText, imagePath=imagePath, voicePath=fileName,
                    maxMessageId=maxMid,
                )
                ticket.save()
                await context.clear()
                await context.set_state(TicketForm.waitingForType)
                await event.message.answer(
                    text='Голосовое сообщение загружено. Ваша заявка принята в работу.',
                    attachments=[buildTicketTypeKeyboard()],
                )
            else:
                await event.message.answer(
                    text='Не удалось загрузить голосовое сообщение. Попробуйте еще раз.',
                    attachments=[buildTicketTypeKeyboard()],
                )
            return

    if messageText:
        shortText = cutLongTicketText(messageText)
        ticket = TicketData(
            chatId=chatId, messageId=0, username=username,
            userFullname=userFullname, ticketType=ticketType,
            ticketText=messageText, imagePath=imagePath, voicePath=voicePath,
            maxMessageId=maxMid,
        )
        ticket.save()
        await context.clear()
        await context.set_state(TicketForm.waitingForType)
        await event.message.answer(
            text=f'Ваша заявка: *{shortText}* принята',
            attachments=[buildTicketTypeKeyboard()],
        )
        return

    await event.message.answer(
        text='Отправьте текст описания проблемы, картинку или голосовое сообщение.',
        attachments=[buildTicketTypeKeyboard()],
    )


@dp.message_created()
async def handleUnexpectedMessage(event: MessageCreated, context: MemoryContext):
    currentState = await context.get_state()
    if currentState is None or currentState == str(TicketForm.waitingForType):
        await event.message.answer(
            text='Вы не выбрали тип заявки. Сначала нужно выбрать тип заявки.',
            attachments=[buildTicketTypeKeyboard()],
        )


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())

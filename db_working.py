import logging
from contextlib import contextmanager
from datetime import datetime

import psycopg2

import config

logger = logging.getLogger(__name__)


@contextmanager
def db_cursor():
    """Context manager providing a database cursor with auto-commit and rollback on error."""
    conn = psycopg2.connect(**config.get_config_data('postgresql'))
    cur = conn.cursor()
    try:
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def _get_or_create_user(cur, telegramUsername, telegramFullname=''):
    """Internal: get or create a telegram user using an existing cursor."""
    queryInsert = (
        'INSERT INTO users (telegram_username, telegram_fullname, date_insert, date_update) '
        'VALUES (%s, %s, %s, %s)'
    )
    queryGet = 'SELECT id, telegram_username, telegram_fullname FROM users WHERE telegram_username = %s'
    dateNow = datetime.now()

    if telegramUsername is None:
        telegramUsername = telegramFullname

    cur.execute(queryGet, (telegramUsername,))
    userDb = cur.fetchall()

    if not userDb:
        cur.execute(queryInsert, (telegramUsername, telegramFullname, dateNow, dateNow))
        cur.execute(queryGet, (telegramUsername,))
        userDb = cur.fetchall()

    return userDb


def _get_or_create_ticket_type(cur, typeName):
    """Internal: get or create a ticket type using an existing cursor."""
    queryInsert = 'INSERT INTO ticket_types (type_name, date_insert, date_update) VALUES (%s, %s, %s)'
    queryGet = 'SELECT id, type_name FROM ticket_types WHERE type_name = %s'
    dateNow = datetime.now()

    cur.execute(queryGet, (typeName,))
    ticketTypeDb = cur.fetchall()

    if not ticketTypeDb:
        cur.execute(queryInsert, (typeName, dateNow, dateNow))
        cur.execute(queryGet, (typeName,))
        ticketTypeDb = cur.fetchall()

    return ticketTypeDb


def _save_image(cur, imagePath, ticketId):
    """Internal: save an image path linked to a ticket."""
    queryInsert = (
        'INSERT INTO images (image_path, ticket_id, date_insert, date_update) '
        'VALUES (%s, %s, %s, %s)'
    )
    dateNow = datetime.now()
    cur.execute(queryInsert, (imagePath, ticketId, dateNow, dateNow))


def _save_audio(cur, audioPath, ticketId):
    """Internal: save an audio path linked to a ticket."""
    queryInsert = (
        'INSERT INTO voices (ticket_id, voice_path, date_insert, date_update) '
        'VALUES (%s, %s, %s, %s)'
    )
    dateNow = datetime.now()
    cur.execute(queryInsert, (ticketId, audioPath, dateNow, dateNow))


def get_insert_ticket_type(typeName):
    """Get ticket type by name, creating it if it doesn't exist.

    Args:
        typeName (str): name of ticket type

    Returns:
        list[tuple]: [(id, type_name)] or [] on error
    """
    try:
        with db_cursor() as cur:
            return _get_or_create_ticket_type(cur, typeName)
    except (Exception, psycopg2.Error):
        logger.exception('Failed to get/insert ticket type: %s', typeName)
        return []


def get_ticket_types():
    """Return all ticket type names from database.

    Returns:
        list[tuple]: [(type_name,), ...] or [] on error
    """
    try:
        with db_cursor() as cur:
            cur.execute('SELECT type_name FROM ticket_types')
            return cur.fetchall()
    except (Exception, psycopg2.Error):
        logger.exception('Failed to get ticket types')
        return []


def get_ticket_types_list():
    """Return flat list of ticket type names from database.

    Returns:
        list[str]: ['Подписание', 'Оборудование', ...] or [] on error
    """
    return [row[0] for row in get_ticket_types()]


def get_insert_user_telegram(telegramUsername, telegramFullname=''):
    """Get telegram user by username, creating if doesn't exist.

    Args:
        telegramUsername (str): nick in telegram
        telegramFullname (str): full name of user in telegram

    Returns:
        list[tuple]: [(id, telegram_username, telegram_fullname)] or [] on error
    """
    try:
        with db_cursor() as cur:
            return _get_or_create_user(cur, telegramUsername, telegramFullname)
    except (Exception, psycopg2.Error):
        logger.exception('Failed to get/insert telegram user: %s', telegramUsername)
        return []


def image_get_save(imagePath, ticketId):
    """Save or retrieve image path linked to a ticket.
    If imagePath is truthy, saves it. Otherwise retrieves existing images.

    Args:
        imagePath (str): path to image file on disk
        ticketId (int): id of the ticket

    Returns:
        list[tuple]: image records or [] on error
    """
    try:
        with db_cursor() as cur:
            if imagePath:
                _save_image(cur, imagePath, ticketId)
                return []
            else:
                cur.execute(
                    'SELECT image_path, ticket_id FROM images WHERE ticket_id = %s',
                    (ticketId,),
                )
                return cur.fetchall()
    except (Exception, psycopg2.Error):
        logger.exception('Failed to save/get image for ticket %s', ticketId)
        return []


def get_insert_audio(audioPath, ticketId):
    """Save or retrieve audio path linked to a ticket.
    If audioPath is truthy, saves it. Otherwise retrieves existing audio records.

    Args:
        audioPath (str): path to *.wav file on server
        ticketId (int): id of the linked ticket

    Returns:
        list[tuple]: audio records or [] on error
    """
    try:
        with db_cursor() as cur:
            if audioPath:
                _save_audio(cur, audioPath, ticketId)
                return []
            else:
                cur.execute(
                    'SELECT voice_path, ticket_id FROM voices WHERE ticket_id = %s',
                    (ticketId,),
                )
                return cur.fetchall()
    except (Exception, psycopg2.Error):
        logger.exception('Failed to save/get audio for ticket %s', ticketId)
        return []


def insert_ticket(telegramUsername, telegramFullname, ticketTypeName, ticketText,
                  telegramChatid, telegramMessageId, imagePath, voicePath, maxMessageId=None):
    """Insert a new ticket with related user, type, image, and audio in a single transaction.

    Args:
        telegramUsername (str): username in telegram
        telegramFullname (str): full name of user in telegram
        ticketTypeName (str): ticket type name (created if not exists)
        ticketText (str): text of the ticket
        telegramChatid (str): id of the chat in telegram bot
        telegramMessageId (int): message id from telegram
        imagePath (str): path to image on disk
        voicePath (str): path to voice file on disk
        maxMessageId (str, optional): message id from MAX messenger for reply quotes

    Returns:
        tuple|list: (ticket_id,) or [] on error
    """
    queryInsert = (
        'INSERT INTO tickets '
        '(user_id_created, ticket_type_id, ticket_text, telegram_chatid, telegram_message_id, '
        'date_insert, date_update, is_done, sended, max_message_id) '
        'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id'
    )

    if telegramUsername is None:
        telegramUsername = telegramFullname

    try:
        with db_cursor() as cur:
            userDb = _get_or_create_user(cur, telegramUsername, telegramFullname)
            ticketTypeDb = _get_or_create_ticket_type(cur, ticketTypeName)
            dateNow = datetime.now()

            cur.execute(queryInsert, (
                userDb[0][0], ticketTypeDb[0][0], ticketText,
                telegramChatid, telegramMessageId,
                dateNow, dateNow, False, False, maxMessageId,
            ))
            ticket = cur.fetchone()

            if imagePath:
                _save_image(cur, imagePath, ticket[0])
            if voicePath:
                _save_audio(cur, voicePath, ticket[0])

            return ticket
    except (Exception, psycopg2.Error):
        logger.exception('Failed to insert ticket')
        return []


def update_ticket(ticketId, employeeId=None, textResponse='', note='', isDone=False, sended=False):
    """Update ticket fields: response, note, status, or mark as sent.

    Args:
        ticketId (int): id of the ticket
        employeeId (int, optional): id of the employee
        textResponse (str): text response for the user
        note (str): internal note for the ticket
        isDone (bool): True to close the ticket
        sended (bool): True to mark the response as sent
    """
    queryUpdate = (
        'UPDATE tickets '
        'SET employee_id = %s, text_response = %s, note = %s, is_done = %s, date_update = %s '
        'WHERE id = %s'
    )
    queryCloseWork = 'UPDATE tickets SET is_working = False WHERE id = %s'
    queryMarkSended = 'UPDATE tickets SET sended = %s WHERE id = %s'

    try:
        with db_cursor() as cur:
            if isDone:
                cur.execute(queryCloseWork, (ticketId,))

            if sended:
                cur.execute(queryMarkSended, (sended, ticketId))
            else:
                dateNow = datetime.now()
                cur.execute(queryUpdate, (
                    employeeId, textResponse, note, isDone, dateNow, ticketId,
                ))
    except (Exception, psycopg2.Error):
        logger.exception('Failed to update ticket %s', ticketId)


def ticket_in_work(ticketId, employeeId, isWork):
    """Mark a ticket as being worked on by an employee.

    Args:
        ticketId (int): id of the ticket
        employeeId (int): id of the employee
        isWork (bool): True if ticket is being worked on
    """
    queryUpdate = (
        'UPDATE tickets '
        'SET employee_id = %s, date_update = %s, is_working = %s '
        'WHERE id = %s'
    )

    try:
        with db_cursor() as cur:
            dateNow = datetime.now()
            cur.execute(queryUpdate, (employeeId, dateNow, isWork, ticketId))
    except (Exception, psycopg2.Error):
        logger.exception('Failed to set ticket %s in work', ticketId)


def get_ticket(ticketId):
    """Get detailed information about a ticket by ID.

    Args:
        ticketId (int): id of the ticket

    Returns:
        list[tuple]: ticket details or [] on error
    """
    queryGet = (
        'SELECT '
        '  t.id, '
        '  u.telegram_username, u.telegram_fullname, '
        '  tt.type_name, '
        '  t.ticket_text, t.text_response, t.note, t.is_done, t.sended, '
        '  e.lastname, e.firstname, e.position, '
        '  t.is_working, '
        '  t.date_insert, t.date_update, '
        '  i.image_path '
        'FROM tickets t '
        'LEFT JOIN users u ON t.user_id_created = u.id '
        'LEFT JOIN ticket_types tt ON t.ticket_type_id = tt.id '
        'LEFT JOIN employee e ON t.employee_id = e.id '
        'LEFT JOIN images i ON t.id = i.ticket_id '
        'WHERE t.id = %s'
    )

    try:
        with db_cursor() as cur:
            cur.execute(queryGet, (ticketId,))
            return cur.fetchall()
    except (Exception, psycopg2.Error):
        logger.exception('Failed to get ticket %s', ticketId)
        return []


def get_tickets(isDone, ticketTypeName='', startDate=None, endDate=None):
    """Get a filtered list of tickets ordered by date_insert DESC.

    Args:
        isDone (str): 'on' to include closed tickets, any other value to filter open only
        ticketTypeName (str, optional): filter by ticket type name
        startDate (str, optional): start date for date range filter
        endDate (str, optional): end date for date range filter

    Returns:
        list[tuple]: list of ticket tuples or [] on error
    """
    queryGet = (
        'SELECT '
        '  t.id, '
        '  u.telegram_username, u.telegram_fullname, '
        '  tt.type_name, '
        '  t.ticket_text, t.text_response, t.note, t.is_done, t.sended, t.is_working, '
        '  e.lastname, e.firstname, e.position, '
        '  t.date_insert, t.date_update '
        'FROM tickets t '
        'LEFT JOIN users u ON t.user_id_created = u.id '
        'LEFT JOIN ticket_types tt ON t.ticket_type_id = tt.id '
        'LEFT JOIN employee e ON t.employee_id = e.id '
        'LEFT JOIN images i ON t.id = i.ticket_id '
        'WHERE 1=1'
    )
    params = []

    if ticketTypeName and ticketTypeName != 'None':
        queryGet += ' AND tt.type_name LIKE %s'
        params.append(f'%{ticketTypeName}%')

    if isDone != 'on':
        queryGet += ' AND t.is_done = %s'
        params.append(False)

    queryGet += ' ORDER BY t.date_insert DESC'

    try:
        with db_cursor() as cur:
            cur.execute(queryGet, tuple(params))
            return cur.fetchall()
    except (Exception, psycopg2.Error):
        logger.exception('Failed to get tickets')
        return []


def get_tickets_for_send():
    """Get closed tickets with unsent responses for Telegram bot.

    Returns:
        list[tuple]: [(id, telegram_chatid, text_response, telegram_message_id), ...] or [] on error
    """
    queryGet = (
        'SELECT t.id, t.telegram_chatid, t.text_response, t.telegram_message_id '
        'FROM tickets t '
        'WHERE is_done = true AND sended = false AND telegram_message_id != 0'
    )

    try:
        with db_cursor() as cur:
            cur.execute(queryGet)
            return cur.fetchall()
    except (Exception, psycopg2.Error):
        logger.exception('Failed to get tickets for sending')
        return []


def get_tickets_for_send_max():
    """Get closed tickets created by MAX bot for sending response back via MAX messenger.

    Returns:
        list[tuple]: [(id, telegram_chatid, text_response, max_message_id), ...] or [] on error
    """
    queryGet = (
        'SELECT t.id, t.telegram_chatid, t.text_response, t.max_message_id '
        'FROM tickets t '
        'WHERE is_done = true AND sended = false AND telegram_message_id = 0'
    )

    try:
        with db_cursor() as cur:
            cur.execute(queryGet)
            return cur.fetchall()
    except (Exception, psycopg2.Error):
        logger.exception('Failed to get MAX tickets for sending')
        return []

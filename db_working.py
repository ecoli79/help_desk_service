from datetime import date, datetime
import psycopg2
from configparser import ConfigParser
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData
from sqlalchemy import select

# local module
import config


def get_connection() -> psycopg2.connect: 
    conn = None
    try:
        params = config.get_config_data('postgresql')
        conn = psycopg2.connect(**params)
        return conn
    
    except (Exception, psycopg2.DatabaseError) as error:
        return error




def get_insert_ticket_type(type_name):
    """This method get name of ticket_type and check exist it in database or not, if not exist insert new row database if exist 
    get item from database

    Args:
        ticket_type_name (str): name of ticket_type
    """
    
    query_insert = "INSERT INTO ticket_types (type_name, date_insert, date_update) VALUES (%s, %s, %s)"
    query_get = """ SELECT id, type_name FROM ticket_types WHERE type_name = %s """
    ticket_type_db = []
    date_update = datetime.now()
    
    try:
        conn = get_connection()
        
        cur = conn.cursor()
        
        cur.execute(query_get, (type_name,))
        ticket_type_db = cur.fetchall()
        
        if not ticket_type_db:
            cur.execute(query_insert, (type_name, date_update, date_update))
            conn.commit()
            cur.execute(query_get, (type_name,))
            ticket_type_db = cur.fetchall()
        
    except (Exception, psycopg2.Error) as error:
        print(error)
    
    finally:
        
        if conn:
            cur.close()
            conn.close()
            
            return ticket_type_db        


def get_ticket_types():
    """This method return all ticket type names in database

    Returns:
         list[(str)] list of tuple   
    """
    
    query_get = "select type_name from ticket_types"
    ticket_types = []
    
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(query_get,)
        ticket_types = cur.fetchall()
               

    except (Exception, psycopg2.Error) as error:
        print(error)
    
    finally:
        conn.close()
        cur.close()
        return ticket_types


def get_insert_user_telegram(telegram_username, telegram_fullname=""):
    """This method get name of telegram_user and check exist it in database or not, if not exist insert new row database if exist 
    get item from database

    Args:
        telegram_username (str): nick in telegram
        telegram_firstname (str): lastname of user in telegram
        telegram_lastname (str): lastname of user in telegram
    """
    
    query_insert = "INSERT INTO users (telegram_username, telegram_fullname, date_insert, date_update) VALUES (%s, %s, %s, %s)"
    query_get = """ SELECT id, telegram_username, telegram_fullname FROM users WHERE telegram_username = %s """
    user_db = []
    date_update = datetime.now()
    
    if telegram_username is None:
        telegram_username = telegram_fullname
    
    try:
        conn = get_connection()
        
        cur = conn.cursor()
        
        cur.execute(query_get, (telegram_username,))
        user_db = cur.fetchall()
        
        if not user_db:
            cur.execute(query_insert, (telegram_username, telegram_fullname,date_update, date_update))
            conn.commit()
            cur.execute(query_get, (telegram_username,))
            user_db = cur.fetchall()
        
    except (Exception, psycopg2.Error) as error:
        print(error)
    
    finally:
        
        if conn:
            cur.close()
            conn.close()
            
            return user_db     
        
        
def image_get_save(image_path, ticket_id):
    """This method save in database path to image/images connection with ticket
    if image_path == '' method only return image_path

    Args:
        image_path (str): path in disk for image
        ticket_id (int): id ticket
    """
    
    query_insert = "INSERT INTO images (image_path, ticket_id, date_insert, date_update) VALUES (%s, %s, %s, %s)"
    query_get = "SELECT image_path, ticket_id FROM images WHERE ticket_id = %s"
    image_db = []
    date_update = datetime.now()
    
    try:
        
        conn = get_connection()
        
        cur = conn.cursor()
        
        if image_path:
            cur.execute(query_insert, (image_path, ticket_id, date_update, date_update))
            conn.commit()
        else:
            cur.execute(query_get, (ticket_id,))
            image_db = cur.fetchall()
            
        
    except (Exception, psycopg2.Error) as error:
        print(error)
    
    finally:
        
        if conn:
            cur.close()
            conn.close()
            
            return image_db   


def get_insert_audio(audio_path, ticket_id):
    """This method save in database path to voice message linked with ticke
    if audio_path == '' method return path to file

    Args:
        audio_path (str): path to file *.wav on server
        ticket_id (int): ticke_id linked ticket
    """
    
    query_get = "SELECT voice_path, ticke_id FROM voices WHERE ticket_id = %s"
    query_insert = "INSERT into voices(ticket_id, voice_path, date_insert, date_update) VALUES (%s, %s, %s, %s)" 
    voice_db = []
    data_update = datetime.now()
    
    try:
        
        conn = get_connection()
        
        cur = conn.cursor()
        
        if audio_path:
            cur.execute(query_insert, (ticket_id, audio_path, data_update, data_update,))
            conn.commit()
        else:
            cur.execute(query_get, (ticket_id, ))
            voice_db = cur.fetchall()
    except (Exception, psycopg2.Error) as error:
        print(error)
        
    finally:
        if conn:
            cur.close()
            conn.close()
            
            return voice_db
    

def insert_ticket(telegram_username, telegram_fullname, ticket_type_name, ticket_text, telegram_chatid, telegram_message_id, image_path, voice_path):
    """This method insert new ticket in database.
    Inside method create new item for images by image_path.
    If telegram_username not exist in database, will create it as new item.

    Args:
        telegram_username (str): username in telegram
        ticket_type_name (str): ticke_type_name, if that type_name not exist, will create it in new item in database
        ticket_text (str): text of the ticket
        telegram_chatid (str): id of a chat in telegram bot
        image_path (str): path to image in disk
    """
    
    query_insert = """INSERT INTO tickets (user_id_created, ticket_type_id, ticket_text, telegram_chatid, telegram_message_id, date_insert, date_update, is_done, sended)
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;"""
    
    if telegram_username is None:
        telegram_username = telegram_fullname
    
    user_created_db = get_insert_user_telegram(telegram_username, telegram_fullname)
    ticket_type_db = get_insert_ticket_type(ticket_type_name)
    date_update = datetime.now()
    ticket = []
    
    try:
        
        conn = get_connection()
        
        cur = conn.cursor()
        cur.execute(query_insert, (user_created_db[0][0], ticket_type_db[0][0], ticket_text, telegram_chatid, telegram_message_id, date_update, date_update, False, False))
        conn.commit()
        ticket = cur.fetchone()
        
        
        if image_path:
            image_get_save(image_path, ticket[0])
        if voice_path:
            get_insert_audio(voice_path, ticket[0])        
        
    except (Exception, psycopg2.Error) as error:
        print(error)
    
    finally:
        
        if conn:
            cur.close()
            conn.close()
            
            return ticket   

        
def update_ticket(ticket_id, employee_id = None, text_response='', note='', is_done = False, sended = False):
    """This method is get ticket in database and give it to employee for editing. After, the ticket save to database with new data

    Args:
        ticket_id (int): id of ticket
        employee_id (id): id of employee
        text_response (str): text for anwer for user in ticket
        note (str): note for ticket
        is_done (bool, optional): It's param for close a ticket is True ticket is close, if False - ticket is open  Defaults to False.
        sended (bool, optional): It's param for check sended answer for ticket.If it True is that answer did sent or otherwise.  Defaults to False.
    """
    
    query_update = """UPDATE tickets
                   set employee_id = %s, text_response = %s, note = %s, is_done = %s, date_update = %s where id = %s 
                   """
    
    query_close_work = """
                    update tickets 
                    set is_working = False  
                    where id = %s
                   """

    query_update_after_sended = "UPDATE tickets set sended = %s WHERE id = %s"
    
    date_update = datetime.now()
    ticket = []
    
    try:
        conn = get_connection()
        
        cur = conn.cursor()
        
        # close working if close ticket
        if is_done:
            cur.execute(query_close_work, (ticket_id,))
            conn.commit()


        if sended:
            cur.execute(query_update_after_sended, (sended, ticket_id))
            conn.commit()
            
        else:    
            cur.execute(query_update, (employee_id, text_response, note, is_done, date_update, ticket_id, ))
            conn.commit()

    except (Exception, psycopg2.Error) as error:
        return error
    finally:
        if conn:
            cur.close()
            conn.close()


def ticket_in_work(ticket_id, emploeey_id, is_work):
    '''
    This method insert fiture is_working for ticket and insert employe who it get in work
    '''

    query_update = """UPDATE tickets
                   set employee_id = %s, date_update = %s, is_working = %s where id = %s 
                   """
    
    date_update = datetime.now()

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(query_update, (emploeey_id, date_update, is_work, ticket_id))
        conn.commit()
    
    except (Exception, psycopg2.Error) as error:
        return error
    
    finally:
        cur.close()
        conn.close()


def get_ticket(ticket_id):
    """This method get detail about ticket

    Args:
        ticket_id (int): id ticket
    """
    
    query_get = """select 
                    t.id,
                    u.telegram_username, u.telegram_fullname,
                    tt.type_name,
                    t.ticket_text, t.text_response, t.note, t.is_done, t.sended,
                    e.lastname, e.firstname, e.position,
                    t.is_working,
                    t.date_insert, t.date_update,
                    i.image_path
                    from tickets t 
                    left join users u on t.user_id_created = u.id 
                    left join ticket_types tt on t.ticket_type_id = tt.id 
                    left join employee e on t.employee_id = e.id 
                    left join images i on t.id = i.ticket_id
                    Where t.id = %s
                """
    ticket = []
    
    try:
        
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(query_get, (ticket_id, ))
        ticket = cur.fetchall()
    
    except (Exception, psycopg2.Error) as error:
        return error
    
    finally:
        if conn:
            cur.close()
            conn.close()
            
            return ticket
        
            
def get_tickets(is_done, ticket_type_name = '',start_date = None, end_date = None):
    """This method get a list of tickts by any parameters. Return list of tuples tickets order by date_insert DESC

    Args:
        ticket_type_name (str, optional): Tycket_type_name Defaults to None.
        start_date (str, optional): Start date for search by date interval create . Defaults to None.
        end_date (str, optional): End date for search by date interval create. Defaults to None.
        employee_id (int, optional): id employee who answer for ticket. Defaults to None.
        telegram_user (str, optional): username telegram who created a ticket. Defaults to None.
    """
    
    query_get = """ select 
                    t.id,
                    u.telegram_username, u.telegram_fullname,
                    tt.type_name,
                    t.ticket_text, t.text_response, t.note, t.is_done, t.sended, t.is_working,
                    e.lastname, e.firstname, e.position,
                    t.date_insert, t.date_update 
                    from tickets t 
                    left join users u on t.user_id_created = u.id 
                    left join ticket_types tt on t.ticket_type_id = tt.id 
                    left join employee e on t.employee_id = e.id 
                    left join images i on t.id = i.ticket_id
                    WHERE 1=1   
                """    
    tickets = []
    
    
    
    if ticket_type_name and ticket_type_name != 'None':
        query_get += f" AND tt.type_name like '%%{ticket_type_name}%%' "
    
    if is_done != 'on':
        query_get += f" AND t.is_done = {False}"
    
        
    query_get += ' order by t.date_insert DESC'
           
    try:
        
        conn = get_connection()
        
        cur = conn.cursor()
        cur.execute(query_get, ())
        tickets = cur.fetchall()

    
    except (Exception, psycopg2.Error) as error:
        return error
    
    finally:
        if conn:
            conn.close()
            cur.close()
            
            return tickets


def get_tickets_for_send():
    """This method get list of tickets for send it to telegram bot.
       Get ticket with option is_done = True and sended is False
    """
    query_get = """select t.id, t.telegram_chatid, t.text_response, t.telegram_message_id from tickets t  
                   where is_done = true and sended = false """
                   
    tickets = []
    
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(query_get, ())
        tickets = cur.fetchall()
        
    except (Exception, psycopg2.Error) as error:
        return(error)
    
    finally:
        if conn:
            conn.close()
            cur.close()
            
        return tickets


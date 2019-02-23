import MySQLdb
from functools import reduce

SUCCESS = 's'
NOT_FOUND = 'nf'
ALREADY_EXIST = 'ae'
ERROR = False
connection = None
c = None

def __init__(host, user, passwd, db):
    global connection
    global c
    connection = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db,charset='utf8' )
    c = connection.cursor()
    c.execute('SET NAMES utf8')
    c.execute('SET CHARACTER SET utf8')
    c.execute('SET character_set_connection=utf8')
    

def setup():
    sql_chats = 'CREATE TABLE IF NOT EXISTS chats (' \
                               'message_id INTEGER,' \
                'user_id INTEGER,' \
                'chat_id BIGINT,' \
                'text TEXT,' \
                'time DATETIME,' \
                'edited BOOLEAN DEFAULT 0' \
                                ')'
    connection.query(sql_chats)
    connection.commit()


def log_message(message_id, text, chat_id, user_id, time, edited=False):
    c.execute('INSERT INTO chats (message_id,text,chat_id,user_id,time,edited) VALUES (%s,%s,%s,%s,%s,%s)',
                       (message_id, text, chat_id, user_id, time, edited))
    connection.commit()

def search_duplicate(keywords, chat_id):
    c.execute('select count(text) from chats where text=%s and chat_id=%s', (keywords,chat_id))
    cursor=c.fetchone()
    print(cursor)
    if cursor[0]:
        print('in the if')
        c.execute('select * from chats where text="'+ keywords +'"')
        cursor = c.fetchone()
        return cursor
    return None


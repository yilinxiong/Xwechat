import sqlite3
import time
from contextlib import closing

from _messages import _Message


# =================================
# Store messages
# =================================
class MessageDb(object):
    def __init__(self):
        self.begin = False
        self.report_queries = []
        self.fields = ['user', 'text', 'timestamp']
        self.column_list = ','.join(self.fields)
        self.holder_list = ','.join(':%s' % var for var in self.fields)
        self.conn = sqlite3.connect(':memory:')
        self.init_db()

    def process(self, records):
        self.begin = time.time()
        insert = 'insert into messages (%s) values (%s)' % (self.column_list, self.holder_list)
        with closing(self.conn.cursor()) as cursor:
            for r in records:
                if isinstance(r, _Message):
                    cursor.execute(insert, (r.user, r.text, r.timestamp))

    def search_all(self):
        with closing(self.conn.cursor()) as cursor:
            cursor.execute('select text from messages order by timestamp')
            return [message[0] for message in cursor.fetchall()]

    def search_chats(self):
        with closing(self.conn.cursor()) as cursor:
            cursor.execute('select distinct user from messages order by timestamp desc')
            return [message[0] for message in cursor.fetchall()]

    def search_user_msg(self, user):
        with closing(self.conn.cursor()) as cursor:
            cursor.execute('select text from messages where user = \'%s\' order by timestamp' % user)
            return [message[0] for message in cursor.fetchall()]

    def init_db(self):
        create_table = 'create table messages (%s)' % self.column_list
        create_index = 'create index msg_user on messages (user)'
        with closing(self.conn.cursor()) as cursor:
            cursor.execute(create_table)
            cursor.execute(create_index)

    def close(self):
        self.conn.close()

import pymysql
from settings import *


class GlobomailRepository:

    def __init__(self):
        self.hostname = GLOBOMAIL_DB_HOST
        self.username = GLOBOMAIL_DB_USER
        self.password = GLOBOMAIL_DB_PASSWORD
        self.database = GLOBOMAIL_DB_NAME
        self.connection = pymysql.connect(host=self.hostname, user=self.username, password=self.password,
                                          database=self.database, charset='utf8mb4', connect_timeout=int(DATABASE_CONNECTION_TIMEOUT),
                                          cursorclass=pymysql.cursors.DictCursor)

    def call_function(self, email):
        try:
            self.cursor = self.connection.cursor()
            self.cursor.execute(f"SELECT globomail.fn_get_user_quota('{email}') as quota")
            return self.cursor.fetchone()

        except Exception as e:
            raise e
        finally:
            self.cursor.close()

    def close_connections(self):
        self.connection.close()

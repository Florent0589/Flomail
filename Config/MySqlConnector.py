import mysql.connector
import time


class MySqlConnector:

    def __init__(self, username, password, host, database):

        self.username = username
        self.password = password
        self.host = host
        self.database = database
        self.connection = None

    def connect(self):
        self.connection = mysql.connector.connect(user=self.username,
                                                  password=self.password,
                                                  host=self.host,
                                                  database=self.database,
                                                  connection_timeout=3600,
                                                  charset='utf8',
                                                  use_unicode=True)

        cursor = self.connection.cursor()
        self.connection.commit()

    def select_data(self, qry, qry_values=()):
        cursor = None
        try:
            self.connect()
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(qry, qry_values)
            cursor_results = cursor.fetchall()
            # Remove query caching
            self.connection.commit()
            return cursor_results

        except Exception as ex:
            # if connection is down, try reconnect
            if type(ex) is mysql.connector.OperationalError or type(ex) is mysql.connector.InterfaceError:
                while True:
                    try:
                        self.connect()
                        cursor = self.connection.cursor(dictionary=True)
                        cursor.execute(qry, qry_values)
                        cursor_results = cursor.fetchall()
                        self.connection.commit()
                        return cursor_results

                    except Exception as ex2:
                        print('trying to reconnect ............')
                        time.sleep(5)
                        continue
            # Just raise an error for other error types
            else:
                raise ex

        finally:
            if cursor is not None:
                cursor.close()

    def insert_data(self, qry, qry_values=()):
        cursor = None
        try:
            self.connect()
            cursor = self.connection.cursor()
            cursor.execute(qry, qry_values)
            self.connection.commit()
            return cursor.lastrowid

        except Exception as ex:
            # if connection is down, try reconnect
            if type(ex) is mysql.connector.OperationalError or type(ex) is mysql.connector.InterfaceError:
                while True:
                    try:

                        self.connect()
                        cursor = self.connection.cursor()
                        cursor.execute(qry, qry_values)
                        self.connection.commit()
                        return cursor.lastrowid
                    except Exception as ex2:
                        print('trying to reconnect ............')
                        time.sleep(5)
                        continue
            # Just raise an error for other error types
            else:
                raise ex

        finally:
            if cursor is not None:
                cursor.close()
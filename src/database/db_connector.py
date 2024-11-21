import mysql.connector
from mysql.connector import Error
from config.db_config import DB_CONFIG

class DBConnector:
    def __init__(self, host, database, user, password):
        self.host = DB_CONFIG['host']
        self.database = DB_CONFIG['database']
        self.user = DB_CONFIG['user']
        self.password = DB_CONFIG['password']
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            if self.connection.is_connected():
                print("Connection to the database established successfully")
                return self.connection  # Return the connection object
        except Error as e:
            print(f"Error while connecting to MySQL: {e}")
            return None  # Return None if connection fails

    def close(self):
        if self.connection.is_connected():
            self.connection.close()
            print("Database connection closed")
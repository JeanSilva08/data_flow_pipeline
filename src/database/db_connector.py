import mysql.connector
from mysql.connector import Error
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DBConnector:
    def __init__(self, host, database, user, password):
        """
        Initialize the DBConnector with database credentials.
        """
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.connection = None

    def connect(self):
        """
        Establish a connection to the MySQL database.
        Returns the connection object if successful, otherwise None.
        """
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            if self.connection.is_connected():
                logger.info("Connection to the database established successfully.")
                return self.connection
        except Error as e:
            logger.error(f"Error while connecting to MySQL: {e}")
            return None

    def is_connected(self):
        """
        Check if the database connection is active.
        """
        return self.connection and self.connection.is_connected()

    def close(self):
        """
        Close the database connection if it is open.
        """
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("Database connection closed.")

    def execute_query(self, query, params=None):
        """
        Execute a SQL query and return the result.
        """
        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            self.connection.commit()
            logger.info(f"Query executed successfully: {query}")
            return cursor
        except Error as e:
            logger.error(f"Error executing query: {query}. Error: {e}")
            if self.connection:
                self.connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()

    def fetch_one(self, query, params=None):
        """
        Fetch a single row from the database.
        """
        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            result = cursor.fetchone()
            logger.info(f"Fetched one row: {result}")
            return result
        except Error as e:
            logger.error(f"Error fetching one row: {e}")
            raise
        finally:
            if cursor:
                cursor.close()

    def fetch_all(self, query, params=None):
        """
        Fetch all rows from the database.
        """
        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            result = cursor.fetchall()
            logger.info(f"Fetched all rows: {result}")
            return result
        except Error as e:
            logger.error(f"Error fetching all rows: {e}")
            raise
        finally:
            if cursor:
                cursor.close()

    def insert(self, table, data):
        """
        Insert a row into the specified table.
        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        self.execute_query(query, tuple(data.values()))

    def update(self, table, data, condition):
        """
        Update rows in the specified table based on a condition.
        """
        set_clause = ', '.join([f"{key} = %s" for key in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {condition}"
        self.execute_query(query, tuple(data.values()))

    def delete(self, table, condition):
        """
        Delete rows from the specified table based on a condition.
        """
        query = f"DELETE FROM {table} WHERE {condition}"
        self.execute_query(query)
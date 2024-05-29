"""
Required packages for the application.

This file contains all utilities funtions for routers of the application.

Attributes:
    - client (MongoClient): The client for the MongoDB database.
    - db (Database): The database for the MongoDB database.
    - USERS (Collection): The collection for the users in the MongoDB database.
    - salt (str): The salt used for hashing passwords.
    - SECRET_KEY (str): The secret key used for generating tokens.
    - ALGORITHM (str): The algorithm used for generating tokens.
    - SMTP_user (str): The email address used for sending emails.
    - SMTP_password (str): The password used for sending emails.
"""
import psycopg2
from decouple import config

DB_USER = config("DB_USER")
DB_PASSWORD = config("DB_PASSWORD")
DB_HOST = config("DB_HOST")
DB_PORT = config("DB_PORT")
DB_NAME = config("DB_NAME")


class PostgresDatabase:
    """
    Posgress database class
    """

    connection: psycopg2.extensions.connection
    cursor: psycopg2.extensions.cursor

    def __init__(self):
        """
        initialize the class method
        """

        with psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
        ) as self.connection:
            self.cursor = self.connection.cursor()

    def execute(self, query, params=None):
        """
        Execute query method
        Attrs:
            query (str): query to execute
            params (str): query parameters
        """
        if params is None:
            self.cursor.execute(query)
        else:
            self.cursor.execute(query, params)

    def fetch_one(self):
        """
        fetch one method
        """
        return self.cursor.fetchone()

    def fetch_all(self):
        """
        fetch all method
        """
        return self.cursor.fetchall()

    def commit(self):
        """
        commit the transaction method
        """
        self.connection.commit()

    def rollback(self):
        """
        rollback the transaction method
        """
        self.connection.rollback()

    def close(self):
        """
        close the connection
        """
        self.connection.close()


PostgresDB = PostgresDatabase()

SERVER_URL = config("SERVER_URL")

salt = config("salt")
SECRET_KEY = config("SECRET_KEY")
ALGORITHM = config("ALGORITHM")

FROM_EMAIL = config("FROM_EMAIL")
SMTP_SERVER = config("SMTP_SERVER")
SMTP_PORT = config("SMTP_PORT")
SMTP_USERNAME = config("SMTP_USERNAME")
SMTP_PASSWORD = config("SMTP_PASSWORD")

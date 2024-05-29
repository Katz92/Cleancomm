"""
This file contains models relative to user
"""
from datetime import datetime, timedelta
from enum import Enum
import secrets
import string

from pydantic import BaseModel
import psycopg2
from psycopg2 import sql

import bcrypt
import jwt

from app.resources.required_packages import PostgresDB, SECRET_KEY, ALGORITHM, salt
from app.resources.type.status import Status
from app.resources.db_utils.user_queries import (USER_SELECT_QUERY, USER_INSERT_QUERY,
                                                 USER_UPDATE_QUERY, END_USER_SESSION_QUERY,
                                                 ACTIVE_USER_SESSION_QUERY,
                                                 IS_USER_SESSION_ACTIVE_QUERY)


class User(BaseModel):
    """
    Represents a user with email and password.

    Attributes:
        email (str): The email address of the user. This is used for user identification.
        password (str): The password of the user. Should be securely hashed
                        before storing in the database.
        host (str): add the host relative of user tonant
        firstName (str): The first name of the user.
        lastName (str): The last name of the user.
        status (Enum): The status of the user.
        token (str): The token of the user.
        session_active (int): 1 if the user is connected and 0 if not
    """

    email: str = ""
    password: str = ""
    host: str = ""
    first_name: str = ""
    last_name: str = ""
    lang: str = ""
    status: Enum = Status.DISABLED
    session_active: int = 0

    def setattr(self, **kwargs):
        """
        instanciate
        """
        if kwargs:
            kwargs.pop("id", None)
            kwargs.pop("email", None)
            kwargs.pop("created_date", None)
            kwargs.pop("updated_date", None)
            self.__dict__.update(**kwargs)

    def select(self):
        """
        Search for an user in database.

        Returns:
            user (dict): The user found. None if no user is found.
        """
        query = sql.SQL(USER_SELECT_QUERY)
        PostgresDB.execute(query, (self.email,))
        user_data = PostgresDB.fetch_one()

        if user_data is None:
            return None

        # Récupérez les noms de colonnes à partir de cursor.description
        column_names = [desc[0] for desc in PostgresDB.cursor.description]

        # Créez un dictionnaire en utilisant les noms de colonnes comme clés
        user_dict = {column_names[i]: user_data[i] for i in range(len(column_names))}
        self.host = user_dict.get("host")
        self.first_name = user_dict.get("first_name")
        self.last_name = user_dict.get("last_name")
        self.lang = user_dict.get("lang")
        self.status = Status(user_dict.get("status"))

        return user_dict

    def create(self):
        """
        Create the user in database.

        Attributes:
            first_name (str): The fist name of user
            last_name (str): The last name of user
            lang (str): The language of user

        Returns
            acknowledged (bool): True if the user is created, False otherwise.
        """
        query = sql.SQL(USER_INSERT_QUERY)
        hashed_password = bcrypt.hashpw(
            self.password.encode("utf-8"), salt.encode("utf-8")
        )
        self.status = Status.PENDING
        try:
            PostgresDB.execute(
                query,
                (
                    self.email,
                    str(hashed_password),
                    self.host,
                    self.first_name,
                    self.last_name,
                    self.lang,
                    datetime.utcnow(),
                    datetime.utcnow(),
                    self.status.value,
                ),
            )
            PostgresDB.commit()

            user_data = self.select()
            if not user_data:
                return None
            user_data.pop("password", None)
            user_data["created_date"] = str(user_data["created_date"])
            user_data["updated_date"] = str(user_data["updated_date"])
            user_data.pop("id", None)
            return user_data

        except psycopg2.IntegrityError as _e_:
            PostgresDB.rollback()
            if _e_.pgcode == psycopg2.errorcodes.UNIQUE_VIOLATION:
                data = {"message": "User exists"}
                return data
            raise

    def generate_token(self, email: str, expiration_time: timedelta = None):
        """
        Generate a token for the user.

        Attributes:
            - email (str): The email address of the user.
            - expiration_time (timedelta): The time before the token expires.

        Returns:
            token (str): The token of the user.
        """
        payload = {
            "sub": email,
            "status": self.status.value,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + expiration_time,
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    def authenticate_user(self):
        """
        Authenticate the user.

        Returns:
            token (str): The token of the user.
        """
        user = self.select()
        # Check if user exists and is active
        if user:
            if (
                not bcrypt.checkpw(
                    bytes(self.password, "utf-8"),
                    bytes(user["password"][2:-1], "utf-8"),
                )
            ) or user["status"] != Status.ACTIVE.value:
                return False

            # Set the user connected in database
            self.active_session()
            return {
                "email": user["email"],
                "host": user["host"],
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "lang": user["lang"],
                "created_date": str(user["created_date"]),
                "updated_date": str(user["updated_date"]),
                "status": user["status"],
                "access_token": self.generate_token(
                    user["email"], expiration_time=timedelta(days=1)
                ),
                "token_type": "Bearer",
            }
        return False

    def update(self, updated_user_data: dict):
        """
        Update a user.
        """
        updated_user_data["updated_date"] = datetime.utcnow()

        query = sql.SQL(USER_UPDATE_QUERY)
        if updated_user_data.get("status"):
            self.status = Status(updated_user_data["status"])
        self.setattr(**updated_user_data)
        if updated_user_data.get("password"):
            updated_user_data["password"] = str(
                bcrypt.hashpw(
                    updated_user_data["password"].encode("utf-8"), salt.encode("utf-8")
                )
            )
        user = self.select()

        PostgresDB.execute(
            query,
            (
                updated_user_data.get("host", user["host"]),
                updated_user_data.get("password", user["password"]),
                updated_user_data.get("first_name", user["first_name"]),
                updated_user_data.get("last_name", user["last_name"]),
                updated_user_data.get("lang", user["lang"]),
                updated_user_data.get("status", user["status"]),
                updated_user_data["updated_date"],
                self.email,
            ),
        )
        PostgresDB.commit()

        return self.select()

    def active_session(self):
        """
        Set a user connected in database by
        setting the column session_active to 1
        """
        query = sql.SQL(ACTIVE_USER_SESSION_QUERY)
        PostgresDB.execute(query, (1, self.email,))
        PostgresDB.commit()

    def end_session(self):
        """
        Set a user disconnected in database by
        setting the column session_active to 0
        """
        query = sql.SQL(END_USER_SESSION_QUERY)
        PostgresDB.execute(query, (0, self.email,))
        PostgresDB.commit()

    def is_session_active(self):
        """
        Return the session_active value
        """
        query = sql.SQL(IS_USER_SESSION_ACTIVE_QUERY)
        PostgresDB.execute(query, (self.email,))
        user_session_active = PostgresDB.fetch_one()
        return user_session_active[0]


def generate_password(length=20):
    """
    genarate random password
    """
    characters = string.ascii_letters + string.digits + string.punctuation
    password = "".join(secrets.choice(characters) for _ in range(length))
    return password

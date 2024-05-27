"""
Utilities function for users
"""
from psycopg2 import sql
from app.resources.db_utils.user_queries import GET_USER_BY_ID_QUERY
from app.resources.required_packages import PostgresDB
from app.resources.db_utils.db_utils import format_data_from_db


def get_user_by_id(user_id: int):
    """
    Function to get a user based on their id
    """
    query = sql.SQL(GET_USER_BY_ID_QUERY)
    PostgresDB.execute(query, (user_id,))
    data = PostgresDB.fetch_one()

    if data is None:
        return None

    return format_data_from_db(PostgresDB, data)

"""
Common utilities
"""
from app.resources.required_packages import PostgresDatabase


def format_data_from_db(postgres_db: PostgresDatabase, data):
    """
    Function to format a row from db
    using the column names from cursor. description
    """
    # Retrieve columns names from cursor.description
    column_names = [desc[0] for desc in postgres_db.cursor.description]

    # Create a new dict using columns names as keys
    formatted_data = {column_names[i]: data[i] for i in range(len(column_names))}

    return formatted_data


def format_datas_from_db(postgres_db: PostgresDatabase, datas):
    """
    Function to format rows from db
    using the column names from cursor. description
    """
    # Retrieve columns names from cursor.description
    column_names = [desc[0] for desc in postgres_db.cursor.description]
    formatted_datas = []
    # Create a new dict using columns names as keys
    for data in datas:
        formatted_data = {column_names[i]: data[i] for i in range(len(column_names))}
        formatted_datas.append(formatted_data)

    return formatted_datas

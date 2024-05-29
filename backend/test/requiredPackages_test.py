"""
Test required_packages.py
"""
import pytest


@pytest.fixture
def mock_postgres_db(mocker):
    """mock"""
    from app.resources.required_packages import PostgresDatabase
    db = mocker.patch("app.resources.required_packages.PostgresDatabase", new_calable=PostgresDatabase())

    mock_connection = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    db.connection = mock_connection
    db.cursor = mocker.MagicMock()
    db.execute = mocker.MagicMock()
    db.cursor.execute = db.execute
    db.fetch_one = mocker.MagicMock()
    db.cursor.fetchone = db.fetch_one
    db.fetchall = mocker.MagicMock()
    db.cursor.fetchall = db.fetch_all
    db.commit = mocker.MagicMock()
    db.rollback = mocker.MagicMock()
    db.close = mocker.MagicMock()
    return db


def test_execute(mocker, mock_postgres_db):
    """
    Test execute method
    """
    query = "SELECT * FROM users"
    mock_postgres_db.execute(query)

    mock_postgres_db.execute.assert_called_once_with(query)
    mock_postgres_db.cursor.execute.assert_called_once_with(query)

def test_fetch_one(mocker, mock_postgres_db):
    """
    Test fetch_one method
    """
    query = "SELECT * FROM users"
    mock_postgres_db.execute(query)
    mock_postgres_db.cursor.fetchone.return_value = ('John', 'Doe')
    result = mock_postgres_db.fetch_one()
    mock_postgres_db.cursor.execute.assert_called_once_with(query)
    mock_postgres_db.cursor.fetchone.assert_called_once_with()
    assert result == ('John', 'Doe')


def test_fetch_all(mocker, mock_postgres_db):
    """
    Test fetch_all method
    """
    query = "SELECT * FROM users LIMIT 10"
    mock_postgres_db.execute(query)
    mock_postgres_db.fetch_all.return_value = [('Alice', 'Smith'), ('Bob', 'Johnson')]
    result = mock_postgres_db.fetch_all()
    mock_postgres_db.cursor.execute.assert_called_once_with(query)
    mock_postgres_db.cursor.fetchall.assert_called_once_with()
    assert result == [('Alice', 'Smith'), ('Bob', 'Johnson')]


def test_commit(mocker, mock_postgres_db):
    """
    Test commit method
    """
    mock_postgres_db.commit()
    mock_postgres_db.commit.assert_called_once_with()


def test_rollback(mocker, mock_postgres_db):
    """
    Test rollback method
    """
    mock_postgres_db.rollback()
    mock_postgres_db.rollback.assert_called_once_with()

def test_close(mocker, mock_postgres_db):
    """Test close method"""

    mock_postgres_db.close()
    mock_postgres_db.close.assert_called_once_with()
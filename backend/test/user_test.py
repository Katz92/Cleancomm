"""
Test of class User
"""
from datetime import datetime, timedelta

import jwt
import bcrypt
import pytest
from unittest.mock import MagicMock
import psycopg2

TEST_EMAIL = "cleancomm@gmail.com"
TEST_PASSWORD = "testpassword"
TEST_HOST = "http://host-test-frontend.app/"
TEST_FIRSTNAME = "Toto"
TEST_LASTNAME = "DUPONT"
TEST_NEW_PASSWORD = "testnewpassword"
SECRET_KEY = "secret-key"
ALGORITHM = "HS256"
FAKE_EMAIL = "fake@cleancomm.com"

class MockPostgresDatabase:

    def __init__(self):
        self.cursor = MagicMock()

    def execute(self, query, params=None):
        print(params)
        self.cursor.execute.assert_called_with(query, params)
        if params[0] == "duplicate email":
            raise psycopg2.IntegrityError(pgcode="23505")

    def fetch_one(self):
        return self.cursor.fetchone.return_value

    def fetch_all(self):
        return self.cursor.fetchall.return_value

    def commit(self):
        self.cursor.commit.assert_called()

    def rollback(self):
        self.cursor.rollback.assert_called()

@pytest.fixture
def mock_salt(mocker):
    """
    Fixture to mock salt
    Args:
        mocker (MockFixture): use to mock object, function ...
    """
    mocker.patch('app.models.user.salt', "$2b$12$dMDN8PpZYSUQmCh.dM3euO")


@pytest.fixture
def mock_db(mocker):
    """
    mock the DB class instance
    """
    mock_postgres_db = MockPostgresDatabase()
    mocker.patch("app.models.user.PostgresDB")
    return mocker.patch("app.models.user.PostgresDB", return_value=mock_postgres_db)

@pytest.fixture
def mock_user_select(mocker):
    from app.models.user import User
    return mocker.patch.object(User, 'select')

@pytest.fixture
def mock_user_update(mocker):
    from app.models.user import User
    return mocker.patch.object(User, 'update')

@pytest.fixture
def expected_result(mocker):
    """expected result"""
    from app.resources.type.status import Status
    return {
        "id": 1,
        "email": "test@example.com",
        "password": "hashed_password",
        "host": "localhost",
        "first_name": "John",
        "last_name": "Doe",
        "lang": "en",
        "created_date": datetime(2023, 10, 2, 12, 32, 44, 298818),
        "updated_date": datetime(2023, 10, 2, 12, 32, 44, 298818),
        "status": Status.DISABLED.value,
    }

def test_select(expected_result, mock_db):
    """
    Test method select
    Args:
        mocker (_type_): _description_
    """
    from app.models.user import User
    print(mock_db)

    mock_db.cursor.description = [("id",),
                                  ("email",),
                                  ("password",),
                                  ("host",),
                                  ("first_name",),
                                  ("last_name",),
                                  ("lang",),
                                  ("created_date",),
                                  ("updated_date",),
                                  ("status",),]
    mock_db.fetch_one.return_value = (
        1,
        "test@example.com",
        "hashed_password",
        "localhost",
        "John",
        "Doe",
        "en",
        datetime(2023, 10, 2, 12, 32, 44, 298818),
        datetime(2023, 10, 2, 12, 32, 44, 298818),
        3)
    mock_db.execute.return_value = None

    user = User(email="test@example.com")
    result = user.select()
    
    assert result == expected_result
    mock_db.execute.assert_called_once()
    mock_db.fetch_one.assert_called_once()


def test_no_select(mock_db):
    """
    Test method select
    """
    from app.models.user import User
    mock_db.execute.return_value = None
    mock_db.fetch_one.return_value = None

    user = User(email=FAKE_EMAIL)
    result = user.select()
    assert result is None
    mock_db.execute.assert_called_once()
    mock_db.fetch_one.assert_called_once()

def test_create_user(mock_db, expected_result, mock_user_select):
    """
    Test method create work
    Args:
        mocker (MockFixture): use to mock object, function ...
        mock_salt (Fixture): use to mock salt
    """
    from app.models.user import User

    mock_db.execute.return_value = None
    mock_user_select.return_value = expected_result

    data = expected_result.copy()
    user = User()
    user.setattr(**data)
    result = user.create()
    assert result is not None
    assert result == expected_result

def test_not_create_user(mock_db, mock_user_select):
    """
    Test method create don't work
    Args:
        mocker (MockFixture): use to mock object, function ...
        mock_salt (Fixture): use to mock salt
    """
    from app.models.user import User

    user_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    mock_db.execute.return_value = None
    mock_user_select.return_value = None

    user = User()
    user.setattr(**user_data)
    result = user.create()
    assert result is None

def test_create_with_duplicate_email(mock_db, mock_user_select, expected_result, mocker, monkeypatch):
    """
    Test that the create method raises an IntegrityError exception when the user already exists.
    """
    from app.models.user import User
    import psycopg2.errorcodes

    mock_db.execute.return_value = None
    expected_result["email"] = "duplicate email"
    mock_user_select.return_value = expected_result
    user = User(
        email="duplicate email",
        password="password",
        host="localhost",
        first_name="John",
        last_name="Doe",
        lang="en"
    )
    # Mock the IntegrityError exception with a duplicate email code
    def mock_execute(query, params):
        raise psycopg2.IntegrityError("duplicate key value violates unique constraint", "23505")

    monkeypatch.setattr(mock_db, "execute", mock_execute)

    # Call the create method
    with pytest.raises(psycopg2.IntegrityError) as e:
        user.create()

    assert e is not None

class CustomIntegrityError(Exception):
    def __init__(self, message, pgcode):
        super().__init__(message)
        self.pgcode = pgcode

def raise_custom_integrity_error(message, pgcode):
    raise CustomIntegrityError(message, pgcode)

def test_create_with_duplicate_email_with_pgcode(mock_db, mock_user_select, expected_result, mocker, monkeypatch):
    """
    Test that the create method raises an IntegrityError exception when the user already exists.
    """
    from app.models.user import User
    import psycopg2.errorcodes

    mock_db.execute.return_value = None
    expected_result["email"] = "duplicate email"
    mock_user_select.return_value = None
    user = User(
        email="duplicate email",
        password="password",
        host="localhost",
        first_name="John",
        last_name="Doe",
        lang="en"
    )
    def mock_execute(query, params):
        raise_custom_integrity_error("duplicate key value violates unique constraint", "23505")

    monkeypatch.setattr(mock_db, "execute", mock_execute)

    with pytest.raises(CustomIntegrityError) as e:
        result = user.create()
        if e.value.pgcode == psycopg2.errorcodes.UNIQUE_VIOLATION:
            assert result == {"message": "User exists"}

    # Assert that the pgcode attribute is set correctly
    assert e.value.pgcode == psycopg2.errorcodes.UNIQUE_VIOLATION



def test_generate_token():
    """
    Test generate_token function
    """
    from app.models.user import User
    from app.resources.type.status import Status

    user = User()
    user.status = Status.PENDING
    token = user.generate_token(TEST_EMAIL, expiration_time=timedelta(days=1))
    assert token is not None
    assert len(token) > 0
    # Check if token is valid
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded_token
    assert decoded_token["sub"] == TEST_EMAIL
    assert decoded_token["status"] == Status.PENDING.value
    exp_time = decoded_token.get("exp")
    start_time = decoded_token.get("iat")
    assert exp_time is not None and start_time is not None
    duration = datetime.utcfromtimestamp(exp_time) - datetime.utcfromtimestamp(
        start_time
    )
    assert duration == timedelta(days=1)

def test_authenticate_user(mocker, mock_user_select):
    """
    Test method authenticate_user work
    Args:
        mocker (MockFixture): use to mock object, function ...
        mock_salt (Fixture): use to mock salt
    """
    from app.models.user import Status, User

    hashed_password = "hashedpassword"
    user_data = {
         "email": TEST_EMAIL,
         "password": TEST_PASSWORD,
         "token":""
    }
    # Setup mocks
    mocker.patch.object(jwt, 'encode', return_value = "testgeneratetoken")
    mocker.patch.object(bcrypt, 'checkpw', return_value = True)
    mock_user_select.return_value = {
            "id": 2,
            "email": TEST_EMAIL,
            "password": hashed_password,
            "host": TEST_HOST,
            "first_name": "test_firstname",
            "last_name": "test_lastname",
            "lang": "fr",
            "created_date": "2021-08-18 14:30:00",
            "updated_date": "2021-08-18 14:30:00",
            "status": Status.ACTIVE.value
    }

    user = User(**user_data)
    user_login_data = user.authenticate_user()
    print(user, user_login_data)
    assert user_login_data is not None
    assert user_login_data["email"] == TEST_EMAIL
    assert user_login_data["host"] == TEST_HOST
    assert user_login_data["first_name"] == "test_firstname"
    assert user_login_data["last_name"] == "test_lastname"
    assert user_login_data["lang"] == "fr"
    assert user_login_data["created_date"] == "2021-08-18 14:30:00"
    assert user_login_data["updated_date"] == "2021-08-18 14:30:00"
    assert user_login_data["status"] == Status.ACTIVE.value
    assert user_login_data["access_token"] == "testgeneratetoken"

def test_not_authenticate_user_fake_password(mock_user_select, expected_result, mocker):
    """
    Test method authenticate_user don't work
    Args:
        mocker (MockFixture): use to mock object, function ...
        mock_salt (Fixture): use to mock salt
    """
    from app.models.user import User

    user_data = {"email": TEST_EMAIL, "password": TEST_PASSWORD}

    mock_user_select.return_value = expected_result
    mocker.patch.object(bcrypt, 'checkpw', return_value = False)

    user = User(**user_data)
    token = user.authenticate_user()
    assert token is False

def test_not_authenticate_user_not_active(mock_user_select, expected_result, mocker):
    """
    Test method authenticate_user don't work
    Args:
        mocker (MockFixture): use to mock object, function ...
        mock_salt (Fixture): use to mock salt
    """
    from app.models.user import User, Status

    user_data = {
         "email": TEST_EMAIL,
         "password": TEST_PASSWORD
    }

    data = expected_result.copy()
    data['status'] = Status.PENDING.value
    mock_user_select.return_value = data
    mocker.patch.object(bcrypt, 'checkpw', return_value = True)

    user = User(**user_data)
    token = user.authenticate_user()
    assert token is False

def test_not_authenticate_not_exist_user(mock_user_select, mocker):
    """
    Test method authenticate_user don't work
    Args:
        mocker (MockFixture): use to mock object, function ...
        mock_salt (Fixture): use to mock salt
    """
    from app.models.user import User

    user_data = {
         "email": TEST_EMAIL,
         "password": TEST_PASSWORD
    }

    mock_user_select.return_value = expected_result
    mocker.patch.object(bcrypt, 'checkpw', return_value = False)

    user = User(**user_data)
    token = user.authenticate_user()
    assert token is False

def test_not_authenticate_user_not_active(mock_user_select, expected_result, mocker):
    """
    Test method authenticate_user don't work
    Args:
        mocker (MockFixture): use to mock object, function ...
        mock_salt (Fixture): use to mock salt
    """
    from app.models.user import User, Status

    user_data = {
         "email": TEST_EMAIL,
         "password": TEST_PASSWORD
    }

    data = expected_result.copy()
    data['status'] = Status.PENDING.value
    mock_user_select.return_value = data
    mocker.patch.object(bcrypt, 'checkpw', return_value = True)

    user = User(**user_data)
    token = user.authenticate_user()
    assert token is False

def test_not_authenticate_not_exist_user(mock_user_select, mocker):
    """
    Test method authenticate_user don't work
    Args:
        mocker (MockFixture): use to mock object, function ...
        mock_salt (Fixture): use to mock salt
    """
    from app.models.user import User

    user_data = {
         "email": TEST_EMAIL,
         "password": TEST_PASSWORD
    }

    mock_user_select.return_value = None
    mocker.patch.object(bcrypt, 'checkpw', return_value = True)

    user = User(**user_data)
    token = user.authenticate_user()
    assert token is False

@pytest.fixture
def updated_user_data():
    """..."""
    return {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
    }

def test_update_exist_with_status(mock_user_select, updated_user_data, expected_result):
    """
    Test method update in successful case
    Args:
        mocker (MockFixture): use to mock object, function ...
        mock_users (Fixture): use to mock users
    """
    from app.models.user import Status, User
    mock_user_select.return_value = expected_result

    updated_date = datetime.utcnow()
    updated_user_data["updated_date"] = updated_date

    updated_user = {
        "password": TEST_PASSWORD+"new",
        "status": Status.ACTIVE.value,
    }
    user = User(**updated_user_data)
    is_update = user.update(updated_user)
    assert updated_user.get('status') is not None
    assert is_update is not None

def test_update_exist_without_status(mock_user_select, updated_user_data, expected_result):
    """
    Test method update in successful case
    Args:
        mocker (MockFixture): use to mock object, function ...
        mock_users (Fixture): use to mock users
    """
    from app.models.user import User
    mock_user_select.return_value = expected_result

    updated_date = datetime.utcnow()
    updated_user_data["updated_date"] = updated_date

    updated_user = {
        "password": TEST_PASSWORD+"new",
    }
    user = User(**updated_user_data)
    is_update = user.update(updated_user)
    assert updated_user.get('status') is None
    assert is_update is not None

def test_update_exist_without_password(mock_user_select, updated_user_data, expected_result):
    """
    Test method update in successful case
    Args:
        mocker (MockFixture): use to mock object, function ...
        mock_users (Fixture): use to mock users
    """
    from app.models.user import Status, User
    mock_user_select.return_value = expected_result

    updated_date = datetime.utcnow()
    updated_user_data["updated_date"] = updated_date

    updated_user = {
        "status": Status.ACTIVE.value,
    }
    user = User(**updated_user_data)
    is_update = user.update(updated_user)
    assert updated_user.get('status') is not None
    assert is_update is not None


def test_generate_password_randomness():
    """
    Verifies that the generate_password function generates different passwords for each call.
    """
    from app.models.user import generate_password

    password1 = generate_password()
    password2 = generate_password()
    assert password1 != password2


def test_generate_password_default_length():
    """
    Verifies that the generate_password
    function generates a default password of the correct length (20 characters).
    """
    from app.models.user import generate_password

    password = generate_password()
    assert len(password) == 20

def test_setattr_with_kwargs(mock_user_select, expected_result):
    """..."""
    from app.models.user import User
    user = User(email=TEST_EMAIL)
    expected_result is not None
    user.setattr(**expected_result) is None
    mock_user_select.return_value == expected_result
    user.select() == expected_result

def test_setattr_without_kwargs(mock_user_select, expected_result):
    """..."""
    from app.models.user import User
    expected_result = {}
    user = User(email=TEST_EMAIL)
    expected_result is None
    user.setattr(**expected_result) is None
    mock_user_select.return_value == None
    user.select() == None
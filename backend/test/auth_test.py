"""
This file contains the tests for the authentication routes.

Attributes:
    - client (TestClient): The test client.
    - username (str): The username of the test user.
    - password (str): The password of the test user.
    - new_password (str): The new password of the test user.
"""
from test.conftest import TEST_CONFIG

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel
import pytest
import bcrypt

class AuthTest(BaseModel):
    """
    This class is purely to test user authentication.

    Attributes:
        - username (str): The email of the user.
        - password (str): The password of the user.
        - new_password (str): A new password of the user.
        - fake_username (str): A fake email.
        - fake_password (str): A fake password.
        - password_already_used (str): A password already used by another user.
        - reset_password (str): The password to reset to.
    """

    username: str
    password: str
    host: str
    hashed: str
    new_password: str
    fake_username: str
    fake_password: str
    password_already_used: str
    reset_password: str
    lang: str


app = FastAPI()

AUTH = AuthTest(
    username=TEST_CONFIG["username"],
    host=TEST_CONFIG["host"],
    password=TEST_CONFIG["password"],
    hashed=TEST_CONFIG["hashed"],
    new_password=TEST_CONFIG["new_password"],
    fake_username=TEST_CONFIG["fake_username"],
    fake_password=TEST_CONFIG["fake_password"],
    password_already_used=TEST_CONFIG["password_already_used"],
    reset_password=TEST_CONFIG["reset_password"],
    lang=TEST_CONFIG["lang"],
)

INVALID_CODE = "123456789"
EXPIRED_CODE = "64ba9472eb65306a1ba60efd"
INVALID_CODE_MESSAGE = "Invalid code"
NO_TOKEN_FOUND_MESSAGE = "No token found"
EXPIRED_TOKEN_MESSAGE = "Token expired."
INVALID_TOKEN_MESSAGE = "Invalid token."
INVALID_EMAIL_OR_PASSWORD_MESSAGE = "Invalid Email or password."
INCORRECT_MESSAGE = "Incorrect message."
VALID_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJndXlnYmFndWlkaS10ZXN0QHJpbnRpby5jb20iLCJzdGF0dXMiOjIsImlhdCI6MTY5NTA0OTUyMiwiZXhwIjoxODUyNzI5NTIyfQ.mIxAZ5pRQbdV4wai9ajVHpsDVPcEcVEJtswf1MF6XYk"
DISABLE_USER_VALID_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0Y2hha291cmFiYXN0b3VAZ21haWwuY29tIiwic3RhdHVzIjozLCJpYXQiOjE2OTUwNDk4MzMsImV4cCI6MTg1MjcyOTgzM30.s5GUQ8FiZ5QzTh5_0_n5rVvCt6LZ2lyWpUE8T_Rq1I8"


def mock_authenticated():
    """
    Mock the get_current_user function.
    """
    from app.models.user import User

    return User(email=AUTH.username, password=AUTH.hashed)


@pytest.fixture
def client():
    """
    Fixture for the test client.
    """
    from app.controllers import auth

    app.include_router(auth.AUTH)
    client = TestClient(app)
    return client


@pytest.fixture
def mock_user_select(mocker):
    """..."""
    from app.models.user import User
    return mocker.patch.object(User, "select")

@pytest.fixture
def mock_user_select(mocker):
    """..."""
    from app.models.user import User
    return mocker.patch.object(User, "select")

@pytest.fixture
def mock_user_update(mocker):
    """..."""
    from app.models.user import User
    return mocker.patch.object(User, "update")

@pytest.fixture
def mock_user(mocker):
    """
    Mock the User class.
    """
    return mocker.patch("app.controllers.auth.User").return_value


@pytest.fixture
def data_user(mocker):
    """......"""
    from app.models.user import Status
    return {
            "id": 2,
            "email": AUTH.username,
            "password": "hashed_password",
            "host": AUTH.host,
            "first_name": "firstName",
            "last_name": "lastName",
            "lang": "fr",
            "created_date": "createDate",
            "updated_date": "updatedDate",
            "status": Status.ACTIVE.value
    }
# Test for route /user/register ===============================================
def test_auth_register_create_success(client, mock_user, mocker):
    """
    Test the register route for success.
    """
    from app.models.user import Status

    user_data = {"email": AUTH.username,
                 "host": AUTH.host,
                 "first_name": "firstName", 
                 "last_name": "lastName",
                 "lang": "french",
                 "created_date": "createDate",
                 "updated_date": "updatedDate",
                 "status": Status.ACTIVE.value
                }
    # Set up mock
    mock_user.select.return_value = None
    mock_user.create.return_value = user_data
    mocker.patch(
        "app.controllers.auth.send_recovery_mail", return_value="Email sent successfully!"
    )
    mock_user.select.return_value = user_data

    response = client.post("/user/register", json={"data": user_data})
    assert response.status_code == 200, INVALID_CODE_MESSAGE
    assert response.json()["email"] == AUTH.username, INCORRECT_MESSAGE
    assert response.json()["host"] == AUTH.host, INCORRECT_MESSAGE
    assert response.json()["first_name"] == "firstName", INCORRECT_MESSAGE
    assert response.json()["last_name"] == "lastName", INCORRECT_MESSAGE
    assert response.json()["lang"] == "french", INCORRECT_MESSAGE
    assert response.json()["created_date"] == "createDate", INCORRECT_MESSAGE
    assert response.json()["updated_date"] == "updatedDate", INCORRECT_MESSAGE
    assert response.json()["status"] == Status.ACTIVE.value, INCORRECT_MESSAGE


def test_auth_register_create_exception(client, mock_user, mocker):
    """
    Test the register route for exception.
    """
    from app.models.user import Status
    
    
    user_data = {"email": AUTH.username,
                 "host": AUTH.host,
                 "first_name": "firstName", 
                 "last_name": "lastName",
                 "lang": "french",
                 "created_date": "createDate",
                 "updated_date": "updatedDate",
                 "status": Status.ACTIVE.value
                }
    # Set up mock
    mock_user.select.return_value = None
    mock_user.create.side_effect = Exception("Some error occurred")
    mocker.patch(
        "app.controllers.auth.send_recovery_mail", return_value="Email sent successfully!"
    )

    response = client.post("/user/register", json={"data": user_data})
    assert response.status_code == 400, INVALID_CODE_MESSAGE


def test_auth_register_email_already_exists(client, mock_user_select,mocker):
    """
    Test the register route when email already exists.
    """
    from app.models.user import Status

    # Set up mock
    mock_user_select.return_value = {"email": AUTH.username,
                                        "host": AUTH.host,
                                        "password": AUTH.hashed,
                                        "first_name": "firstName", 
                                        "last_name": "lastName",
                                        "lang": "french",
                                        "created_date": "createDate",
                                        "updated_date": "updatedDate",
                                        "status": Status.ACTIVE.value}

    user_data = {"email": AUTH.username,
                 "host": AUTH.host,
                 "first_name": "firstName", 
                 "last_name": "lastName",
                 "lang": "french",
                 "created_date": "createDate",
                 "updated_date": "updatedDate",
                 "status": Status.ACTIVE.value
                }
    mocker.patch('app.controllers.auth.send_recovery_mail', return_value="Email sent successfully!")

    response = client.post("/user/register", json={"data": user_data})
    assert response.status_code == 200, INVALID_CODE_MESSAGE
    assert response.json()["email"] == AUTH.username, INCORRECT_MESSAGE
    assert response.json()["host"] == AUTH.host, INCORRECT_MESSAGE
    assert response.json()["first_name"] == "firstName", INCORRECT_MESSAGE
    assert response.json()["last_name"] == "lastName", INCORRECT_MESSAGE
    assert response.json()["lang"] == "french", INCORRECT_MESSAGE
    assert response.json()["created_date"] == "createDate", INCORRECT_MESSAGE
    assert response.json()["updated_date"] == "updatedDate", INCORRECT_MESSAGE
    assert response.json()["status"] == Status.ACTIVE.value, INCORRECT_MESSAGE


# Test for route /user/login ==================================================
def test_auth_login(client, mock_user_select, mocker, data_user):
    """
    Test the login route for success.
    """
    from app.models.user import Status

    # Set up mock
    mocker.patch.object(bcrypt, 'checkpw', return_value = True)
    mock_user_select.return_value = data_user
    user_data = {"username": AUTH.username, "password": AUTH.password}
    response = client.post("/user/login", data=user_data)
    assert response.status_code == 200, INVALID_CODE_MESSAGE
    assert response.json()["email"] == AUTH.username, INCORRECT_MESSAGE
    assert response.json()["host"] == AUTH.host, INCORRECT_MESSAGE
    assert response.json()["first_name"] == "firstName", INCORRECT_MESSAGE
    assert response.json()["last_name"] == "lastName", INCORRECT_MESSAGE
    assert response.json()["lang"] == "fr", INCORRECT_MESSAGE
    assert response.json()["created_date"] == "createDate", INCORRECT_MESSAGE
    assert response.json()["updated_date"] == "updatedDate", INCORRECT_MESSAGE
    assert response.json()["status"] == Status.ACTIVE.value, INCORRECT_MESSAGE
    assert response.json()["access_token"] is not None, NO_TOKEN_FOUND_MESSAGE
    assert response.json()["token_type"] == "Bearer", "Incorrect token type"

def test_auth_login_wrong_password(client, mock_user_select, mocker, data_user):
    """
    Test the login route for wrong password.
    """
    mocker.patch.object(bcrypt, 'checkpw', return_value = False)
    mock_user_select.return_value = data_user
    response = client.post("/user/login", data={"username": AUTH.username,
                                               "password": AUTH.fake_password})
    assert response.status_code == 400, INVALID_CODE_MESSAGE
    assert (
        response.json()["detail"] == INVALID_EMAIL_OR_PASSWORD_MESSAGE
    ), INCORRECT_MESSAGE


def test_auth_login_wrong_username(client, mock_user_select, mocker, data_user):
    """
    Test the login route for wrong username.
    """
    mocker.patch.object(bcrypt, 'checkpw', return_value = False)
    mock_user_select.return_value = data_user
    response = client.post("/user/login", data={"username": AUTH.fake_username,
                                                "password": AUTH.password})
    assert response.status_code == 400, INVALID_CODE_MESSAGE
    assert (
        response.json()["detail"] == INVALID_EMAIL_OR_PASSWORD_MESSAGE
    ), INCORRECT_MESSAGE


def test_auth_login_wrong_user(client, mock_user_select, mocker):
    """
    Test the login route for wrong username and password.
    """
    mocker.patch.object(bcrypt, 'checkpw', return_value = None)
    mock_user_select.return_value = None
    response = client.post("/user/login", data={"username": AUTH.fake_username,
                                               "password": AUTH.fake_password})
    assert response.status_code == 400, INVALID_CODE_MESSAGE
    assert (
        response.json()["detail"] == INVALID_EMAIL_OR_PASSWORD_MESSAGE
    ), INCORRECT_MESSAGE


# Test for route /user/send-reset-link ========================================
def test_auth_password_reset_link(client, mocker, mock_user):
    """
    Test the send-reset-link route for successful request.
    """
    # Set up mock
    mock_user.select.return_value = {
        "email": AUTH.username,
        "host": AUTH.host,
        "password": AUTH.hashed,
        "lang": AUTH.lang,
        "first_name": AUTH.fake_username,
    }
    mocker.patch("app.controllers.auth.send_recovery_mail",
                 return_value="Email sent successfully!")
    user_data = {"email": AUTH.username}

    response = client.post(f"/user/send-reset-link", json={"data": user_data})
    assert response.status_code == 200, INVALID_CODE_MESSAGE
    assert response.json()["message"] == "Reset password link sent "\
        "successfully.", INCORRECT_MESSAGE


def test_auth_password_reset_link_invalid_email(client, mock_user):
    """
    Test the send-reset-link route for invalid email.
    """
    mock_user.select.return_value = None
    user_data = {"email": AUTH.username}
    response = client.post(f"/user/send-reset-link", json={"data": user_data})
    assert response.status_code == 404, INVALID_CODE_MESSAGE
    assert response.json()["detail"] == "Invalid email.", INCORRECT_MESSAGE


def test_auth_password_reset_link_exception(client, mock_user):
    """
    Test the send-reset-link route for exception.
    """

    def raise_value_error(*args, **kwargs):
        raise ValueError("Custom")

    # Set up mock
    mock_user.select.return_value = {"email": AUTH.username, "password": AUTH.hashed}
    mock_user.generate_token.side_effect = raise_value_error
    user_data = {"email": AUTH.username}
    response = client.post(f"/user/send-reset-link", json={"data": user_data})
    assert response.status_code == 400, INVALID_CODE_MESSAGE

def test_auth_password_reset_link_status_disabled(client, mocker, mock_user_select):
    """
    Test the send-reset-link route when user is disabled.
    """
    from app.resources.type.status import Status

    # Set up mock
    mock_user_select.return_value = {"email": AUTH.username,
                                        "password": AUTH.hashed,
                                        "host": AUTH.host,
                                        "first_name": "firstName",
                                        "last_name": "lastName",
                                        "lang": "french",
                                        "created_date": "createDate",
                                        "updated_date": "updatedDate",
                                        "status": Status.DISABLED.value}

    user_data = {"email": AUTH.username}

    response = client.post(f"/user/send-reset-link", json={"data": user_data})
    assert response.status_code == 400, INVALID_CODE_MESSAGE
    assert response.json()["detail"] == "User is disabled.", INCORRECT_MESSAGE


# Test for route /user/reset ==================================================
def test_auth_reset_password(client, mock_user, mocker):
    """
    Test the reset route for successful request.
    """
    origin_user = {"email": AUTH.username, "password": AUTH.new_password}
    # Setup mock
    mock_user.update.return_value = origin_user

    response = client.post(
        "/user/reset",
        json={"data": origin_user},
        headers={"Authorization": f"Bearer {VALID_TOKEN}"},
    )
    assert response.status_code == 200, (
        "Incorrect code, error: " f'{response.json()["detail"]}'
    )
    assert (
        response.json()["message"] == "Password successfully reset."
    ), INCORRECT_MESSAGE


def test_auth_reset_password_no_data(client, mocker, mock_user):
    """
    Test the reset route when no data sent.
    """
    response = client.post(
        "/user/reset",
        json={"data": {}},
        headers={"Authorization": f"Bearer {VALID_TOKEN}"},
    )
    assert response.status_code == 400, INVALID_CODE_MESSAGE
    assert response.json()["detail"] == "No data sent.", INCORRECT_MESSAGE


def test_auth_reset_password_invalid_email(client, mock_user):
    """
    Test the reset route when invalid email is sent.
    """
    reset_user = {"email": AUTH.username, "password": AUTH.new_password}
    # Set up mock
    mock_user.update.return_value = None

    response = client.post(
        "/user/reset",
        json={"data": reset_user},
        headers={"Authorization": f"Bearer {VALID_TOKEN}"},
    )
    assert response.status_code == 400, (
        "Incorrect code, error: " f'{response.json()["detail"]}'
    )
    assert response.json()["detail"] == "Invalid email.", INCORRECT_MESSAGE


def test_auth_reset_password_status_disabled(client, mocker, mock_user_select):
    """
    Test the reset route when user is disabled.
    """
    from app.resources.type.status import Status

    reset_user = {"email": AUTH.username, "password": AUTH.new_password}
    # Set up mock
    mock_user_select.return_value = {"email": AUTH.username,
                                        "password": AUTH.hashed,
                                        "host": AUTH.host,
                                        "first_name": "firstName",
                                        "last_name": "lastName",
                                        "lang": "french",
                                        "created_date": "createDate",
                                        "updated_date": "updatedDate",
                                        "status": Status.DISABLED.value}

    response = client.post(
        "/user/reset",
        json={"data": reset_user},
        headers={"Authorization": f"Bearer {DISABLE_USER_VALID_TOKEN}"},
    )

    assert response.status_code == 400, (
        "Incorrect code, error: " f'{response.json()["detail"]}'
    )
    assert response.json()["detail"] == "User is disabled.", INCORRECT_MESSAGE


def test_logout_success(client, mock_user_select, data_user):
    email = "guygbaguidi-test@rintio.com"
    mock_user_select.return_value = data_user

    response = client.post(
        "/user/logout",
        json={"data": {"email": email}},
        headers={"Authorization": f"Bearer {VALID_TOKEN}"}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "User logged out successfully."}


def test_logout_invalid_email(client, mock_user_select, data_user):
    email = AUTH.fake_username
    mock_user_select.return_value = None

    response = client.post(
        "/user/logout",
        json={"data": {"email": email}},
        headers={"Authorization": f"Bearer {VALID_TOKEN}"}
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Invalid email."}

def test_update_profile_with_success(client, mock_user):
    """
    Test the update profile route when the user is connected.
    """
    from app.resources.type.status import Status

    # Prepare test data for the update
    update_data = {
        "first_name": "UpdatedFirstName",
        "last_name": "UpdatedLastName",
        "lang": "en",
    }

    # Set the return value of mock_user_update to a realistic user data dictionary
    mock_user.update.return_value = {
        "email": AUTH.username,
        "host": AUTH.host,
        "first_name": update_data["first_name"],
        "last_name": update_data["last_name"],
        "lang": update_data["lang"],
        "created_date": "createDate",
        "updated_date": "updatedDate",
        "status": Status.ACTIVE.value,
    }

    # Perform the request with the valid token
    response = client.post(
        "/user/update",
        json={"data": update_data},
        headers={"Authorization": f"Bearer {VALID_TOKEN}"}
    )

    # Validate the response
    assert response.status_code == 200
    updated_user = response.json()

    # Assert that the updated user information matches the expected values
    assert updated_user["first_name"] == update_data["first_name"]
    assert updated_user["last_name"] == update_data["last_name"]
    assert updated_user["lang"] == update_data["lang"]

    # Perform additional assertions using the mock_user_update fixture
    assert updated_user["updated_date"] == "updatedDate"
    assert updated_user["status"] == Status.ACTIVE.value

def test_update_profile_without_data(client, mock_user):
    """
    Test the update profile route when no data sent.
    """
    response = client.post(
        "/user/update",
        json={"data": {}},
        headers={"Authorization": f"Bearer {VALID_TOKEN}"}
    )

    assert response.status_code == 400, INVALID_CODE_MESSAGE
    assert response.json()["detail"] == "No data sent.", INCORRECT_MESSAGE

def test_update_profile_with_invalid_email(client, mock_user):
    """
    Test the update profile route when no data sent.
    """
    reset_user = {"email": AUTH.username, "password": AUTH.new_password}
    # Set up mock
    mock_user.update.return_value = None

    response = client.post(
        "/user/update",
        json={"data": reset_user},
        headers={"Authorization": f"Bearer {VALID_TOKEN}"},
    )
    assert response.status_code == 400, (
        "Incorrect code, error: " f'{response.json()["detail"]}'
    )
    assert response.json()["detail"] == "Invalid email.", INCORRECT_MESSAGE

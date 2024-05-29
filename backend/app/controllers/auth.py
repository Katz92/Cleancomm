"""
This file contains the routes for authentication.

Attributes:
    - AUTH (APIRouter): The router for the authentication.
    - oauth2_scheme (OAuth2PasswordBearer): The scheme for the authentication.
    - oauth2_scheme_session (OAuth2PasswordBearer): The scheme for the authentication for
      endpoints that require the user to be connected.
    - User (BaseModel): The model for the user.
    - BodyRequest (BaseModel): The model for body data sent
    - register (function): The function to register an user
    - oauth2_login (function): The function to log in an user.
    - logout (function): The function to log out a user.
    - send_password_reset_link (function): The function to send a link to an
                                           user by mail to reset his password.
    - reset_password (function): The function to reset the password of an user.
"""
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials

from app.services.apphttpbearer import AppHttpBearer
from app.models.user import Status, User
from app.services.send_mail import send_recovery_mail
from app.pydantic.models import BodyRequest
from app.resources.dependencies import oauth2_scheme_session

INVALID_EMAIL_OR_PASSWORD_MESSAGE = "Invalid Email or password."
PASSWORD_ALREADY_USED_MESSAGE = "Password already used."
INVALID_EMAIL_MESSAGE = "Invalid email."

AUTH = APIRouter(
    prefix="/user",
    tags=["auth"],
    responses={400: {"description": INVALID_EMAIL_OR_PASSWORD_MESSAGE}},
)

oauth2_sheme = AppHttpBearer()


@AUTH.post("/register", description="Register a new user.")
def register(data: BodyRequest):
    """
    Register a new user.

    - user (BodyRequest): The user to register. The user email and password are required.

    Returns:
        200: User is successfully registered.
        400: An error occurred.
    """
    user_data = data.data
    new_user = User(email=user_data["email"])

    # Check if email already exists
    if not new_user.select():
        # Insert user in db
        new_user.host = user_data["host"]
        new_user.first_name = user_data["first_name"]
        new_user.last_name = user_data["last_name"]
        new_user.lang = user_data["lang"]

        try:
            new_user.create()
        except Exception as exception:
            raise HTTPException(
                status_code=400, detail=f"Something went wrong:" f"{str(exception)}"
            ) from exception

    # Generate token and save it in db
    reset_token = new_user.generate_token(
        user_data["email"], expiration_time=timedelta(minutes=15)
    )

    result = new_user.select()
    result.pop("id", None)
    result.pop("password", None)
    result["created_date"] = str(result["created_date"])
    result["updated_date"] = str(result["updated_date"])

    send_recovery_mail(
        token=reset_token,
        host=user_data["host"],
        email=user_data["email"],
        lang=result["lang"],
        first_name=result["first_name"],
    )

    return JSONResponse(content=result, status_code=200)


@AUTH.post("/login", description="Login by filling form data with email and password.")
def oauth2_login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Log in an user with given email and password.

    - form_data (OAuth2PasswordRequestForm): The form data containing the email and password.
                There are two fields that are required, the others are optional

        grant_type: The grant type. This must be the fixed string "password".
        username: The email address of the user, this is required.
        password: The password of the user, this is required.
        scope: The scope of the access token, this is optional.
        client_id: The client id, this is optional.
        client_secret: The client secret, this is optional.

    Returns:
        200 Token: The access token and token type.
        400: Invalid Email or password.
    """
    user = User(email=form_data.username, password=form_data.password)
    user_data = user.authenticate_user()
    if not user_data:
        raise HTTPException(
            status_code=400,
            detail=INVALID_EMAIL_OR_PASSWORD_MESSAGE,
            headers={"WWW-Authenticate": "Bearer"},
        )
    return JSONResponse(content=user_data, status_code=200)


@AUTH.post("/logout", dependencies=[Depends(oauth2_sheme)], description="Logout a user")
def logout(data: BodyRequest) -> JSONResponse:

    """
    Log out a user.

    - email (BodyRequest): Email of the user to log out (required)

    Returns:
        200: User logged out successfully.
    """
    # Check if email exists
    user = User(email=data.data["email"])
    if not user.select():
        raise HTTPException(status_code=404, detail=INVALID_EMAIL_MESSAGE)

    user.end_session()
    return JSONResponse(
        content={"message": "User logged out successfully."},
        status_code=200,
    )


@AUTH.post("/send-reset-link", description="Send link by mail to reset" "password.")
def send_password_reset_link(data_user: BodyRequest):
    """
    Send a link to an user by mail to reset his password.

    - email (str): The email address of the user.

    Returns:
        200: Mail with the link has been successfully sent.
        400: Invalid email.
    """
    data = data_user.data
    # Check if email exists
    user = User(email=data["email"])
    if not user.select():
        raise HTTPException(status_code=404, detail=INVALID_EMAIL_MESSAGE)

    # Check if user is disabled
    if user.status == Status.DISABLED:
        raise HTTPException(status_code=400, detail="User is disabled.")

    try:
        # Generate token and send mail
        updated_user_data = {"status": Status.PENDING.value}
        user.update(updated_user_data)
        reset_token = user.generate_token(
            data["email"], expiration_time=timedelta(minutes=15)
        )
        user = user.select()

        send_recovery_mail(
            token=reset_token,
            host=user["host"],
            email=user["email"],
            lang=user["lang"],
            first_name=user["first_name"],
        )
        return JSONResponse(
            content={"message": "Reset password link sent successfully."},
            status_code=200,
        )
    except Exception as exception:
        raise HTTPException(
            status_code=400, detail=f"Something went wrong:" f"{str(exception)}"
        ) from exception


@AUTH.post(
    "/reset", dependencies=[Depends(oauth2_sheme)], description="Reset password."
)
def reset_password(
    login: BodyRequest,
    decode_token: HTTPAuthorizationCredentials = Depends(oauth2_sheme),
) -> JSONResponse:
    """
    Reset password of a user.

    - new_login (Reset): The new login informations of the user and reset token id.

    Returns:
        200: Password is successfully reset.
        400: An error occurred.
    """
    new_login = login.data
    if not new_login:
        raise HTTPException(status_code=400, detail="No data sent.")

    # Check if token is valid
    email = decode_token["sub"]
    status = decode_token["status"]
    user_to_reset = User(email=email)

    # Check if user is disabled
    if status == Status.DISABLED.value:
        raise HTTPException(status_code=400, detail="User is disabled.")

    # Hash and update user password
    updated_user_data = {
        "password": str(new_login["password"]),
        "status": Status.ACTIVE.value,
    }
    original = user_to_reset.update(updated_user_data)
    if original is None:
        raise HTTPException(status_code=400, detail=INVALID_EMAIL_MESSAGE)

    return JSONResponse(
        content={"message": "Password successfully reset."}, status_code=200
    )

@AUTH.post("/update", description="Update the user information")
def update_profile(
    user_data: BodyRequest,
    login_decode_token: HTTPAuthorizationCredentials = Depends(oauth2_scheme_session),
):
    """
    Update user profile.

    - user_data (BodyRequest): Define the user information to modify/update.

    Returns:
        200: User information is successfully updated.
        400: An error occurred.
    """
    update_data = user_data.data
    if not update_data:
        raise HTTPException(status_code=400, detail="No data sent.")

    email = login_decode_token["sub"]
    current_user = User(email=email)

    # Update user information in the database based on user_data
    updated_user = current_user.update(update_data)


    if updated_user is None:
        raise HTTPException(status_code=400, detail=INVALID_EMAIL_MESSAGE)

    updated_user.pop("id", None)
    updated_user.pop("password", None)
    updated_user["created_date"] = str(updated_user["created_date"])
    updated_user["updated_date"] = str(updated_user["updated_date"])


    return JSONResponse(content=updated_user, status_code=200)

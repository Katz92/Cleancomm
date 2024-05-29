"""
Test of method send_mail
"""
from fastapi import HTTPException
import pytest

from unittest.mock import MagicMock

@pytest.fixture
def mock_sendgrid_api_client(mocker):
    """
    Fixture to mock SendGridAPIClient.
    """
    return mocker

# def test_send_mail_success(mocker, mock_sendgrid_api_client):
#     # Arrange
#     from app.services.send_mail import send_mail

#     recipient = "test@example.com"
#     template_data = {
#         "link": "google.com",
#         "first_name": "Toto",
#         "lang": "fr",
#     }

#     send_mock = MagicMock()
#     send_mock.return_value.status_code = 202  # Set the desired status code
#     mock_sendgrid_api_client.return_value.send = send_mock


#     status_code = send_mail(recipient, template_data)
#     assert status_code == 202


# def test_send_mail_exception():
#     """
#     Test method send_mail exception
#     """
#     from app.services.send_mail import send_mail

#     recipient = "test@example.com"
#     template_data = "link"

#     with pytest.raises(HTTPException):
#         send_mail(recipient, template_data)


def test_send_recovery_mail(mocker):
    """
    Test send_recovery_Mail function in succesful case
    """
    from app.services.send_mail import send_recovery_mail

    RECEIVER = "username"
    RECEIVER_HOST = "https://host-test-frontend.com"
    TEST_CODE = "expired_code"
    LANG = "fr"
    FIRST_NAME = "Toto"

    mocker.patch("app.services.send_mail.send_mail", return_value="Email sent successfully!")
    assert (
        send_recovery_mail(
            token=TEST_CODE,
            host=RECEIVER_HOST,
            email=RECEIVER,
            first_name=FIRST_NAME,
            lang=LANG,
        )
        == 200
    )

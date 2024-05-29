# pylint: disable=invalid-name
"""
App dependencies
"""
from app.services.apphttpbearer import AppHttpBearer

oauth2_scheme_session = AppHttpBearer(check_session=True)

"""
Models describing data sent and received in the API
"""

from typing import Any
from pydantic import BaseModel


class BodyRequest(BaseModel):
    """
    Generic Model body

    Attributes:
        data: Data sent in body
    """

    data: Any

"""
Official Temp Mail API (https://temp-mail.io) Wrapper for Python.
"""

__version__ = "0.1.0b1"

from .client import TempMailClient
from .models import (
    RateLimit,
    Domain,
    EmailAddress,
    EmailMessage,
    Attachment,
)
from .exceptions import (
    TempMailError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
)

__all__ = [
    "TempMailClient",
    "RateLimit",
    "Domain",
    "EmailAddress",
    "Attachment",
    "EmailMessage",
    "TempMailError",
    "AuthenticationError",
    "RateLimitError",
    "ValidationError",
]

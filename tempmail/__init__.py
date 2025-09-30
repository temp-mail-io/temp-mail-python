"""
Official Temp Mail API (https://temp-mail.io) Wrapper for Python.
"""

__version__ = "1.0.1"

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

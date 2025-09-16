"""
Official Temp Mail API (https://temp-mail.io) Wrapper for Python.
"""

__version__ = "0.1.0"

from .client import TempMailClient
from .models import (
    RateLimit,
    Domain,
    EmailAddress,
    EmailMessage,
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
    "EmailMessage",
    "TempMailError",
    "AuthenticationError",
    "RateLimitError",
    "ValidationError",
]

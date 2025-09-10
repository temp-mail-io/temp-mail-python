"""Official Temp Mail API (https://temp-mail.io) Wrapper for Python."""

__version__ = "1.0.0"

from .client import TempMailClient
from .models import (
    RateLimit,
    Domain,
    EmailAddress,
    EmailMessage,
    CreateEmailOptions,
    ListMessagesOptions,
)
from .exceptions import (
    TempMailError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    APIError,
)

__all__ = [
    "TempMailClient",
    "RateLimit",
    "Domain",
    "EmailAddress",
    "EmailMessage",
    "CreateEmailOptions",
    "ListMessagesOptions",
    "TempMailError",
    "AuthenticationError",
    "RateLimitError",
    "ValidationError",
    "APIError",
]

"""Exceptions for the Temp Mail API client."""

from typing import Optional


class TempMailError(Exception):
    """Base exception for all Temp Mail API errors."""

    pass


class AuthenticationError(TempMailError):
    """Raised when API key is invalid or missing."""

    pass


class RateLimitError(TempMailError):
    """Raised when API rate limit is exceeded."""

    pass


class ValidationError(TempMailError):
    """Raised when request parameters are invalid."""

    pass


class APIError(TempMailError):
    """Raised when the API returns an error response."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[dict] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data

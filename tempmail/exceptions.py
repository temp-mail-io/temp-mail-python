"""Exceptions for the Temp Mail API client."""


class TempMailError(Exception):
    """Base exception for all Temp Mail API errors."""

    pass


class AuthenticationError(TempMailError):
    """Raised when API Key is invalid or missing."""

    pass


class RateLimitError(TempMailError):
    """Raised when API Rate Limit is exceeded."""

    pass


class ValidationError(TempMailError):
    """Raised when request parameters are invalid."""

    pass

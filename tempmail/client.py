"""Temp Mail API client implementation."""

import json
import time
from typing import Optional, List, Dict, Any, Union
from urllib.parse import urljoin
import requests

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


class TempMailClient:
    """Client for interacting with the Temp Mail API."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.temp-mail.org",
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """
        Initialize the Temp Mail client.

        Args:
            api_key: Your Temp Mail API key
            base_url: Base URL for the API (default: https://api.temp-mail.org)
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum number of retry attempts (default: 3)
        """
        if not api_key:
            raise AuthenticationError("API key is required")

        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "temp-mail-python/1.0.0",
        })

        self._last_rate_limit: Optional[RateLimit] = None

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make an HTTP request to the API."""
        url = urljoin(self.base_url, endpoint)

        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    timeout=self.timeout,
                )

                # Update rate limit info from headers
                self._update_rate_limit_from_headers(response.headers)

                # Handle different status codes
                if response.status_code == 200 or response.status_code == 201:
                    return response.json()
                elif response.status_code == 401:
                    raise AuthenticationError("Invalid API key")
                elif response.status_code == 429:
                    raise RateLimitError("Rate limit exceeded")
                elif response.status_code == 400:
                    error_data = response.json() if response.content else {}
                    raise ValidationError(
                        error_data.get("message", "Invalid request parameters")
                    )
                else:
                    error_data = response.json() if response.content else {}
                    raise APIError(
                        error_data.get(
                            "message",
                            f"API request failed with status {response.status_code}",
                        ),
                        status_code=response.status_code,
                        response_data=error_data,
                    )

            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries:
                    raise TempMailError(
                        f"Request failed after {self.max_retries + 1} attempts: {str(e)}"
                    )
                time.sleep(2**attempt)  # Exponential backoff

        # This should never be reached due to the raise in the except block
        raise TempMailError("Unexpected error in request handling")

    def _update_rate_limit_from_headers(self, headers: Any) -> None:
        """Update rate limit info from response headers."""
        try:
            if "X-RateLimit-Limit" in headers:
                self._last_rate_limit = RateLimit(
                    limit=int(headers["X-RateLimit-Limit"]),
                    remaining=int(headers.get("X-RateLimit-Remaining", 0)),
                    reset=int(headers.get("X-RateLimit-Reset", 0)),
                )
        except (ValueError, KeyError):
            pass

    def create_email(
        self, options: Optional[CreateEmailOptions] = None
    ) -> EmailAddress:
        """
        Generate a new temporary email address.

        Args:
            options: Configuration options for email creation

        Returns:
            EmailAddress: The generated email address
        """
        params: Dict[str, Any] = {}
        if options:
            if options.domain:
                params["domain"] = options.domain
            if options.prefix:
                params["prefix"] = options.prefix

        data = self._make_request("POST", "/emails", params=params)

        return EmailAddress(
            email=data["email"],
            domain=data["domain"],
            created_at=data.get("created_at"),
        )

    def list_domains(self) -> List[Domain]:
        """
        Get a list of available email domains.

        Returns:
            List[Domain]: Available domains
        """
        data = self._make_request("GET", "/domains")

        return [Domain(domain=domain) for domain in data.get("domains", [])]

    def list_email_messages(
        self, email: str, options: Optional[ListMessagesOptions] = None
    ) -> List[EmailMessage]:
        """
        Get messages for a specific email address.

        Args:
            email: The email address to get messages for
            options: Options for filtering messages

        Returns:
            List[EmailMessage]: List of email messages
        """
        if not email:
            raise ValidationError("Email address is required")

        params: Dict[str, Any] = {"email": email}
        if options:
            if options.limit:
                params["limit"] = options.limit
            if options.offset:
                params["offset"] = options.offset

        data = self._make_request("GET", "/messages", params=params)

        messages = []
        for msg_data in data.get("messages", []):
            messages.append(
                EmailMessage(
                    id=msg_data["id"],
                    from_addr=msg_data["from"],
                    to_addr=msg_data["to"],
                    subject=msg_data["subject"],
                    body_text=msg_data["body_text"],
                    body_html=msg_data.get("body_html"),
                    created_at=msg_data.get("created_at"),
                    attachments=msg_data.get("attachments"),
                )
            )

        return messages

    def delete_message(self, message_id: str) -> bool:
        """
        Delete a specific message.

        Args:
            message_id: ID of the message to delete

        Returns:
            bool: True if deletion was successful
        """
        if not message_id:
            raise ValidationError("Message ID is required")

        self._make_request("DELETE", f"/messages/{message_id}")
        return True

    def get_rate_limit(self) -> Optional[RateLimit]:
        """
        Get current rate limit information.

        Returns:
            RateLimit: Current rate limit status, or None if not available
        """
        # Make a lightweight request to get fresh rate limit info
        self._make_request("GET", "/rate-limit")
        return self._last_rate_limit

    @property
    def last_rate_limit(self) -> Optional[RateLimit]:
        """Get the last known rate limit information."""
        return self._last_rate_limit

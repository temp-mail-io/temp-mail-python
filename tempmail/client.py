"""Temp Mail API client implementation."""

import json
import time
from typing import Optional, List, Dict, Any
from urllib.parse import urljoin
import requests

from . import __version__
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
    APIError,
)


class TempMailClient:
    """Client for interacting with the Temp Mail API."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.temp-mail.io",
        timeout: int = 30,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout

        self.session = requests.Session()
        self.session.headers.update({
            "X-API-Key": api_key,
            "Content-Type": "application/json",
            "User-Agent": f"temp-mail-python/{__version__}",
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
            if response.status_code >= 200 and response.status_code < 300:
                return response.json()
            elif response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            elif response.status_code == 400:
                error_data = response.json() if response.content else {}
                error_message = self._extract_error_message(error_data, "Invalid request parameters")
                raise ValidationError(error_message)
            else:
                error_data = response.json() if response.content else {}
                error_message = self._extract_error_message(
                    error_data,
                    f"API request failed with status {response.status_code}"
                )
                raise APIError(
                    error_message,
                    status_code=response.status_code,
                    response_data=error_data,
                )

        except requests.exceptions.RequestException as e:
            raise TempMailError(f"Request failed: {str(e)}")

    def _extract_error_message(self, error_data: Dict[str, Any], default_message: str) -> str:
        """Extract error message from API response."""
        # Try new API format: {"error": {"detail": "message"}}
        if "error" in error_data and isinstance(error_data["error"], dict):
            error_obj = error_data["error"]
            if "detail" in error_obj:
                return str(error_obj["detail"])
            if "message" in error_obj:
                return str(error_obj["message"])

        # Try old format: {"message": "error"}
        if "message" in error_data:
            return str(error_data["message"])

        return default_message

    def _update_rate_limit_from_headers(self, headers: Any) -> None:
        """Update rate limit info from response headers."""
        self._last_rate_limit = RateLimit(
            limit=int(headers["X-RateLimit-Limit"]),
            remaining=int(headers.get("X-RateLimit-Remaining", 0)),
            reset=int(headers.get("X-RateLimit-Reset", 0)),
        )

    def create_email(
        self, email: Optional[str] = None, domain: Optional[str] = None, domain_type: Optional[str] = None,
    ) -> EmailAddress:
        """
        Create a new temporary email address.
        :param email: Optional specific email address to create
        :param domain: Optional domain to use
        :param domain_type: Optional domain type (e.g., "public", "custom", "premium")
        """
        params: Dict[str, Any] = {}
        if email:
            params["email"] = email
        if domain:
            params["domain"] = domain
        if domain_type:
            params["domain_type"] = domain_type

        data = self._make_request("POST", "/v1/emails", params=params)

        return EmailAddress.from_json(data)

    def list_domains(self) -> List[Domain]:
        """
        Get a list of available email domains.

        Returns:
            List[Domain]: Available domains
        """
        data = self._make_request("GET", "/v1/domains")

        return [Domain.from_json(domain) for domain in data["domains"]]

    def list_email_messages(
        self, email: str,
    ) -> List[EmailMessage]:
        data = self._make_request("GET", f"/v1/emails/{email}/messages")

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
        self._make_request("DELETE", f"/v1/messages/{message_id}")
        return True

    def get_rate_limit(self) -> RateLimit:
        """
        Get current rate limit information.

        Returns:
            RateLimit: Current rate limit status, or None if not available
        """
        # Make a lightweight request to get fresh rate limit info
        self._make_request("GET", "/v1/rate-limit")
        return self._last_rate_limit

    @property
    def last_rate_limit(self) -> Optional[RateLimit]:
        """Get the last known rate limit information."""
        return self._last_rate_limit

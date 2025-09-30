"""Temp Mail API client implementation."""

import typing
from typing import Optional, List, Dict, Any, overload, Literal
from urllib.parse import urljoin
import httpx

from . import __version__
from .models import (
    RateLimit,
    Domain,
    DomainType,
    EmailAddress,
    EmailMessage,
    APIErrorResponse,
)
from .exceptions import (
    TempMailError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
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

        self.client = httpx.Client(
            headers={
                "X-API-Key": api_key,
                "Content-Type": "application/json",
                "User-Agent": f"temp-mail-python/{__version__}",
            },
            timeout=timeout,
        )

        self._last_rate_limit: Optional[RateLimit] = None

    @overload
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        return_content: Literal[True] = ...,
        update_rate_limit: bool = True,
    ) -> bytes: ...

    @overload
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        return_content: Literal[False] = ...,
        update_rate_limit: bool = True,
    ) -> Dict[str, Any]: ...

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        return_content: bool = False,
        update_rate_limit: bool = True,
    ) -> typing.Union[Dict[str, Any], bytes]:
        """
        Make an HTTP request to the API.
        :param method: HTTP method (GET, POST, DELETE, etc.)
        :param endpoint: API endpoint (e.g., "/v1/emails")
        :param params: Query parameters
        :param json_data: JSON body for POST/PUT requests
        :param return_content: If True, return raw response content instead of JSON
        """
        url = urljoin(self.base_url, endpoint)

        try:
            response = self.client.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
            )

            if 200 <= response.status_code < 300:
                if update_rate_limit:
                    self._update_rate_limit_from_headers(response.headers)
                if return_content:
                    return response.content
                return response.json()
            else:
                api_response: APIErrorResponse = APIErrorResponse.from_json(
                    response.json()
                )
                if api_response.is_api_key_error():
                    raise AuthenticationError(api_response.detail)
                elif api_response.is_rate_limit_error():
                    raise RateLimitError(api_response.detail)
                elif api_response.is_validation_error():
                    raise ValidationError(api_response.detail)
                else:
                    raise TempMailError(api_response.detail)
        except httpx.RequestError as e:
            raise TempMailError(f"Request failed: {str(e)}")

    def _update_rate_limit_from_headers(self, headers: Any) -> None:
        """Update rate limit info from response headers."""
        self._last_rate_limit = RateLimit(
            limit=int(headers["X-Ratelimit-Limit"]),
            remaining=int(headers["X-Ratelimit-Remaining"]),
            reset=int(headers["X-Ratelimit-Reset"]),
            used=int(headers["X-Ratelimit-Used"]),
        )

    def create_email(
        self,
        email: Optional[str] = None,
        domain: Optional[str] = None,
        domain_type: Optional[DomainType] = None,
    ) -> EmailAddress:
        """
        Create a new temporary email address.
        :param email: Optional specific email address to create
        :param domain: Optional domain to use
        :param domain_type: an Optional domain type
        """
        json_data: Dict[str, Any] = {}
        if email:
            json_data["email"] = email
        if domain:
            json_data["domain"] = domain
        if domain_type:
            json_data["domain_type"] = domain_type.value

        data = self._make_request(
            "POST",
            "/v1/emails",
            json_data=json_data if json_data else None,
            return_content=False,
        )

        return EmailAddress.from_json(data)

    def list_domains(self) -> List[Domain]:
        """
        Get a list of available email domains.

        Returns:
            List[Domain]: Available domains
        """
        data = self._make_request("GET", "/v1/domains", return_content=False)

        return [Domain.from_json(domain) for domain in data["domains"]]

    def list_email_messages(
        self,
        email: str,
    ) -> List[EmailMessage]:
        """Get all messages for a specific email address."""
        data = self._make_request(
            "GET", f"/v1/emails/{email}/messages", return_content=False
        )

        messages = []
        for msg_data in data["messages"]:
            messages.append(EmailMessage.from_json(msg_data))

        return messages

    def get_message(self, message_id: str) -> EmailMessage:
        """Get a specific message by ID."""
        data = self._make_request(
            "GET", f"/v1/messages/{message_id}", return_content=False
        )
        return EmailMessage.from_json(data)

    def delete_message(self, message_id: str) -> None:
        """Delete a specific message by ID."""
        self._make_request("DELETE", f"/v1/messages/{message_id}", return_content=False)

    def delete_email(self, email: str) -> None:
        """Delete an email address and all its messages."""
        self._make_request("DELETE", f"/v1/emails/{email}", return_content=False)

    def get_message_source_code(self, message_id: str) -> str:
        """Get the raw source code of a message."""
        data = self._make_request(
            "GET", f"/v1/messages/{message_id}/source_code", return_content=False
        )
        return data["data"]

    def download_attachment(self, attachment_id: str) -> bytes:
        """Download an attachment by ID."""
        content: bytes = self._make_request(
            "GET", f"/v1/attachments/{attachment_id}", return_content=True
        )
        return content

    def get_rate_limit(self) -> RateLimit:
        """
        Get current rate limit information.
        :return: RateLimit object
        """
        data = self._make_request(
            "GET", "/v1/rate_limit", return_content=False, update_rate_limit=False
        )
        rate_limit: RateLimit = RateLimit.from_json(data)
        # Also update the last known rate limit since this method doesn't use headers
        self._last_rate_limit = rate_limit
        return rate_limit

    @property
    def last_rate_limit(self) -> Optional[RateLimit]:
        """
        Get the last known rate limit information.
        It will be None if no requests have been made yet.
        """
        return self._last_rate_limit

    def close(self) -> None:
        """Close the underlying HTTPX client.

        The client will *not* be usable after this.
        """
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

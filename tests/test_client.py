"""Tests for the TempMailClient."""

import typing
import pytest

from unittest.mock import Mock, patch
from tempmail import (
    TempMailClient,
    EmailAddress,
    Domain,
    EmailMessage,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    APIError,
)
from tempmail.models import DomainType


class TestTempMailClient:
    _rate_limit_headers: typing.Dict[str, str] = {
        "X-Ratelimit-Limit": "100",
        "X-Ratelimit-Remaining": "99",
        "X-Ratelimit-Reset": "2073044847",
        "X-Ratelimit-Used": "1",
    }

    def test_client_initialization(self) -> None:
        """Test client initialization with API key."""
        client = TempMailClient("test-api-key")
        assert client.api_key == "test-api-key"
        assert client.session.headers["X-API-Key"] == "test-api-key"

    def test_client_initialization_with_custom_params(self) -> None:
        """Test client initialization with custom parameters."""
        client = TempMailClient(
            "test-api-key", base_url="https://custom.api.com", timeout=60
        )
        assert client.base_url == "https://custom.api.com"
        assert client.timeout == 60

    @patch("tempmail.client.requests.Session.request")
    def test_create_email_success(self, mock_request) -> None:
        """Test successful email creation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"email": "test@example.com", "ttl": 86400}
        mock_response.headers = self._rate_limit_headers
        mock_request.return_value = mock_response

        client: TempMailClient = TempMailClient("test-api-key")
        email: EmailAddress = client.create_email()
        assert email == EmailAddress(email="test@example.com", ttl=86400)

    @patch("tempmail.client.requests.Session.request")
    def test_create_email_with_options(self, mock_request):
        """Test email creation with options."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"email": "custom@mydomain.com", "ttl": 86400}
        mock_response.headers = self._rate_limit_headers
        mock_request.return_value = mock_response

        client: TempMailClient = TempMailClient("test-api-key")
        email: EmailAddress = client.create_email(domain="mydomain.com")
        assert email == EmailAddress(email="custom@mydomain.com", ttl=86400)

        # Verify request was made with correct parameters
        mock_request.assert_called_once_with(
            method="POST",
            url="https://api.temp-mail.io/v1/emails",
            params=None,
            json={"domain": "mydomain.com"},
            timeout=30,
        )

    @patch("tempmail.client.requests.Session.request")
    def test_list_domains_success(self, mock_request) -> None:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "domains": [
                {
                    "name": "example.com",
                    "type": "public",
                },
                {
                    "name": "test.org",
                    "type": "custom",
                },
                {
                    "name": "example.io",
                    "type": "premium",
                },
            ]
        }
        mock_response.headers = self._rate_limit_headers
        mock_request.return_value = mock_response

        client: TempMailClient = TempMailClient("test-api-key")
        domains: typing.List[Domain] = client.list_domains()
        assert domains == [
            Domain(name="example.com", type=DomainType.PUBLIC),
            Domain(name="test.org", type=DomainType.CUSTOM),
            Domain(name="example.io", type=DomainType.PREMIUM),
        ]

    @patch("tempmail.client.requests.Session.request")
    def test_list_email_messages_success(self, mock_request):
        """Test successful message listing."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "messages": [
                {
                    "id": "msg1",
                    "from": "sender@example.com",
                    "to": "test@temp.io",
                    "cc": ["cc@example.com"],
                    "subject": "Test Subject",
                    "body_text": "Test body",
                    "body_html": "<p>Test body</p>",
                    "created_at": "2023-01-01T00:00:00Z",
                    "attachments": [],
                }
            ]
        }
        mock_response.headers = self._rate_limit_headers
        mock_request.return_value = mock_response

        client = TempMailClient("test-api-key")
        messages = client.list_email_messages("test@temp.io")

        assert len(messages) == 1
        message = messages[0]
        assert isinstance(message, EmailMessage)
        assert message.id == "msg1"
        assert message.from_addr == "sender@example.com"
        assert message.to_addr == "test@temp.io"
        assert message.cc == ["cc@example.com"]
        assert message.subject == "Test Subject"
        assert message.body_text == "Test body"
        assert message.body_html == "<p>Test body</p>"
        assert message.created_at == "2023-01-01T00:00:00Z"
        assert message.attachments == []

    @patch("tempmail.client.requests.Session.request")
    def test_list_email_messages_empty(self, mock_request):
        """Test message listing with empty response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"messages": []}
        mock_response.headers = self._rate_limit_headers
        mock_request.return_value = mock_response

        client = TempMailClient("test-api-key")
        messages = client.list_email_messages("test@temp.io")

        assert len(messages) == 0
        # Verify the request was made to correct endpoint
        mock_request.assert_called_once_with(
            method="GET",
            url="https://api.temp-mail.io/v1/emails/test@temp.io/messages",
            params=None,
            json=None,
            timeout=30,
        )

    @patch("tempmail.client.requests.Session.request")
    def test_get_message_success(self, mock_request):
        """Test successful single message retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "msg1",
            "from": "sender@example.com",
            "to": "test@temp.io",
            "cc": [],
            "subject": "Test Subject",
            "body_text": "Test body",
            "body_html": "<p>Test body</p>",
            "created_at": "2023-01-01T00:00:00Z",
            "attachments": [],
        }
        mock_response.headers = self._rate_limit_headers
        mock_request.return_value = mock_response

        client = TempMailClient("test-api-key")
        message = client.get_message("msg1")

        assert isinstance(message, EmailMessage)
        assert message.id == "msg1"
        assert message.from_addr == "sender@example.com"
        assert message.to_addr == "test@temp.io"
        assert message.subject == "Test Subject"

        # Verify correct endpoint was called
        mock_request.assert_called_once_with(
            method="GET",
            url="https://api.temp-mail.io/v1/messages/msg1",
            params=None,
            json=None,
            timeout=30,
        )

    @patch("tempmail.client.requests.Session.request")
    def test_delete_message_success(self, mock_request):
        """Test successful message deletion."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_response.headers = self._rate_limit_headers
        mock_request.return_value = mock_response

        client = TempMailClient("test-api-key")
        result = client.delete_message("msg123")

        assert result is True

        # Verify correct endpoint was called
        mock_request.assert_called_once_with(
            method="DELETE",
            url="https://api.temp-mail.io/v1/messages/msg123",
            params=None,
            json=None,
            timeout=30,
        )

    @patch("tempmail.client.requests.Session.request")
    def test_delete_email_success(self, mock_request):
        """Test successful email deletion."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_response.headers = self._rate_limit_headers
        mock_request.return_value = mock_response

        client = TempMailClient("test-api-key")
        result = client.delete_email("test@temp.io")

        assert result is True

        # Verify correct endpoint was called
        mock_request.assert_called_once_with(
            method="DELETE",
            url="https://api.temp-mail.io/v1/emails/test@temp.io",
            params=None,
            json=None,
            timeout=30,
        )

    @patch("tempmail.client.requests.Session.request")
    def test_get_message_source_code_success(self, mock_request):
        """Test successful message source code retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": "Received: from example.com...\r\nSubject: Test Subject\r\n\r\nTest body"
        }
        mock_response.headers = self._rate_limit_headers
        mock_request.return_value = mock_response

        client = TempMailClient("test-api-key")
        source_code = client.get_message_source_code("msg1")

        assert "Received: from example.com" in source_code
        assert "Subject: Test Subject" in source_code

        # Verify correct endpoint was called
        mock_request.assert_called_once_with(
            method="GET",
            url="https://api.temp-mail.io/v1/messages/msg1/source_code",
            params=None,
            json=None,
            timeout=30,
        )

    @patch("tempmail.client.requests.Session.request")
    def test_download_attachment_success(self, mock_request):
        """Test successful attachment download."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"attachment content here"
        mock_response.headers = self._rate_limit_headers
        mock_request.return_value = mock_response

        client = TempMailClient("test-api-key")
        content = client.download_attachment("attachment1")

        assert content == b"attachment content here"

        # Verify correct endpoint was called
        mock_request.assert_called_once_with(
            method="GET",
            url="https://api.temp-mail.io/v1/attachments/attachment1",
            timeout=30,
        )

    @patch("tempmail.client.requests.Session.request")
    def test_authentication_error(self, mock_request):
        """Test authentication error handling."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.content = b""
        mock_response.headers = {}
        mock_request.return_value = mock_response

        client = TempMailClient("test-api-key")
        with pytest.raises(AuthenticationError, match="Invalid API key"):
            client.create_email()

    @patch("tempmail.client.requests.Session.request")
    def test_rate_limit_error(self, mock_request):
        """Test rate limit error handling."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.content = b""
        mock_response.headers = {}
        mock_request.return_value = mock_response

        client = TempMailClient("test-api-key")
        with pytest.raises(RateLimitError, match="Rate limit exceeded"):
            client.create_email()

    @patch("tempmail.client.requests.Session.request")
    def test_validation_error(self, mock_request):
        """Test validation error handling."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.content = b'{"error": {"detail": "Invalid domain"}}'
        mock_response.json.return_value = {"error": {"detail": "Invalid domain"}}
        mock_response.headers = {}
        mock_request.return_value = mock_response

        client = TempMailClient("test-api-key")
        with pytest.raises(ValidationError, match="Invalid domain"):
            client.create_email()

    @patch("tempmail.client.requests.Session.request")
    def test_api_error(self, mock_request):
        """Test generic API error handling."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.content = b'{"error": {"detail": "Internal server error"}}'
        mock_response.json.return_value = {"error": {"detail": "Internal server error"}}
        mock_response.headers = {}
        mock_request.return_value = mock_response

        client = TempMailClient("test-api-key")
        with pytest.raises(APIError) as exc_info:
            client.create_email()

        assert exc_info.value.status_code == 500
        assert "Internal server error" in str(exc_info.value)

    @patch("tempmail.client.requests.Session.request")
    def test_get_rate_limit_success(self, mock_request):
        """Test successful rate limit retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "limit": 100,
            "remaining": 95,
            "used": 5,
            "reset": 1640995200,
        }
        mock_response.headers = {
            "X-RateLimit-Limit": "100",
            "X-RateLimit-Remaining": "95",
            "X-RateLimit-Reset": "1640995200",
        }
        mock_request.return_value = mock_response

        client = TempMailClient("test-api-key")
        rate_limit_data = client.get_rate_limit()

        assert rate_limit_data.limit == 100
        assert rate_limit_data.remaining == 95
        assert rate_limit_data.used == 5
        assert rate_limit_data.reset == 1640995200

        # Verify the last rate limit was updated from headers
        assert client.last_rate_limit is not None
        assert client.last_rate_limit.limit == 100
        assert client.last_rate_limit.remaining == 95
        assert client.last_rate_limit.reset == 1640995200

    @patch("tempmail.client.requests.Session.request")
    def test_request_exception(self, mock_request):
        """Test handling of request exceptions."""
        from requests.exceptions import ConnectionError
        from tempmail.exceptions import TempMailError

        mock_request.side_effect = ConnectionError("Connection failed")

        client = TempMailClient("test-api-key")
        with pytest.raises(TempMailError, match="Request failed"):
            client.list_domains()

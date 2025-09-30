import datetime
import typing
import pytest

from httpx import TimeoutException
from unittest.mock import Mock, patch
from tempmail import (
    TempMailClient,
    EmailAddress,
    Domain,
    EmailMessage,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    TempMailError,
)
from httpx import ConnectError
from tempmail.models import DomainType, RateLimit, Attachment


class TestTempMailClient:
    _rate_limit_headers: typing.Dict[str, str] = {
        "X-Ratelimit-Limit": "100",
        "X-Ratelimit-Remaining": "99",
        "X-Ratelimit-Reset": "2073044847",
        "X-Ratelimit-Used": "1",
    }

    def test_client_initialization(self) -> None:
        client = TempMailClient("test-api-key")
        assert client.api_key == "test-api-key"
        assert client.client.headers["X-API-Key"] == "test-api-key"

    def test_client_initialization_with_custom_params(self) -> None:
        client = TempMailClient(
            "test-api-key", base_url="https://custom.api.com", timeout=60
        )
        assert client.base_url == "https://custom.api.com"
        assert client.timeout == 60

    @patch("tempmail.client.httpx.Client.request")
    def test_create_email_success(self, mock_request) -> None:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"email": "test@example.com", "ttl": 86400}
        mock_response.headers = self._rate_limit_headers
        mock_request.return_value = mock_response

        client: TempMailClient = TempMailClient("test-api-key")
        email: EmailAddress = client.create_email()
        assert email == EmailAddress(email="test@example.com", ttl=86400)

    @patch("tempmail.client.httpx.Client.request")
    def test_create_email_premium_domain_type(self, mock_request) -> None:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"email": "test@example.com", "ttl": 86400}
        mock_response.headers = self._rate_limit_headers
        mock_request.return_value = mock_response

        client: TempMailClient = TempMailClient("test-api-key")
        email: EmailAddress = client.create_email(domain_type=DomainType.PREMIUM)
        assert email == EmailAddress(email="test@example.com", ttl=86400)

        mock_request.assert_called_once_with(
            method="POST",
            url="https://api.temp-mail.io/v1/emails",
            params=None,
            json={"domain_type": "premium"},
        )

    @patch("tempmail.client.httpx.Client.request")
    def test_create_email_with_options(self, mock_request):
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
        )

    @patch("tempmail.client.httpx.Client.request")
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

    @patch("tempmail.client.httpx.Client.request")
    def test_list_email_messages_success(self, mock_request):
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
                    "attachments": [
                        {
                            "id": "att1",
                            "name": "file.txt",
                            "size": 1234,
                        },
                        {
                            "id": "att2",
                            "name": "image.png",
                            "size": 4567,
                        },
                    ],
                }
            ]
        }
        mock_response.headers = self._rate_limit_headers
        mock_request.return_value = mock_response

        client = TempMailClient("test-api-key")
        messages: typing.List[EmailMessage] = client.list_email_messages("test@temp.io")

        assert len(messages) == 1
        assert messages[0] == EmailMessage(
            id="msg1",
            from_addr="sender@example.com",
            to_addr="test@temp.io",
            cc=["cc@example.com"],
            subject="Test Subject",
            body_text="Test body",
            body_html="<p>Test body</p>",
            created_at=datetime.datetime(
                2023, 1, 1, 0, 0, tzinfo=datetime.timezone.utc
            ),
            attachments=[
                Attachment(id="att1", name="file.txt", size=1234),
                Attachment(id="att2", name="image.png", size=4567),
            ],
        )

    @patch("tempmail.client.httpx.Client.request")
    def test_list_email_messages_no_attachments(self, mock_request):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "messages": [
                {
                    "id": "msg1",
                    "from": "<sender@example.com>",
                    "to": "test@temp.io",
                    "cc": ["cc@example.com"],
                    "subject": "Test Subject",
                    "body_text": "Test body",
                    "body_html": "<p>Test body</p>",
                    "created_at": "2023-01-01T00:00:00Z",
                    "attachments": None,
                }
            ]
        }
        mock_response.headers = self._rate_limit_headers
        mock_request.return_value = mock_response

        client = TempMailClient("test-api-key")
        messages: typing.List[EmailMessage] = client.list_email_messages("test@temp.io")

        assert len(messages) == 1
        assert messages[0] == EmailMessage(
            id="msg1",
            from_addr="<sender@example.com>",
            to_addr="test@temp.io",
            cc=["cc@example.com"],
            subject="Test Subject",
            body_text="Test body",
            body_html="<p>Test body</p>",
            created_at=datetime.datetime(
                2023, 1, 1, 0, 0, tzinfo=datetime.timezone.utc
            ),
            attachments=[],
        )

    @patch("tempmail.client.httpx.Client.request")
    def test_list_email_messages_empty(self, mock_request):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"messages": []}
        mock_response.headers = self._rate_limit_headers
        mock_request.return_value = mock_response

        client = TempMailClient("test-api-key")
        messages = client.list_email_messages("test@temp.io")

        assert len(messages) == 0
        mock_request.assert_called_once_with(
            method="GET",
            url="https://api.temp-mail.io/v1/emails/test@temp.io/messages",
            params=None,
            json=None,
        )

    @patch("tempmail.client.httpx.Client.request")
    def test_get_message_success(self, mock_request):
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

        assert message == EmailMessage(
            id="msg1",
            from_addr="sender@example.com",
            to_addr="test@temp.io",
            cc=[],
            subject="Test Subject",
            body_text="Test body",
            body_html="<p>Test body</p>",
            created_at=datetime.datetime(
                2023, 1, 1, 0, 0, tzinfo=datetime.timezone.utc
            ),
            attachments=[],
        )
        mock_request.assert_called_once_with(
            method="GET",
            url="https://api.temp-mail.io/v1/messages/msg1",
            params=None,
            json=None,
        )

    @patch("tempmail.client.httpx.Client.request")
    def test_delete_message_success(self, mock_request):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_response.headers = self._rate_limit_headers
        mock_request.return_value = mock_response

        client = TempMailClient("test-api-key")
        client.delete_message("msg123")

        mock_request.assert_called_once_with(
            method="DELETE",
            url="https://api.temp-mail.io/v1/messages/msg123",
            params=None,
            json=None,
        )

    @patch("tempmail.client.httpx.Client.request")
    def test_delete_email_success(self, mock_request):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_response.headers = self._rate_limit_headers
        mock_request.return_value = mock_response

        client = TempMailClient("test-api-key")
        client.delete_email("test@temp.io")

        mock_request.assert_called_once_with(
            method="DELETE",
            url="https://api.temp-mail.io/v1/emails/test@temp.io",
            params=None,
            json=None,
        )

    @patch("tempmail.client.httpx.Client.request")
    def test_get_message_source_code_success(self, mock_request):
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

        mock_request.assert_called_once_with(
            method="GET",
            url="https://api.temp-mail.io/v1/messages/msg1/source_code",
            params=None,
            json=None,
        )

    @patch("tempmail.client.httpx.Client.request")
    def test_download_attachment_success(self, mock_request):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"attachment content here"
        mock_response.headers = self._rate_limit_headers
        mock_request.return_value = mock_response

        client = TempMailClient("test-api-key")
        content = client.download_attachment("attachment1")

        assert content == b"attachment content here"

        mock_request.assert_called_once_with(
            method="GET",
            url="https://api.temp-mail.io/v1/attachments/attachment1",
            params=None,
            json=None,
        )

    @patch("tempmail.client.httpx.Client.request")
    def test_authentication_error(self, mock_request):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": {
                "code": "api_key_invalid",
                "detail": "API token is invalid",
                "type": "request_error",
            },
            "meta": {"request_id": "01K510JMH7V5PTN1TNCW5HF9AE"},
        }
        mock_response.headers = {}
        mock_request.return_value = mock_response

        client = TempMailClient("test-api-key")
        with pytest.raises(AuthenticationError, match="API token is invalid"):
            client.create_email()

    @patch("tempmail.client.httpx.Client.request")
    def test_rate_limit_error(self, mock_request):
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = {
            "error": {
                "code": "rate_limited",
                "detail": "You have reached your rate limit. Please try again later.",
                "type": "request_error",
            },
            "meta": {"request_id": "01K510JMH7V5PTN1TNCW5HF9AE"},
        }
        mock_response.headers = {}
        mock_request.return_value = mock_response

        client = TempMailClient("test-api-key")
        with pytest.raises(
            RateLimitError,
            match="You have reached your rate limit. Please try again later.",
        ):
            client.create_email()

    @patch("tempmail.client.httpx.Client.request")
    def test_validation_error(self, mock_request):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": {
                "code": "validation_error",
                "detail": "Invalid domain name",
                "type": "request_error",
            },
            "meta": {"request_id": "01K510JMH7V5PTN1TNCW5HF9AE"},
        }
        mock_response.headers = {}
        mock_request.return_value = mock_response

        client = TempMailClient("test-api-key")
        with pytest.raises(ValidationError, match="Invalid domain name"):
            client.create_email(domain="invalid_domain")

    @patch("tempmail.client.httpx.Client.request")
    def test_api_error(self, mock_request):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {
            "error": {
                "code": "internal_error",
                "detail": "Internal server error",
                "type": "api_error",
            },
            "meta": {"request_id": "01K510JMH7V5PTN1TNCW5HF9AE"},
        }
        mock_response.headers = {}
        mock_request.return_value = mock_response

        client = TempMailClient("test-api-key")
        with pytest.raises(TempMailError, match="Internal server error"):
            client.create_email()

    @patch("tempmail.client.httpx.Client.request")
    def test_get_rate_limit_success(self, mock_request):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "limit": 100,
            "remaining": 95,
            "used": 5,
            "reset": 1640995200,
        }
        mock_response.headers = {
            "X-Ratelimit-Limit": "100",
            "X-Ratelimit-Remaining": "95",
            "X-Ratelimit-Reset": "1640995200",
            "X-Ratelimit-Used": "5",
        }
        mock_request.return_value = mock_response

        client = TempMailClient("test-api-key")
        rate_limit_data = client.get_rate_limit()

        assert rate_limit_data == RateLimit(
            limit=100, remaining=95, used=5, reset=1640995200
        )

        # Verify the last rate limit was updated from headers
        assert client.last_rate_limit is not None
        assert client.last_rate_limit == RateLimit(
            limit=100, remaining=95, used=5, reset=1640995200
        )

    @patch("tempmail.client.httpx.Client.request")
    def test_request_exception(self, mock_request):
        mock_request.side_effect = ConnectError("Connection failed")

        client = TempMailClient("test-api-key")
        with pytest.raises(TempMailError, match="Request failed"):
            client.list_domains()

    @patch("tempmail.client.httpx.Client.request")
    def test_create_email_with_specific_email(self, mock_request):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "email": "specific@example.com",
            "ttl": 86400,
        }
        mock_response.headers = self._rate_limit_headers
        mock_request.return_value = mock_response

        client = TempMailClient("test-api-key")
        email = client.create_email(email="specific@example.com")
        assert email == EmailAddress(email="specific@example.com", ttl=86400)

        mock_request.assert_called_once_with(
            method="POST",
            url="https://api.temp-mail.io/v1/emails",
            params=None,
            json={"email": "specific@example.com"},
        )

    def test_context_manager(self):
        with patch("tempmail.client.httpx.Client.close") as mock_close:
            with TempMailClient("test-api-key") as client:
                assert isinstance(client, TempMailClient)
            mock_close.assert_called_once()

    def test_close_method(self):
        with patch("tempmail.client.httpx.Client.close") as mock_close:
            client = TempMailClient("test-api-key")
            client.close()
            mock_close.assert_called_once()

    @patch("tempmail.client.httpx.Client.request")
    def test_create_email_with_empty_json_data(self, mock_request):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"email": "random@example.com", "ttl": 86400}
        mock_response.headers = self._rate_limit_headers
        mock_request.return_value = mock_response

        client = TempMailClient("test-api-key")
        email = client.create_email()
        assert email == EmailAddress(email="random@example.com", ttl=86400)

        mock_request.assert_called_once_with(
            method="POST",
            url="https://api.temp-mail.io/v1/emails",
            params=None,
            json=None,
        )

    def test_last_rate_limit_initial_state(self):
        client = TempMailClient("test-api-key")
        assert client.last_rate_limit is None

    @patch("tempmail.client.httpx.Client.request")
    def test_error_response_with_different_status_codes(self, mock_request):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            "error": {
                "code": "not_found",
                "detail": "Message not found",
                "type": "request_error",
            },
            "meta": {"request_id": "123"},
        }
        mock_response.headers = {}
        mock_request.return_value = mock_response

        client = TempMailClient("test-api-key")
        with pytest.raises(TempMailError, match="Message not found"):
            client.get_message("non-existent-id")

    def test_httpx_client_timeout_configuration(self):
        client = TempMailClient("test-api-key", timeout=60)
        # httpx.Client.timeout returns a Timeout object
        assert client.client.timeout.read == 60
        assert client.client.timeout.connect == 60

    @patch("tempmail.client.httpx.Client.request")
    def test_httpx_specific_error_handling(self, mock_request):
        mock_request.side_effect = TimeoutException("Request timeout")

        client = TempMailClient("test-api-key")
        with pytest.raises(TempMailError, match="Request failed"):
            client.list_domains()

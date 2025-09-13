"""Tests for the TempMailClient."""

import typing

from unittest.mock import Mock, patch
from tempmail import (
    TempMailClient,
    EmailAddress,
    Domain,
)
from tempmail.models import DomainType


class TestTempMailClient:
    _rate_limit_headers: typing.Dict[str, str] = {
        "X-RateLimit-Limit": "100",
        "X-RateLimit-Remaining": "99",
        "X-RateLimit-Reset": "2073044847",
        "X-RateLimit-Used": "1",
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
            params={"domain": "mydomain.com"},
            json=None,
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

    #
    # @patch('tempmail.client.requests.Session.request')
    # def test_list_email_messages_success(self, mock_request):
    #     """Test successful message listing."""
    #     mock_response = Mock()
    #     mock_response.status_code = 200
    #     mock_response.json.return_value = {
    #         "messages": [
    #             {
    #                 "id": "msg1",
    #                 "from": "sender@example.com",
    #                 "to": "test@temp.io",
    #                 "subject": "Test Subject",
    #                 "body_text": "Test body",
    #                 "body_html": "<p>Test body</p>",
    #                 "created_at": "2023-01-01T00:00:00Z"
    #             }
    #         ]
    #     }
    #     mock_response.headers = {}
    #     mock_request.return_value = mock_response
    #
    #     client = TempMailClient("test-api-key")
    #     messages = client.list_email_messages("test@temp.io")
    #
    #     assert len(messages) == 1
    #     message = messages[0]
    #     assert isinstance(message, EmailMessage)
    #     assert message.id == "msg1"
    #     assert message.from_addr == "sender@example.com"
    #     assert message.to_addr == "test@temp.io"
    #     assert message.subject == "Test Subject"
    #     assert message.body_text == "Test body"
    #     assert message.body_html == "<p>Test body</p>"
    #
    # @patch('tempmail.client.requests.Session.request')
    # def test_list_email_messages_with_options(self, mock_request):
    #     """Test message listing with options."""
    #     mock_response = Mock()
    #     mock_response.status_code = 200
    #     mock_response.json.return_value = {"messages": []}
    #     mock_response.headers = {}
    #     mock_request.return_value = mock_response
    #
    #     client = TempMailClient("test-api-key")
    #     options = ListMessagesOptions(limit=10, offset=5)
    #     client.list_email_messages("test@temp.io", options)
    #
    #     # Verify the request was made with correct parameters
    #     mock_request.assert_called_once()
    #     call_args = mock_request.call_args
    #     expected_params = {"email": "test@temp.io", "limit": 10, "offset": 5}
    #     assert call_args[1]['params'] == expected_params
    #
    # def test_list_email_messages_no_email(self):
    #     """Test message listing fails without email."""
    #     client = TempMailClient("test-api-key")
    #     with pytest.raises(ValidationError, match="Email address is required"):
    #         client.list_email_messages("")
    #
    # @patch('tempmail.client.requests.Session.request')
    # def test_delete_message_success(self, mock_request):
    #     """Test successful message deletion."""
    #     mock_response = Mock()
    #     mock_response.status_code = 200
    #     mock_response.json.return_value = {}
    #     mock_response.headers = {}
    #     mock_request.return_value = mock_response
    #
    #     client = TempMailClient("test-api-key")
    #     result = client.delete_message("msg123")
    #
    #     assert result is True
    #
    #     # Verify correct endpoint was called
    #     mock_request.assert_called_once()
    #     call_args = mock_request.call_args
    #     assert "/messages/msg123" in call_args[1]['url']
    #     assert call_args[1]['method'] == "DELETE"
    #
    # def test_delete_message_no_id(self):
    #     """Test message deletion fails without message ID."""
    #     client = TempMailClient("test-api-key")
    #     with pytest.raises(ValidationError, match="Message ID is required"):
    #         client.delete_message("")
    #
    # @patch('tempmail.client.requests.Session.request')
    # def test_authentication_error(self, mock_request):
    #     """Test authentication error handling."""
    #     mock_response = Mock()
    #     mock_response.status_code = 401
    #     mock_response.content = b''
    #     mock_response.headers = {}
    #     mock_request.return_value = mock_response
    #
    #     client = TempMailClient("test-api-key")
    #     with pytest.raises(AuthenticationError, match="Invalid API key"):
    #         client.create_email()
    #
    # @patch('tempmail.client.requests.Session.request')
    # def test_rate_limit_error(self, mock_request):
    #     """Test rate limit error handling."""
    #     mock_response = Mock()
    #     mock_response.status_code = 429
    #     mock_response.content = b''
    #     mock_response.headers = {}
    #     mock_request.return_value = mock_response
    #
    #     client = TempMailClient("test-api-key")
    #     with pytest.raises(RateLimitError, match="Rate limit exceeded"):
    #         client.create_email()
    #
    # @patch('tempmail.client.requests.Session.request')
    # def test_validation_error(self, mock_request):
    #     """Test validation error handling."""
    #     mock_response = Mock()
    #     mock_response.status_code = 400
    #     mock_response.content = b'{"message": "Invalid domain"}'
    #     mock_response.json.return_value = {"message": "Invalid domain"}
    #     mock_response.headers = {}
    #     mock_request.return_value = mock_response
    #
    #     client = TempMailClient("test-api-key")
    #     with pytest.raises(ValidationError, match="Invalid domain"):
    #         client.create_email()
    #
    # @patch('tempmail.client.requests.Session.request')
    # def test_api_error(self, mock_request):
    #     """Test generic API error handling."""
    #     mock_response = Mock()
    #     mock_response.status_code = 500
    #     mock_response.content = b'{"message": "Internal server error"}'
    #     mock_response.json.return_value = {"message": "Internal server error"}
    #     mock_response.headers = {}
    #     mock_request.return_value = mock_response
    #
    #     client = TempMailClient("test-api-key")
    #     with pytest.raises(APIError) as exc_info:
    #         client.create_email()
    #
    #     assert exc_info.value.status_code == 500
    #     assert "Internal server error" in str(exc_info.value)
    #
    # @patch('tempmail.client.requests.Session.request')
    # def test_rate_limit_headers(self, mock_request):
    #     """Test rate limit information from headers."""
    #     mock_response = Mock()
    #     mock_response.status_code = 200
    #     mock_response.json.return_value = {}
    #     mock_response.headers = {
    #         "X-RateLimit-Limit": "100",
    #         "X-RateLimit-Remaining": "95",
    #         "X-RateLimit-Reset": "1640995200"
    #     }
    #     mock_request.return_value = mock_response
    #
    #     client = TempMailClient("test-api-key")
    #     rate_limit = client.get_rate_limit()
    #
    #     assert rate_limit is not None
    #     assert rate_limit.limit == 100
    #     assert rate_limit.remaining == 95
    #     assert rate_limit.reset == 1640995200
    #
    # @patch('tempmail.client.requests.Session.request')
    # def test_request_exception(self, mock_request):
    #     """Test handling of request exceptions."""
    #     from requests.exceptions import ConnectionError
    #     from tempmail.exceptions import TempMailError
    #
    #     mock_request.side_effect = ConnectionError("Connection failed")
    #
    #     client = TempMailClient("test-api-key")
    #     with pytest.raises(TempMailError, match="Request failed"):
    #         client.list_domains()

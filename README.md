# Temp Mail Python Library

Official Python library for the [Temp Mail API](https://temp-mail.io). Create temporary email addresses and receive emails programmatically.

## Installation

```bash
pip install temp-mail-io
```

## Quick Start

```python
from tempmail import TempMailClient

# Initialize the client
client = TempMailClient("your-api-key")

# Create a temporary email address
email = client.create_email()
print(f"Your temporary email: {email.email}")

# Check for messages
messages = client.list_email_messages(email.email)
for message in messages:
    print(f"From: {message.from_addr}")
    print(f"Subject: {message.subject}")
    print(f"Body: {message.body_text}")
```

## Features

- **Create temporary email addresses** - Generate disposable emails instantly
- **List available domains** - Get domains you can use for email creation
- **Receive emails** - Fetch messages sent to your temporary addresses
- **Delete messages** - Clean up messages when done
- **Rate limit monitoring** - Track your API usage
- **Error handling** - Comprehensive exception handling
- **Type hints** - Full typing support for better development experience

## API Reference

### TempMailClient

The main client class for interacting with the Temp Mail API.

```python
from tempmail import TempMailClient

# Basic initialization
client = TempMailClient("your-api-key")

# With custom parameters
client = TempMailClient(
    "your-api-key",
    base_url="https://api.temp-mail.io",
    timeout=30
)
```

### Creating Email Addresses

```python
from tempmail import CreateEmailOptions

# Create random email
email = client.create_email()

# Create with specific domain and prefix
options = CreateEmailOptions(domain="example.com", prefix="mytest")
email = client.create_email(options)
```

### Listing Domains

```python
domains = client.list_domains()
for domain in domains:
    print(domain.domain)
```

### Managing Messages

```python
from tempmail import ListMessagesOptions

# List all messages for an email
messages = client.list_email_messages("test@example.com")

# List with pagination
options = ListMessagesOptions(limit=10, offset=0)
messages = client.list_email_messages("test@example.com", options)

# Delete a message
client.delete_message("message-id")
```

### Rate Limiting

```python
# Get current rate limit status
rate_limit = client.get_rate_limit()
if rate_limit:
    print(f"Remaining requests: {rate_limit.remaining}")
    print(f"Reset time: {rate_limit.reset}")
```

## Error Handling

The library provides specific exception types for different error conditions:

```python
from tempmail import (
    TempMailError,           # Base exception
    AuthenticationError,     # Invalid API key
    RateLimitError,         # Rate limit exceeded
    ValidationError,        # Invalid parameters
    APIError               # Server errors
)

try:
    client = TempMailClient("invalid-key")
    email = client.create_email()
except AuthenticationError:
    print("Invalid API key")
except RateLimitError:
    print("Rate limit exceeded")
except ValidationError as e:
    print(f"Invalid parameters: {e}")
except APIError as e:
    print(f"API error: {e.status_code} - {e}")
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/temp-mail-io/temp-mail-python
cd temp-mail-python

# Install in development mode
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black tempmail/ tests/
isort tempmail/ tests/
```

### Type Checking

```bash
mypy tempmail/
```

## Examples

See the [examples/](examples/) directory for more detailed usage examples.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Links

- [Temp Mail API Documentation](https://docs.temp-mail.io)
- [GitHub Repository](https://github.com/temp-mail-io/temp-mail-python)
- [PyPI Package](https://pypi.org/project/temp-mail-io/)

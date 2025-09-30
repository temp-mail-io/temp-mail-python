# Temp Mail Python Library

[![PyPI version](https://badge.fury.io/py/temp-mail.svg)](https://badge.fury.io/py/temp-mail)
[![Python Support](https://img.shields.io/pypi/pyversions/temp-mail.svg)](https://pypi.org/project/temp-mail/)
[![Test Status](https://github.com/temp-mail-io/temp-mail-python/workflows/Test/badge.svg)](https://github.com/temp-mail-io/temp-mail-python/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/temp-mail-io/temp-mail-python/branch/main/graph/badge.svg)](https://codecov.io/gh/temp-mail-io/temp-mail-python)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/temp-mail)](https://pepy.tech/project/temp-mail)

Official Python library for the [Temp Mail API](https://temp-mail.io). Create temporary email addresses and receive emails programmatically.

## Installation

```bash
pip install temp-mail
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
- **Get individual messages** - Retrieve specific messages by ID
- **Get message source code** - Access raw email source
- **Download attachments** - Download email attachments
- **Delete messages** - Clean up individual messages
- **Delete emails** - Remove email addresses and all their messages
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
# Create random email
email = client.create_email()

# Create with specific domain
email = client.create_email(domain="example.com")

# Create with specific email address
email = client.create_email(email="mytest@example.com")

# Create with domain type preference
from tempmail.models import DomainType
email = client.create_email(domain_type=DomainType.PREMIUM)
```

### Listing Domains

```python
domains = client.list_domains()
for domain in domains:
    print(f"Domain: {domain.name}, Type: {domain.type.value}")
```

### Managing Messages

```python
# List all messages for an email
messages = client.list_email_messages("test@example.com")
for message in messages:
    print(f"From: {message.from_addr}")
    print(f"Subject: {message.subject}")
    print(f"CC: {message.cc}")
    print(f"Attachments: {len(message.attachments or [])}")

# Get a specific message
message = client.get_message("message-id")

# Get message source code
source_code = client.get_message_source_code("message-id")

# Download an attachment
attachment_data = client.download_attachment("attachment-id")

# Delete a message
client.delete_message("message-id")

# Delete an entire email address and all its messages
client.delete_email("test@example.com")
```

### Rate Limiting

```python
# Get current rate limit status
rate_limit = client.get_rate_limit()
print(f"Limit: {rate_limit.limit}")
print(f"Remaining: {rate_limit.remaining}")
print(f"Used: {rate_limit.used}")
print(f"Reset time: {rate_limit.reset}")

# Access last rate limit from any request
last_rate_limit = client.last_rate_limit
if last_rate_limit:
    print(f"Last known remaining: {last_rate_limit.remaining}")
```

## Error Handling

The library provides specific exception types for different error conditions:

```python
from tempmail import (
    TempMailError,           # Base exception
    AuthenticationError,     # Invalid API key
    RateLimitError,         # Rate limit exceeded
    ValidationError,        # Invalid parameters
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
except TempMailError as e:
    print(f"API error: {e}")
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/temp-mail-io/temp-mail-python
cd temp-mail-python

# Install uv (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync --dev
```

### Running Tests

```bash
uv run pytest tests/
```

### Code Quality

```bash
# Run all pre-commit hooks
uv run pre-commit run --all-files

# Or run individual tools
uv run ruff check          # Linting
uv run ruff format         # Formatting
uv run mypy tempmail/      # Type checking
```

## Complete Example

```python
from tempmail import TempMailClient, AuthenticationError, RateLimitError

# Initialize client
client = TempMailClient("your-api-key")

try:
    # Create a temporary email
    email = client.create_email()
    print(f"Created email: {email.email}")
    print(f"TTL: {email.ttl} seconds")

    # List available domains
    domains = client.list_domains()
    print(f"Available domains: {len(domains)}")

    # Check for messages (would be empty initially)
    messages = client.list_email_messages(email.email)
    print(f"Messages: {len(messages)}")

    # Check rate limit
    rate_limit = client.get_rate_limit()
    print(f"Requests remaining: {rate_limit.remaining}/{rate_limit.limit}")

except AuthenticationError:
    print("Invalid API key")
except RateLimitError:
    print("Rate limit exceeded")
except Exception as e:
    print(f"Error: {e}")
```

## License

MIT License—see [LICENSE](LICENSE) file for details.

## Links

- [Temp Mail API Documentation](https://docs.temp-mail.io)
- [GitHub Repository](https://github.com/temp-mail-io/temp-mail-python)
- [PyPI Package](https://pypi.org/project/temp-mail-io/)

"""Data models for the Temp Mail API."""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class RateLimit:
    """Rate limit information from API responses."""

    limit: int
    remaining: int
    reset: int


@dataclass
class Domain:
    """Email domain information."""

    domain: str


@dataclass
class EmailAddress:
    """Generated temporary email address."""

    email: str
    domain: str
    created_at: Optional[datetime] = None


@dataclass
class EmailMessage:
    """Email message received at temporary address."""

    id: str
    from_addr: str
    to_addr: str
    subject: str
    body_text: str
    body_html: Optional[str] = None
    created_at: Optional[datetime] = None
    attachments: Optional[List[Dict[str, Any]]] = None


@dataclass
class CreateEmailOptions:
    """Options for creating a new email address."""

    domain: Optional[str] = None
    prefix: Optional[str] = None


@dataclass
class ListMessagesOptions:
    """Options for listing email messages."""

    limit: Optional[int] = None
    offset: Optional[int] = None

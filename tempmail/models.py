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
    name: str
    type: str # e.g., "public", "custom", "premium"

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Domain':
        return cls(
            name=data['name'],
            type=data['type']
        )


@dataclass
class EmailAddress:
    """Generated temporary email address."""
    email: str
    ttl: int # Time to live in seconds

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'EmailAddress':
        return cls(
            email=data['email'],
            ttl=data['ttl']
        )


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

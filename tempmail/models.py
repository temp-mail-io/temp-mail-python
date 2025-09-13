"""Data models for the Temp Mail API."""

import enum
from dataclasses import dataclass
from typing import Optional, List, Dict, Any


@dataclass
class RateLimit:
    """Rate limit information from API responses."""

    limit: int
    remaining: int
    reset: int
    used: Optional[int] = None

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "RateLimit":
        return cls(
            limit=data["limit"],
            remaining=data["remaining"],
            reset=data["reset"],
            used=data.get("used"),
        )


class DomainType(enum.Enum):
    PUBLIC = "public"
    CUSTOM = "custom"
    PREMIUM = "premium"


@dataclass
class Domain:
    """Email domain information."""

    name: str
    type: DomainType

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Domain":
        return cls(name=data["name"], type=DomainType(data["type"]))


@dataclass
class EmailAddress:
    """Generated temporary email address."""

    email: str
    ttl: int  # Time to live in seconds

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "EmailAddress":
        return cls(email=data["email"], ttl=data["ttl"])


@dataclass
class EmailMessage:
    """Email message received at temporary address."""

    id: str
    from_addr: str
    to_addr: str
    subject: str
    body_text: str
    cc: Optional[List[str]] = None
    body_html: Optional[str] = None
    created_at: Optional[str] = None
    attachments: Optional[List[Dict[str, Any]]] = None

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "EmailMessage":
        return cls(
            id=data["id"],
            from_addr=data["from"],
            to_addr=data["to"],
            subject=data["subject"],
            body_text=data["body_text"],
            cc=data.get("cc", []),
            body_html=data.get("body_html"),
            created_at=data.get("created_at"),
            attachments=data.get("attachments", []),
        )

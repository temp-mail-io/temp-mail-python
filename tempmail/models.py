"""Data models for the Temp Mail API."""

import enum
import typing
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any


@dataclass
class RateLimit:
    """Rate limit information from API responses."""

    limit: int
    remaining: int
    reset: int
    used: int

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "RateLimit":
        return cls(
            limit=data["limit"],
            remaining=data["remaining"],
            reset=data["reset"],
            used=data["used"],
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
class Attachment:
    """Attachment information for an email message."""

    id: str
    name: str
    size: int  # Size in bytes

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Attachment":
        return cls(
            id=data["id"],
            name=data["name"],
            size=data["size"],
        )


@dataclass
class EmailMessage:
    """Email message received at temporary address."""

    id: str
    from_addr: str
    to_addr: str
    subject: str
    body_text: str
    created_at: datetime
    cc: List[str]
    body_html: str
    attachments: List[Attachment]

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "EmailMessage":
        attachments: typing.List[Dict[str, Any]] = data["attachments"] or []
        return cls(
            id=data["id"],
            from_addr=data["from"],
            to_addr=data["to"],
            subject=data["subject"],
            body_text=data["body_text"],
            created_at=datetime.fromisoformat(
                data["created_at"].replace("Z", "+00:00")
            ),
            cc=data["cc"],
            body_html=data["body_html"],
            attachments=[Attachment.from_json(v) for v in attachments],
        )


@dataclass
class APIErrorResponse:
    code: str
    detail: str
    type: str
    request_id: str

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "APIErrorResponse":
        return cls(
            code=data["error"]["code"],
            detail=data["error"]["detail"],
            type=data["error"]["type"],
            request_id=data["meta"]["request_id"],
        )

    def is_api_key_error(self) -> bool:
        """
        Returns True if the error is related to an invalid or missing API key.
        """
        return self.code in {"api_key_invalid", "api_key_empty"}

    def is_rate_limit_error(self) -> bool:
        """
        Returns True if the error is related to exceeding the API rate limit.
        """
        return self.code == "rate_limited"

    def is_validation_error(self) -> bool:
        """
        Returns True if the error is related to invalid request parameters.
        """
        return self.code == "validation_error"

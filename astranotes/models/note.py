"""Note domain entity (FR-01, FR-06, FR-07)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class Note:
    title: str
    body: str = ""
    is_private: bool = False
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=_utcnow)
    modified_at: datetime = field(default_factory=_utcnow)
    tags: list[str] = field(default_factory=list)

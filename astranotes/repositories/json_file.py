"""JSON-file-per-note repository adapter (FR-05, FR-06)."""

from __future__ import annotations

import base64
import json
import logging
from datetime import datetime
from pathlib import Path
from uuid import UUID

from astranotes.models.exceptions import NoteNotFoundError, PersistenceError
from astranotes.models.note import Note
from astranotes.repositories.base import NoteRepository

logger = logging.getLogger(__name__)


class JsonFileRepository(NoteRepository):
    def __init__(self, data_dir: Path) -> None:
        self._data_dir = Path(data_dir)
        try:
            self._data_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise PersistenceError("Could not initialize data directory") from exc

    def save(self, note: Note) -> None:
        self._write(note)

    def update(self, note: Note) -> None:
        if not self._path_for(note.id).exists():
            raise NoteNotFoundError(str(note.id))
        self._write(note)

    def get(self, note_id: UUID) -> Note:
        path = self._path_for(note_id)
        if not path.exists():
            raise NoteNotFoundError(str(note_id))
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise PersistenceError("Could not read note") from exc
        return self._from_payload(payload)

    def list_all(self) -> list[Note]:
        notes: list[Note] = []
        for path in sorted(self._data_dir.glob("*.json")):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
                notes.append(self._from_payload(payload))
            except (OSError, json.JSONDecodeError, KeyError, ValueError) as exc:
                logger.error("Skipping corrupt note file %s: %s", path.name, exc)
        return notes

    def delete(self, note_id: UUID) -> None:
        path = self._path_for(note_id)
        if not path.exists():
            raise NoteNotFoundError(str(note_id))
        try:
            path.unlink()
        except OSError as exc:
            raise PersistenceError("Could not delete note") from exc

    def _path_for(self, note_id: UUID) -> Path:
        return self._data_dir / f"{note_id}.json"

    def _write(self, note: Note) -> None:
        try:
            self._path_for(note.id).write_text(
                json.dumps(self._to_payload(note), indent=2),
                encoding="utf-8",
            )
        except OSError as exc:
            raise PersistenceError("Could not write note") from exc

    @staticmethod
    def _to_payload(note: Note) -> dict:
        body = note.body
        body_encoding = "utf-8"
        if isinstance(body, bytes):
            body = base64.b64encode(body).decode("ascii")
            body_encoding = "base64"
        return {
            "id": str(note.id),
            "title": note.title,
            "body": body,
            "body_encoding": body_encoding,
            "is_private": note.is_private,
            "created_at": note.created_at.isoformat(),
            "modified_at": note.modified_at.isoformat(),
            "tags": list(note.tags),
        }

    @staticmethod
    def _from_payload(payload: dict) -> Note:
        body: str | bytes = payload["body"]
        if payload.get("body_encoding") == "base64":
            body = base64.b64decode(payload["body"].encode("ascii"))
        return Note(
            id=UUID(payload["id"]),
            title=payload["title"],
            body=body,
            is_private=payload["is_private"],
            created_at=datetime.fromisoformat(payload["created_at"]),
            modified_at=datetime.fromisoformat(payload["modified_at"]),
            tags=list(payload.get("tags", [])),
        )

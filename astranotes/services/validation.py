"""ValidationLayer: enforces note invariants before persistence (FR-01)."""

from __future__ import annotations

from astranotes.models.exceptions import ValidationError
from astranotes.models.note import Note


class ValidationLayer:
    def validate(self, note: Note) -> None:
        self._validate_title(note.title)

    @staticmethod
    def _validate_title(title: str) -> None:
        if not isinstance(title, str) or not title.strip():
            raise ValidationError("Note title must be a non-empty string")

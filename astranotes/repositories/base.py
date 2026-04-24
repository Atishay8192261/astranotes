"""Abstract repository interface for notes (FR-05, NFR-02)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from astranotes.models.note import Note


class NoteRepository(ABC):
    @abstractmethod
    def save(self, note: Note) -> None:
        """Persist a new note."""

    @abstractmethod
    def get(self, note_id: UUID) -> Note:
        """Return the note with the given id or raise NoteNotFoundError."""

    @abstractmethod
    def list_all(self) -> list[Note]:
        """Return all stored notes."""

    @abstractmethod
    def update(self, note: Note) -> None:
        """Replace an existing note's stored representation."""

    @abstractmethod
    def delete(self, note_id: UUID) -> None:
        """Remove the note with the given id or raise NoteNotFoundError."""

"""Presentation-tier logic for the GUI (NFR-02, SPR-02).

This module holds NO widget code. The CustomTkinter view in app.py is a thin
shell that delegates every action here, so the presentation tier's behavior
is unit-testable without a display. The controller talks to the logic tier
through the same NoteManager dependency-injection seam the CLI used.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from astranotes.config import resolve_data_dir, resolve_privacy
from astranotes.models.exceptions import AstraNotesError
from astranotes.models.note import Note
from astranotes.repositories.json_file import JsonFileRepository
from astranotes.services.note_manager import NoteManager
from astranotes.services.validation import ValidationLayer


@dataclass
class ActionResult:
    ok: bool
    message: str


class NotesController:
    def __init__(self, manager: NoteManager) -> None:
        self._manager = manager

    def list_notes(self) -> list[Note]:
        try:
            return self._manager.list_notes()
        except AstraNotesError:
            return []

    def create_note(
        self,
        title: str,
        body: str,
        is_private: bool,
        tags_csv: str = "",
    ) -> ActionResult:
        tags = [t.strip() for t in tags_csv.split(",") if t.strip()]
        try:
            note = self._manager.create_note(
                title=title,
                body=body,
                is_private=is_private,
                tags=tags,
            )
        except AstraNotesError as exc:
            return ActionResult(False, str(exc))
        return ActionResult(True, f"Saved note {note.id}")

    def delete_note(self, note_id: UUID) -> ActionResult:
        try:
            self._manager._repository.delete(note_id)
        except AstraNotesError as exc:
            return ActionResult(False, str(exc))
        return ActionResult(True, "Note deleted")


def build_default_controller() -> tuple[NotesController, str]:
    """Wire the default runtime controller. Returns (controller, key_source)."""
    data_dir = resolve_data_dir()
    resolution = resolve_privacy()
    manager = NoteManager(
        repository=JsonFileRepository(data_dir),
        validation=ValidationLayer(),
        privacy=resolution.privacy,
    )
    return NotesController(manager), resolution.source

"""Presentation-tier logic for the GUI (NFR-02, SPR-02).

This module holds NO widget code. The CustomTkinter view in app.py is a thin
shell that delegates every action here, so the presentation tier's behavior
is unit-testable without a display. The controller talks to the logic tier
through the same NoteManager dependency-injection seam the CLI used.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional
from uuid import UUID

from astranotes.config import resolve_data_dir, resolve_privacy
from astranotes.models.exceptions import AstraNotesError
from astranotes.models.note import Note
from astranotes.repositories.json_file import JsonFileRepository
from astranotes.services.note_manager import NoteManager
from astranotes.services.privacy import PrivacyService
from astranotes.services.validation import ValidationLayer


@dataclass
class ActionResult:
    ok: bool
    message: str


class NotesController:
    def __init__(self, manager: NoteManager) -> None:
        self._manager = manager

    @property
    def has_privacy_key(self) -> bool:
        return self._manager._privacy is not None

    def set_privacy_service(self, privacy: PrivacyService) -> None:
        """Inject a passphrase-derived PrivacyService after launch (ADR-005)."""
        self._manager._privacy = privacy

    def reset_vault(self, privacy: PrivacyService) -> None:
        self._manager.rotate_privacy(privacy)

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

    def update_note(
        self,
        note_id: UUID,
        title: str,
        body: str,
        tags_csv: str = "",
    ) -> ActionResult:
        tags = [t.strip() for t in tags_csv.split(",") if t.strip()]
        try:
            self._manager.update_note(note_id, title=title, body=body, tags=tags)
        except AstraNotesError as exc:
            return ActionResult(False, str(exc))
        return ActionResult(True, "Note updated")

    def set_private(self, note_id: UUID, is_private: bool) -> ActionResult:
        try:
            self._manager.set_private(note_id, is_private)
        except AstraNotesError as exc:
            return ActionResult(False, str(exc))
        return ActionResult(True, "Private" if is_private else "Public")

    def search_notes(self, keyword: str) -> list[Note]:
        try:
            return self._manager.search_notes(keyword)
        except AstraNotesError:
            return []

    def delete_note(self, note_id: UUID) -> ActionResult:
        try:
            self._manager.delete_note(note_id)
        except AstraNotesError as exc:
            return ActionResult(False, str(exc))
        return ActionResult(True, "Note deleted")

    def duplicate_note(self, note_id: UUID) -> ActionResult:
        try:
            note = self._manager.duplicate_note(note_id)
        except AstraNotesError as exc:
            return ActionResult(False, str(exc))
        return ActionResult(True, f"Duplicated as '{note.title}'")

    def get_note(self, note_id: UUID) -> Optional[Note]:
        try:
            return self._manager.get_note(note_id)
        except AstraNotesError:
            return None

    def list_all_for_display(self) -> list[Note]:
        try:
            return self._manager.list_all_for_display()
        except AstraNotesError:
            return []

    def get_stats(self) -> dict[str, Any]:
        data_dir = Path(resolve_data_dir())
        stats = self._manager.get_stats()
        storage_bytes = (
            sum(f.stat().st_size for f in data_dir.glob("*.json") if f.is_file())
            if data_dir.exists()
            else 0
        )
        stats["storage_bytes"] = storage_bytes
        stats["data_dir"] = str(data_dir)
        return stats


_LEGACY = object()


def build_default_controller(
    privacy: Optional[PrivacyService] = _LEGACY,  # type: ignore[assignment]
    key_source: Optional[str] = None,
) -> tuple[NotesController, str]:
    """Wire the default runtime controller. Returns (controller, key_source).

    Modes:
      - privacy=_LEGACY (default): use env-var resolver. CLI/tests rely on this.
      - privacy=None:              build with no key (passphrase set lazily).
      - privacy=<PrivacyService>:  use the caller's service (passphrase unlock).
    """
    data_dir = resolve_data_dir()
    if privacy is _LEGACY:
        resolution = resolve_privacy()
        privacy = resolution.privacy
        key_source = key_source or resolution.source
    manager = NoteManager(
        repository=JsonFileRepository(data_dir),
        validation=ValidationLayer(),
        privacy=privacy,
    )
    return NotesController(manager), key_source or "passphrase"

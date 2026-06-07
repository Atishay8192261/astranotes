"""NoteManager: orchestrates validation, privacy, and persistence (FR-01-FR-08)."""

from __future__ import annotations

import logging
from dataclasses import replace
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID

from astranotes.models.exceptions import NoteNotFoundError, PersistenceError
from astranotes.models.note import Note
from astranotes.repositories.base import NoteRepository
from astranotes.services.privacy import PrivacyService
from astranotes.services.validation import ValidationLayer

logger = logging.getLogger(__name__)


class NoteManager:
    def __init__(
        self,
        repository: NoteRepository,
        validation: ValidationLayer,
        privacy: Optional[PrivacyService] = None,
    ) -> None:
        self._repository = repository
        self._validation = validation
        self._privacy = privacy

    def create_note(
        self,
        title: str,
        body: str = "",
        is_private: bool = False,
        tags: Optional[list[str]] = None,
    ) -> Note:
        note = Note(title=title, body=body, is_private=is_private, tags=list(tags or []))
        self._validation.validate(note)

        if is_private:
            if self._privacy is None:
                raise PersistenceError("Private notes require a configured privacy key")
            stored = replace(note, body=self._privacy.encrypt(body))
        else:
            stored = note

        self._repository.save(stored)
        return note

    def list_notes(self) -> list[Note]:
        loaded = self._repository.list_all()
        visible: list[Note] = []
        for stored in loaded:
            if stored.is_private:
                if self._privacy is None:
                    logger.error("Skipping private note %s: no privacy key configured", stored.id)
                    continue
                try:
                    plaintext = self._privacy.decrypt(stored.body)
                except PersistenceError as exc:
                    logger.error("Skipping note %s: decryption failed (%s)", stored.id, exc)
                    continue
                visible.append(replace(stored, body=plaintext))
            else:
                visible.append(stored)
        visible.sort(key=lambda n: (n.modified_at, n.created_at), reverse=True)
        return visible

    def update_note(
        self,
        note_id: UUID,
        title: Optional[str] = None,
        body: Optional[str] = None,
        tags: Optional[list[str]] = None,
    ) -> Note:
        """Edit title/body/tags of an existing note (FR-02).

        `created_at` and `id` are immutable; `modified_at` advances. Privacy
        flag is unchanged here - use `set_private` to toggle it (FR-04).
        """
        stored = self._load_stored(note_id)
        plaintext_body = self._plaintext_body(stored)

        new_title = title if title is not None else stored.title
        new_body = body if body is not None else plaintext_body
        new_tags = list(tags) if tags is not None else list(stored.tags)

        candidate = replace(
            stored,
            title=new_title,
            body=new_body,
            tags=new_tags,
            is_private=stored.is_private,
        )
        self._validation.validate(candidate)

        if stored.is_private:
            self._require_privacy()
            persisted_body = self._privacy.encrypt(new_body)
        else:
            persisted_body = new_body

        updated = replace(
            stored,
            title=new_title,
            body=persisted_body,
            tags=new_tags,
            modified_at=datetime.now(timezone.utc),
        )
        self._repository.update(updated)
        return replace(updated, body=new_body)

    def delete_note(self, note_id: UUID) -> None:
        """Delete a note by id (FR-03).

        Raises NoteNotFoundError if the id does not exist; PersistenceError if
        the underlying storage fails. Never silently succeeds.
        """
        self._repository.delete(note_id)

    def set_private(self, note_id: UUID, is_private: bool) -> Note:
        """Toggle the privacy flag on an existing note (FR-04).

        True  -> re-save body as ciphertext.
        False -> decrypt and re-save body as plaintext.
        If decryption fails during a True->False toggle, the operation fails
        and the note is left untouched on disk (refined FR-04).
        """
        stored = self._load_stored(note_id)
        if stored.is_private == is_private:
            return replace(stored, body=self._plaintext_body(stored))

        plaintext = self._plaintext_body(stored)
        if is_private:
            self._require_privacy()
            new_body = self._privacy.encrypt(plaintext)
        else:
            new_body = plaintext

        updated = replace(
            stored,
            body=new_body,
            is_private=is_private,
            modified_at=datetime.now(timezone.utc),
        )
        self._repository.update(updated)
        return replace(updated, body=plaintext)

    def rotate_privacy(self, new_privacy: PrivacyService) -> None:
        """Re-encrypt every private note with a new vault key.

        The current privacy key must be loaded so the manager can decrypt the
        existing private notes first. Public notes are left untouched.
        """
        self._require_privacy()

        private_notes: list[tuple[Note, str]] = []
        for stored in self._repository.list_all():
            if not stored.is_private:
                continue
            plaintext = self._privacy.decrypt(stored.body)
            private_notes.append((stored, plaintext))

        for stored, plaintext in private_notes:
            updated = replace(
                stored,
                body=new_privacy.encrypt(plaintext),
                modified_at=datetime.now(timezone.utc),
            )
            self._repository.update(updated)

        self._privacy = new_privacy

    def _load_stored(self, note_id: UUID) -> Note:
        try:
            return self._repository.get(note_id)
        except NoteNotFoundError:
            raise

    def _plaintext_body(self, stored: Note) -> str:
        if not stored.is_private:
            return stored.body if isinstance(stored.body, str) else stored.body.decode("utf-8")
        self._require_privacy()
        return self._privacy.decrypt(stored.body)

    def _require_privacy(self) -> None:
        if self._privacy is None:
            raise PersistenceError("Operation requires a configured privacy key")

    def get_note(self, note_id: UUID) -> Note:
        """Retrieve a single note, decrypted if private."""
        stored = self._load_stored(note_id)
        if stored.is_private:
            return replace(stored, body=self._plaintext_body(stored))
        return stored

    def duplicate_note(self, note_id: UUID) -> Note:
        """Create a copy of a note with 'Copy of ' title prefix (FR-05 extension)."""
        stored = self._load_stored(note_id)
        plaintext = self._plaintext_body(stored) if stored.is_private else stored.body
        return self.create_note(
            title=f"Copy of {stored.title}",
            body=plaintext,
            is_private=stored.is_private,
            tags=list(stored.tags),
        )

    def list_all_for_display(self) -> list[Note]:
        """Return all notes including locked ones.

        Private notes that cannot be decrypted (no key or wrong key) are
        included with body="" and is_private=True so the UI can show a lock
        indicator. This differs from list_notes() which silently skips them.
        """
        loaded = self._repository.list_all()
        result: list[Note] = []
        for stored in loaded:
            if stored.is_private:
                if self._privacy is None:
                    result.append(replace(stored, body=""))
                    continue
                try:
                    plaintext = self._privacy.decrypt(stored.body)
                    result.append(replace(stored, body=plaintext))
                except Exception:
                    result.append(replace(stored, body=""))
            else:
                result.append(stored)
        result.sort(key=lambda n: (n.modified_at, n.created_at), reverse=True)
        return result

    def get_stats(self) -> dict[str, Any]:
        """Return operational statistics for the admin/telemetry panel."""
        all_notes = self._repository.list_all()
        total = len(all_notes)
        private = sum(1 for n in all_notes if n.is_private)
        public_bodies = [len(n.body) for n in all_notes if not n.is_private]
        avg_body = sum(public_bodies) / len(public_bodies) if public_bodies else 0.0
        return {
            "total_notes": total,
            "public_notes": total - private,
            "private_notes": private,
            "avg_body_length": avg_body,
        }

    def search_notes(self, keyword: str) -> list[Note]:
        """Keyword search across titles and bodies (FR-07).

        Case-insensitive plain substring match (not regex). Private notes are
        decrypted before matching; notes whose bodies fail to decrypt are
        skipped with an error logged (SPR-01, SPR-02). Empty/whitespace
        keywords return an empty list. Results follow FR-08 ordering.
        """
        needle = keyword.strip().lower()
        if not needle:
            return []
        matches = [n for n in self.list_notes() if needle in n.title.lower() or needle in n.body.lower()]
        return matches

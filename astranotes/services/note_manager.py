"""NoteManager: orchestrates validation, privacy, and persistence (FR-01, FR-04, FR-05, FR-08)."""

from __future__ import annotations

import logging
from dataclasses import replace
from typing import Optional

from astranotes.models.exceptions import PersistenceError
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

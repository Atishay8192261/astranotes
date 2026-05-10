"""NoteManager unit tests (FR-01, FR-04, FR-05, FR-08, SPR-02)."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from astranotes.models.exceptions import PersistenceError, ValidationError
from astranotes.repositories.json_file import JsonFileRepository
from astranotes.services.note_manager import NoteManager
from astranotes.services.privacy import PrivacyService
from astranotes.services.validation import ValidationLayer


@pytest.fixture
def manager(tmp_path: Path) -> NoteManager:
    return NoteManager(
        repository=JsonFileRepository(tmp_path),
        validation=ValidationLayer(),
        privacy=PrivacyService(PrivacyService.generate_key()),
    )


def test_create_note_persists_plaintext_body(manager: NoteManager, tmp_path: Path) -> None:
    note = manager.create_note(title="grocery list", body="milk, eggs")
    saved_files = list(tmp_path.glob("*.json"))
    assert len(saved_files) == 1
    contents = saved_files[0].read_text()
    assert "milk, eggs" in contents
    assert note.title == "grocery list"


def test_create_note_rejects_whitespace_title(manager: NoteManager) -> None:
    with pytest.raises(ValidationError):
        manager.create_note(title="   ", body="anything")


def test_create_private_note_encrypts_body_on_disk(manager: NoteManager, tmp_path: Path) -> None:
    manager.create_note(title="secret", body="meet at 5", is_private=True)
    raw = list(tmp_path.glob("*.json"))[0].read_text()
    assert "meet at 5" not in raw
    assert '"body_encoding": "base64"' in raw


def test_create_private_without_privacy_service_raises(tmp_path: Path) -> None:
    bare = NoteManager(
        repository=JsonFileRepository(tmp_path),
        validation=ValidationLayer(),
        privacy=None,
    )
    with pytest.raises(PersistenceError):
        bare.create_note(title="t", body="b", is_private=True)


def test_list_notes_decrypts_private_bodies(manager: NoteManager) -> None:
    manager.create_note(title="public", body="hello")
    manager.create_note(title="private", body="hidden text", is_private=True)
    notes = manager.list_notes()
    bodies = {n.title: n.body for n in notes}
    assert bodies["public"] == "hello"
    assert bodies["private"] == "hidden text"


def test_list_notes_skips_undecryptable_private_note(tmp_path: Path) -> None:
    privacy_writer = PrivacyService(PrivacyService.generate_key())
    privacy_reader = PrivacyService(PrivacyService.generate_key())
    writer = NoteManager(
        repository=JsonFileRepository(tmp_path),
        validation=ValidationLayer(),
        privacy=privacy_writer,
    )
    writer.create_note(title="public", body="visible")
    writer.create_note(title="locked", body="will fail", is_private=True)

    reader = NoteManager(
        repository=JsonFileRepository(tmp_path),
        validation=ValidationLayer(),
        privacy=privacy_reader,
    )
    notes = reader.list_notes()
    titles = [n.title for n in notes]
    assert "public" in titles
    assert "locked" not in titles


def test_list_notes_sorted_by_modified_desc(manager: NoteManager) -> None:
    manager.create_note(title="first", body="a")
    time.sleep(0.01)
    manager.create_note(title="second", body="b")
    time.sleep(0.01)
    manager.create_note(title="third", body="c")
    notes = manager.list_notes()
    assert [n.title for n in notes] == ["third", "second", "first"]


def test_list_notes_empty_collection_returns_empty_list(manager: NoteManager) -> None:
    assert manager.list_notes() == []

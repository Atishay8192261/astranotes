"""Tests for the Note dataclass (FR-01, FR-06)."""

from datetime import datetime, timezone
from uuid import UUID

from astranotes.models.note import Note


def test_note_instantiates_with_required_fields():
    note = Note(title="Hello")
    assert note.title == "Hello"
    assert note.body == ""
    assert note.is_private is False
    assert note.tags == []


def test_note_id_is_valid_uuid():
    note = Note(title="Hello")
    assert isinstance(note.id, UUID)


def test_note_ids_are_unique():
    a = Note(title="A")
    b = Note(title="B")
    assert a.id != b.id


def test_note_timestamps_default_to_utc_now():
    before = datetime.now(timezone.utc)
    note = Note(title="Hello")
    after = datetime.now(timezone.utc)

    assert note.created_at.tzinfo is not None
    assert note.modified_at.tzinfo is not None
    assert before <= note.created_at <= after
    assert before <= note.modified_at <= after


def test_note_tags_are_independent_per_instance():
    a = Note(title="A")
    b = Note(title="B")
    a.tags.append("work")
    assert b.tags == []

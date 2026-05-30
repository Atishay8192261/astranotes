"""Tests for JsonFileRepository (FR-05, FR-06)."""

import pytest

from astranotes.models.exceptions import NoteNotFoundError
from astranotes.models.note import Note
from astranotes.repositories.json_file import JsonFileRepository


@pytest.fixture
def repo(tmp_path):
    return JsonFileRepository(tmp_path / "data")


def test_save_and_get_round_trip(repo):
    note = Note(title="Hello", body="World", tags=["greeting"])
    repo.save(note)

    loaded = repo.get(note.id)
    assert loaded.id == note.id
    assert loaded.title == note.title
    assert loaded.body == note.body
    assert loaded.is_private == note.is_private
    assert loaded.created_at == note.created_at
    assert loaded.modified_at == note.modified_at
    assert loaded.tags == note.tags


def test_get_unknown_id_raises(repo):
    note = Note(title="Hello")
    with pytest.raises(NoteNotFoundError):
        repo.get(note.id)


def test_list_all_returns_every_saved_note(repo):
    a = Note(title="A")
    b = Note(title="B")
    repo.save(a)
    repo.save(b)

    ids = {n.id for n in repo.list_all()}
    assert ids == {a.id, b.id}


def test_update_replaces_stored_payload(repo):
    note = Note(title="Original")
    repo.save(note)

    note.title = "Edited"
    repo.update(note)

    assert repo.get(note.id).title == "Edited"


def test_update_unknown_id_raises(repo):
    with pytest.raises(NoteNotFoundError):
        repo.update(Note(title="ghost"))


def test_delete_removes_note(repo):
    note = Note(title="Doomed")
    repo.save(note)
    repo.delete(note.id)
    with pytest.raises(NoteNotFoundError):
        repo.get(note.id)


def test_delete_unknown_id_raises(repo):
    with pytest.raises(NoteNotFoundError):
        repo.delete(Note(title="ghost").id)


def test_corrupt_files_are_skipped(repo, tmp_path):
    note = Note(title="Good")
    repo.save(note)
    (tmp_path / "data" / "broken.json").write_text("{not json")

    loaded = repo.list_all()
    assert [n.id for n in loaded] == [note.id]


def test_data_directory_is_auto_created(tmp_path):
    target = tmp_path / "nested" / "data"
    JsonFileRepository(target)
    assert target.exists()


# ---------- Corrupt-file branch coverage (gap #5) ---------------------------


def test_list_all_skips_files_missing_required_keys(repo, tmp_path):
    """list_all's except catches KeyError - prove it actually exercises that branch."""
    good = Note(title="ok")
    repo.save(good)
    (tmp_path / "data" / "missing-title.json").write_text('{"id": "x", "body": ""}')
    loaded = repo.list_all()
    assert [n.id for n in loaded] == [good.id]


def test_list_all_skips_files_with_bad_uuid(repo, tmp_path):
    good = Note(title="ok")
    repo.save(good)
    (tmp_path / "data" / "bad.json").write_text(
        '{"id": "not-a-uuid", "title": "x", "body": "", "is_private": false,'
        ' "created_at": "2026-01-01T00:00:00+00:00",'
        ' "modified_at": "2026-01-01T00:00:00+00:00", "tags": []}'
    )
    loaded = repo.list_all()
    assert [n.id for n in loaded] == [good.id]


def test_list_all_skips_files_with_bad_iso_timestamp(repo, tmp_path):
    good = Note(title="ok")
    repo.save(good)
    from uuid import uuid4
    (tmp_path / "data" / "badts.json").write_text(
        '{"id": "' + str(uuid4()) + '", "title": "x", "body": "", "is_private": false,'
        ' "created_at": "not-a-date", "modified_at": "not-a-date", "tags": []}'
    )
    loaded = repo.list_all()
    assert [n.id for n in loaded] == [good.id]


# ---------- Mixed-dir startup (gap #6) --------------------------------------


def test_startup_mixed_dir_loads_valid_and_logs_for_corrupt(repo, tmp_path, caplog):
    """FR-05: 'load valid files, skip corrupt ones with error logged.'"""
    import logging
    good = Note(title="keep me")
    repo.save(good)
    (tmp_path / "data" / "broken.json").write_text("{not json")
    (tmp_path / "data" / "missing.json").write_text('{"id": "x"}')

    with caplog.at_level(logging.ERROR, logger="astranotes.repositories.json_file"):
        loaded = repo.list_all()

    assert [n.id for n in loaded] == [good.id]
    error_messages = "\n".join(rec.message for rec in caplog.records)
    assert "broken.json" in error_messages or "missing.json" in error_messages


# ---------- Filesystem-failure branches (gap #13) ---------------------------


def test_save_raises_persistence_error_on_write_failure(repo, monkeypatch):
    """The except OSError branch in _write must surface as PersistenceError, not OSError."""
    from astranotes.models.exceptions import PersistenceError
    note = Note(title="t")

    def boom(self, *a, **kw):
        raise OSError("disk full")
    monkeypatch.setattr("pathlib.Path.write_text", boom)
    with pytest.raises(PersistenceError):
        repo.save(note)


def test_delete_raises_persistence_error_on_unlink_failure(repo, monkeypatch):
    from astranotes.models.exceptions import PersistenceError
    note = Note(title="t")
    repo.save(note)

    def boom(self, *a, **kw):
        raise PermissionError("readonly")
    monkeypatch.setattr("pathlib.Path.unlink", boom)
    with pytest.raises(PersistenceError):
        repo.delete(note.id)


def test_get_raises_persistence_error_on_read_failure(repo, monkeypatch):
    from astranotes.models.exceptions import PersistenceError
    note = Note(title="t")
    repo.save(note)

    def boom(self, *a, **kw):
        raise OSError("io error")
    monkeypatch.setattr("pathlib.Path.read_text", boom)
    with pytest.raises(PersistenceError):
        repo.get(note.id)


# ---------- UTC tzinfo round-trip (gap #15) ---------------------------------


def test_round_trip_preserves_utc_tzinfo(repo):
    from datetime import timezone
    note = Note(title="t")
    repo.save(note)
    loaded = repo.get(note.id)
    assert loaded.created_at.tzinfo is not None
    assert loaded.created_at.utcoffset() == timezone.utc.utcoffset(None)

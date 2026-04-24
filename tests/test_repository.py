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

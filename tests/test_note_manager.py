"""NoteManager unit tests (FR-01, FR-04, FR-05, FR-08, SPR-02)."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from astranotes.models.exceptions import NoteNotFoundError, PersistenceError, ValidationError
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
    """Gap #4 fix: assert the SPR-01 property, not the serialization format.

    The original test pinned the literal `'"body_encoding": "base64"'` string,
    which couples the test to a private storage detail. The real contract is:
    (a) the plaintext never appears on disk in any form, and (b) the stored
    bytes still decrypt back to the original plaintext under the same key.
    This passes if we change envelope formats; it fails if we leak plaintext.
    """
    import json
    plaintext = "meet rendezvous coordinates xyz123"
    manager.create_note(title="secret", body=plaintext, is_private=True)
    payload = json.loads(list(tmp_path.glob("*.json"))[0].read_text())

    assert plaintext not in payload["body"]
    for word in plaintext.split():
        assert word not in payload["body"], f"plaintext token '{word}' leaked to disk"

    notes = manager.list_notes()
    assert [n.body for n in notes] == [plaintext]


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


def test_search_notes_matches_title_and_body_case_insensitive(manager: NoteManager) -> None:
    manager.create_note(title="Grocery List", body="milk, eggs")
    manager.create_note(title="Meeting", body="discuss MILK delivery")
    manager.create_note(title="unrelated", body="nothing here")
    titles = {n.title for n in manager.search_notes("milk")}
    assert titles == {"Grocery List", "Meeting"}


def test_search_notes_decrypts_private_notes_before_matching(manager: NoteManager) -> None:
    manager.create_note(title="diary", body="secret password", is_private=True)
    results = manager.search_notes("password")
    assert [n.title for n in results] == ["diary"]


def test_search_notes_empty_keyword_returns_empty(manager: NoteManager) -> None:
    manager.create_note(title="anything", body="anything")
    assert manager.search_notes("") == []
    assert manager.search_notes("   ") == []


def test_search_notes_empty_collection_returns_empty(manager: NoteManager) -> None:
    assert manager.search_notes("anything") == []


def test_search_notes_skips_undecryptable_private_note(tmp_path: Path) -> None:
    writer = NoteManager(
        repository=JsonFileRepository(tmp_path),
        validation=ValidationLayer(),
        privacy=PrivacyService(PrivacyService.generate_key()),
    )
    writer.create_note(title="public match", body="findme")
    writer.create_note(title="locked", body="findme too", is_private=True)
    reader = NoteManager(
        repository=JsonFileRepository(tmp_path),
        validation=ValidationLayer(),
        privacy=PrivacyService(PrivacyService.generate_key()),
    )
    titles = [n.title for n in reader.search_notes("findme")]
    assert titles == ["public match"]


# ---------- FR-02 Edit (gap #1) ---------------------------------------------


def test_update_note_changes_title_and_body_advances_modified(manager: NoteManager) -> None:
    note = manager.create_note(title="draft", body="v1")
    original_created = note.created_at
    original_modified = note.modified_at
    time.sleep(0.01)

    updated = manager.update_note(note.id, title="final", body="v2")
    assert updated.id == note.id
    assert updated.title == "final"
    assert updated.body == "v2"
    assert updated.created_at == original_created
    assert updated.modified_at > original_modified


def test_update_note_preserves_immutables(manager: NoteManager) -> None:
    note = manager.create_note(title="t", body="b")
    updated = manager.update_note(note.id, title="t2")
    assert updated.id == note.id
    assert updated.created_at == note.created_at


def test_update_note_rejects_blank_title(manager: NoteManager) -> None:
    note = manager.create_note(title="ok", body="b")
    with pytest.raises(ValidationError):
        manager.update_note(note.id, title="   ")


def test_update_note_unknown_id_raises_not_found(manager: NoteManager) -> None:
    from uuid import uuid4
    with pytest.raises(NoteNotFoundError):
        manager.update_note(uuid4(), title="x")


def test_update_preserves_encryption_for_private_note(manager: NoteManager, tmp_path: Path) -> None:
    note = manager.create_note(title="s", body="alpha", is_private=True)
    manager.update_note(note.id, body="bravo")
    raw = list(tmp_path.glob("*.json"))[0].read_text()
    assert "alpha" not in raw
    assert "bravo" not in raw
    assert manager.list_notes()[0].body == "bravo"


# ---------- FR-03 Delete via manager (gap #2) -------------------------------


def test_delete_note_removes_from_storage(manager: NoteManager) -> None:
    note = manager.create_note(title="doomed", body="x")
    manager.delete_note(note.id)
    assert manager.list_notes() == []


def test_delete_note_unknown_id_raises_domain_error(manager: NoteManager) -> None:
    from uuid import uuid4
    with pytest.raises(NoteNotFoundError):
        manager.delete_note(uuid4())


# ---------- FR-04 Toggle private (gap #3) -----------------------------------


def test_set_private_true_encrypts_body_on_disk(manager: NoteManager, tmp_path: Path) -> None:
    plaintext = "make it secret"
    note = manager.create_note(title="t", body=plaintext)
    manager.set_private(note.id, True)
    raw = list(tmp_path.glob("*.json"))[0].read_text()
    assert plaintext not in raw
    assert manager.list_notes()[0].body == plaintext
    assert manager.list_notes()[0].is_private is True


def test_set_private_false_decrypts_and_writes_plaintext(manager: NoteManager, tmp_path: Path) -> None:
    plaintext = "no longer secret"
    note = manager.create_note(title="t", body=plaintext, is_private=True)
    manager.set_private(note.id, False)
    raw = list(tmp_path.glob("*.json"))[0].read_text()
    assert plaintext in raw
    assert manager.list_notes()[0].is_private is False


def test_set_private_toggle_decrypt_failure_keeps_note_encrypted(tmp_path: Path) -> None:
    """Refined FR-04: if decryption fails during a True->False toggle,
    the operation fails and the note stays encrypted on disk."""
    writer = NoteManager(
        repository=JsonFileRepository(tmp_path),
        validation=ValidationLayer(),
        privacy=PrivacyService(PrivacyService.generate_key()),
    )
    note = writer.create_note(title="s", body="hidden", is_private=True)
    raw_before = list(tmp_path.glob("*.json"))[0].read_text()

    reader = NoteManager(
        repository=JsonFileRepository(tmp_path),
        validation=ValidationLayer(),
        privacy=PrivacyService(PrivacyService.generate_key()),
    )
    with pytest.raises(PersistenceError):
        reader.set_private(note.id, False)

    raw_after = list(tmp_path.glob("*.json"))[0].read_text()
    assert raw_before == raw_after
    assert "hidden" not in raw_after


def test_set_private_noop_when_already_in_target_state(manager: NoteManager) -> None:
    note = manager.create_note(title="t", body="b", is_private=False)
    result = manager.set_private(note.id, False)
    assert result.is_private is False
    assert result.body == "b"


# ---------- Search hardening (gaps #10, #11, #12) ---------------------------


def test_search_treats_special_characters_as_literal(manager: NoteManager) -> None:
    """FR-07: 'plain string matching, not regex'. Special chars must match literally."""
    manager.create_note(title="alpha", body="value is a|b")
    manager.create_note(title="beta", body="anything")
    manager.create_note(title="gamma", body="literal .* here")

    assert [n.title for n in manager.search_notes("a|b")] == ["alpha"]
    assert [n.title for n in manager.search_notes(".*")] == ["gamma"]


def test_search_returns_only_matching_private_note_among_many(manager: NoteManager) -> None:
    manager.create_note(title="d1", body="apple", is_private=True)
    manager.create_note(title="d2", body="banana", is_private=True)
    manager.create_note(title="d3", body="cherry", is_private=True)
    titles = [n.title for n in manager.search_notes("banana")]
    assert titles == ["d2"]


def test_search_and_list_skip_the_same_undecryptable_notes(tmp_path: Path) -> None:
    """gap #12: search and list must agree on which private notes are skipped."""
    writer = NoteManager(
        repository=JsonFileRepository(tmp_path),
        validation=ValidationLayer(),
        privacy=PrivacyService(PrivacyService.generate_key()),
    )
    writer.create_note(title="visible", body="findme")
    writer.create_note(title="locked", body="findme", is_private=True)
    reader = NoteManager(
        repository=JsonFileRepository(tmp_path),
        validation=ValidationLayer(),
        privacy=PrivacyService(PrivacyService.generate_key()),
    )
    listed = {n.title for n in reader.list_notes()}
    searched = {n.title for n in reader.search_notes("findme")}
    assert "locked" not in listed
    assert "locked" not in searched


# ---------- SPR-02 log-content assertion (gap #7) ---------------------------


def test_decrypt_failure_log_does_not_leak_path_or_traceback(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """SPR-02: error messages must not expose file paths, stack traces, or key material."""
    import logging
    writer = NoteManager(
        repository=JsonFileRepository(tmp_path),
        validation=ValidationLayer(),
        privacy=PrivacyService(PrivacyService.generate_key()),
    )
    writer.create_note(title="locked", body="hidden", is_private=True)
    reader_key = PrivacyService.generate_key()
    reader = NoteManager(
        repository=JsonFileRepository(tmp_path),
        validation=ValidationLayer(),
        privacy=PrivacyService(reader_key),
    )
    with caplog.at_level(logging.ERROR, logger="astranotes.services.note_manager"):
        reader.list_notes()
    blob = "\n".join(rec.message for rec in caplog.records)
    assert str(tmp_path) not in blob
    assert "Traceback" not in blob
    assert reader_key.decode("ascii") not in blob


# ---------- NFR-01 performance budget (gap #8) ------------------------------


def test_list_and_search_500_notes_within_2s(manager: NoteManager) -> None:
    """NFR-01: list and search complete within 2 seconds for 500 notes.

    Mixed public/private corpus so the decrypt path is on the hot loop.
    """
    for i in range(500):
        manager.create_note(
            title=f"note {i:03d}",
            body=f"body content number {i} with searchable token findme{i % 10}",
            is_private=(i % 5 == 0),
        )
    t0 = time.perf_counter()
    notes = manager.list_notes()
    list_ms = (time.perf_counter() - t0) * 1000

    t1 = time.perf_counter()
    results = manager.search_notes("findme3")
    search_ms = (time.perf_counter() - t1) * 1000

    assert len(notes) == 500
    assert len(results) >= 50
    assert list_ms < 2000, f"list_notes took {list_ms:.0f}ms (NFR-01 budget: 2000)"
    assert search_ms < 2000, f"search_notes took {search_ms:.0f}ms (NFR-01 budget: 2000)"


# ---------- Tags duplication policy (gap #14) -------------------------------


def test_duplicate_tags_are_preserved_by_design(manager: NoteManager) -> None:
    """Refined-reqs: 'duplicate tags allowed, known limitation'.
    Pin the behavior so a future dedupe slip is caught."""
    note = manager.create_note(title="t", body="b", tags=["work", "work", "urgent"])
    loaded = manager.list_notes()[0]
    assert loaded.tags == ["work", "work", "urgent"]

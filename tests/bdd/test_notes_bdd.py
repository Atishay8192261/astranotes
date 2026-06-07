"""BDD step definitions for notes.feature (Gherkin / Given-When-Then).

Uses pytest-bdd. Each scenario in notes.feature maps to steps here.
Tests exercise the real NoteManager without mocked storage — SPR-03.
"""

from __future__ import annotations

import time
from pathlib import Path
from uuid import uuid4

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from astranotes.models.exceptions import NoteNotFoundError, PersistenceError, ValidationError
from astranotes.repositories.json_file import JsonFileRepository
from astranotes.services.note_manager import NoteManager
from astranotes.services.privacy import PrivacyService
from astranotes.services.validation import ValidationLayer

# Load all scenarios from the feature file.
scenarios("notes.feature")


# ── fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def manager(tmp_path: Path) -> NoteManager:
    return NoteManager(
        repository=JsonFileRepository(tmp_path),
        validation=ValidationLayer(),
        privacy=PrivacyService(PrivacyService.generate_key()),
    )


@pytest.fixture
def store(tmp_path: Path) -> dict:
    """Shared state dict passed between steps within one scenario."""
    return {"tmp_path": tmp_path, "manager": None, "last_note": None, "error": None}


# ── Background ──────────────────────────────────────────────────────────────


@given("the application has an empty note store", target_fixture="store")
def app_empty_store(tmp_path: Path) -> dict:
    mgr = NoteManager(
        repository=JsonFileRepository(tmp_path),
        validation=ValidationLayer(),
        privacy=PrivacyService(PrivacyService.generate_key()),
    )
    return {"tmp_path": tmp_path, "manager": mgr, "last_note": None, "error": None}


@given("the application has an encryption key configured")
def app_has_key(store: dict) -> None:
    # Background already wires a key; this step is a semantic label.
    assert store["manager"]._privacy is not None


@given("the application has no encryption key")
def app_no_key(store: dict) -> None:
    store["manager"] = NoteManager(
        repository=JsonFileRepository(store["tmp_path"]),
        validation=ValidationLayer(),
        privacy=None,
    )


# ── When — create ────────────────────────────────────────────────────────────


@when(parsers.parse('I create a note with title "{title}" and body "{body}"'))
def create_note(store: dict, title: str, body: str) -> None:
    store["last_note"] = store["manager"].create_note(title=title, body=body)


@when(parsers.parse('I try to create a note with title "{title}" and body "{body}"'))
def try_create_note(store: dict, title: str, body: str) -> None:
    try:
        store["manager"].create_note(title=title, body=body)
    except (ValidationError, PersistenceError) as exc:
        store["error"] = exc


@when(parsers.parse('I create a private note with title "{title}" and body "{body}"'))
def create_private_note(store: dict, title: str, body: str) -> None:
    store["last_note"] = store["manager"].create_note(
        title=title, body=body, is_private=True
    )


@when(parsers.parse('I try to create a private note with title "{title}" and body "{body}"'))
def try_create_private_note(store: dict, title: str, body: str) -> None:
    try:
        store["manager"].create_note(title=title, body=body, is_private=True)
    except PersistenceError as exc:
        store["error"] = exc


# ── Given — existing notes ───────────────────────────────────────────────────


@given(parsers.parse('there is a note titled "{title}" with body "{body}"'))
def existing_note(store: dict, title: str, body: str) -> None:
    store["last_note"] = store["manager"].create_note(title=title, body=body)


# ── When — update / delete / toggle / search / duplicate ─────────────────────


@when(parsers.parse('I update the note title to "{title}" and body to "{body}"'))
def update_note(store: dict, title: str, body: str) -> None:
    time.sleep(0.02)  # ensure modified_at advances
    store["last_note"] = store["manager"].update_note(
        store["last_note"].id, title=title, body=body
    )


@when(parsers.parse('I try to update the note title to "{title}"'))
def try_update_title(store: dict, title: str) -> None:
    try:
        store["manager"].update_note(store["last_note"].id, title=title)
    except ValidationError as exc:
        store["error"] = exc


@when("I delete the note")
def delete_note(store: dict) -> None:
    store["manager"].delete_note(store["last_note"].id)
    store["last_note"] = None


@when("I try to delete a note with a random UUID")
def try_delete_random(store: dict) -> None:
    try:
        store["manager"].delete_note(uuid4())
    except NoteNotFoundError as exc:
        store["error"] = exc


@when("I toggle the note to private")
def toggle_to_private(store: dict) -> None:
    store["last_note"] = store["manager"].set_private(store["last_note"].id, True)


@when(parsers.parse('I search for "{keyword}"'))
def do_search(store: dict, keyword: str) -> None:
    store["search_results"] = store["manager"].search_notes(keyword)


@when('I search for ""')
def do_search_empty(store: dict) -> None:
    store["search_results"] = store["manager"].search_notes("")


@when("I duplicate the note")
def duplicate_note(store: dict) -> None:
    store["duplicated"] = store["manager"].duplicate_note(store["last_note"].id)


# ── Then — assertions ────────────────────────────────────────────────────────


@then(parsers.parse("the note store contains {count:d} note"))
@then(parsers.parse("the note store contains {count:d} notes"))
def note_count(store: dict, count: int) -> None:
    assert len(store["manager"].list_notes()) == count


@then(parsers.parse('the note title is "{expected}"'))
def check_title(store: dict, expected: str) -> None:
    note = store["last_note"]
    assert note.title == expected


@then(parsers.parse('the note body is "{expected}"'))
def check_body(store: dict, expected: str) -> None:
    assert store["last_note"].body == expected


@then("the note is not private")
def check_not_private(store: dict) -> None:
    assert store["last_note"].is_private is False


@then("a validation error is raised")
def check_validation_error(store: dict) -> None:
    assert isinstance(store["error"], ValidationError), (
        f"Expected ValidationError, got {store['error']}"
    )


@then("a persistence error is raised")
def check_persistence_error(store: dict) -> None:
    assert isinstance(store["error"], PersistenceError), (
        f"Expected PersistenceError, got {store['error']}"
    )


@then("a not-found error is raised")
def check_not_found_error(store: dict) -> None:
    assert isinstance(store["error"], NoteNotFoundError), (
        f"Expected NoteNotFoundError, got {store['error']}"
    )


@then(parsers.parse('the raw file on disk does not contain "{text}"'))
def raw_file_has_no_plaintext(store: dict, text: str) -> None:
    files = list(store["tmp_path"].glob("*.json"))
    assert files, "No JSON file found on disk"
    for f in files:
        assert text not in f.read_text(), f"Plaintext '{text}' leaked to disk in {f.name}"


@then(parsers.parse('I can retrieve the note with body "{expected}"'))
def retrieve_body(store: dict, expected: str) -> None:
    notes = store["manager"].list_notes()
    bodies = [n.body for n in notes]
    assert expected in bodies, f"Expected body '{expected}' not found; got: {bodies}"


@then("the note's modified timestamp is later than its created timestamp")
def check_timestamps(store: dict) -> None:
    note = store["last_note"]
    assert note.modified_at > note.created_at


@then(parsers.parse('the search results contain "{title}"'))
def search_contains(store: dict, title: str) -> None:
    titles = [n.title for n in store["search_results"]]
    assert title in titles, f"'{title}' not in search results: {titles}"


@then(parsers.parse('the search results do not contain "{title}"'))
def search_not_contains(store: dict, title: str) -> None:
    titles = [n.title for n in store["search_results"]]
    assert title not in titles, f"'{title}' unexpectedly in search results: {titles}"


@then("the search results are empty")
def search_empty(store: dict) -> None:
    assert store["search_results"] == []


@then(parsers.parse('the note store contains a note titled "{title}"'))
def store_has_title(store: dict, title: str) -> None:
    titles = [n.title for n in store["manager"].list_notes()]
    assert title in titles, f"'{title}' not in note store: {titles}"

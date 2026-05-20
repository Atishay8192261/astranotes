"""Headless tests for the GUI presentation-tier logic (US-01, US-05, FR-04).

These exercise NotesController without importing customtkinter or Tk, which
is exactly the point of the controller/view split: the presentation tier's
behavior is provable with no display.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from astranotes.gui.controller import NotesController
from astranotes.repositories.json_file import JsonFileRepository
from astranotes.services.note_manager import NoteManager
from astranotes.services.privacy import PrivacyService
from astranotes.services.validation import ValidationLayer


@pytest.fixture
def controller(tmp_path: Path) -> NotesController:
    manager = NoteManager(
        repository=JsonFileRepository(tmp_path),
        validation=ValidationLayer(),
        privacy=PrivacyService(PrivacyService.generate_key()),
    )
    return NotesController(manager)


def test_create_note_reports_success(controller: NotesController) -> None:
    result = controller.create_note("grocery", "milk", is_private=False)
    assert result.ok
    assert "Saved note" in result.message


def test_create_note_rejects_blank_title(controller: NotesController) -> None:
    result = controller.create_note("   ", "body", is_private=False)
    assert not result.ok
    assert result.message


def test_tags_csv_is_parsed(controller: NotesController) -> None:
    controller.create_note("t", "b", is_private=False, tags_csv="work, urgent ,, ")
    note = controller.list_notes()[0]
    assert note.tags == ["work", "urgent"]


def test_private_note_round_trips_through_controller(controller: NotesController) -> None:
    controller.create_note("secret", "hidden", is_private=True)
    note = controller.list_notes()[0]
    assert note.is_private
    assert note.body == "hidden"


def test_delete_removes_note(controller: NotesController) -> None:
    controller.create_note("doomed", "x", is_private=False)
    note = controller.list_notes()[0]
    result = controller.delete_note(note.id)
    assert result.ok
    assert controller.list_notes() == []


def test_list_empty_returns_empty(controller: NotesController) -> None:
    assert controller.list_notes() == []


def test_search_through_controller(controller: NotesController) -> None:
    controller.create_note("Grocery", "milk eggs", is_private=False)
    controller.create_note("diary", "secret password", is_private=True)
    controller.create_note("unrelated", "x", is_private=False)
    titles = {n.title for n in controller.search_notes("password")}
    assert titles == {"diary"}
    assert controller.search_notes("") == []

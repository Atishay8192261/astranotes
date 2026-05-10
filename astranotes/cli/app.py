"""CLI shell for AstraNotes (FR-01, FR-05, FR-08, SPR-02).

Text menu. No external UI framework. Reads the data directory from
ASTRANOTES_DATA_DIR (default ~/.astranotes/notes) and the Fernet key from
ASTRANOTES_KEY. If no key is set a dev key is generated for the session with
a visible warning; the persistent-key strategy is the open SPR-01 ADR.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Callable, TextIO

from astranotes.models.exceptions import AstraNotesError
from astranotes.repositories.json_file import JsonFileRepository
from astranotes.services.note_manager import NoteManager
from astranotes.services.privacy import PrivacyService
from astranotes.services.validation import ValidationLayer

APP_NAME = "AstraNotes"
APP_VERSION = "0.2.0"
DEFAULT_DATA_DIR = Path.home() / ".astranotes" / "notes"


def resolve_data_dir() -> Path:
    raw = os.environ.get("ASTRANOTES_DATA_DIR")
    return Path(raw).expanduser() if raw else DEFAULT_DATA_DIR


def resolve_privacy(out: TextIO) -> PrivacyService:
    raw = os.environ.get("ASTRANOTES_KEY")
    if raw:
        return PrivacyService(raw.encode("utf-8"))
    out.write(
        "[warning] ASTRANOTES_KEY not set. Generating a dev key for this session only.\n"
        "          Private notes saved now will not be readable next launch.\n"
        "          Persistent key strategy is the open SPR-01 ADR (Sprint 1).\n\n"
    )
    return PrivacyService(PrivacyService.generate_key())


def build_main_menu() -> str:
    return (
        f"{APP_NAME} - main menu\n"
        "  1) Create a note\n"
        "  2) List notes\n"
        "  3) Settings\n"
        "  4) About\n"
        "  5) Quit\n"
    )


def render_settings(data_dir: Path, key_source: str) -> str:
    return (
        "Settings\n"
        f"  Data directory : {data_dir}\n"
        f"  Privacy key    : {key_source}\n"
        "  (Profile screen intentionally omitted - AstraNotes is single-user,\n"
        "   no accounts are part of the committed requirements.)\n"
    )


def render_about() -> str:
    return (
        f"{APP_NAME} {APP_VERSION}\n"
        "  Local-first, single-user Python note app.\n"
        "  Course   : CSEN 296B-2 (Spring 2026)\n"
        "  Storage  : one JSON file per note (FR-05).\n"
        "  Privacy  : Fernet symmetric encryption for private notes (SPR-01).\n"
    )


def prompt_create_note(manager: NoteManager, inp: Callable[[str], str], out: TextIO) -> None:
    title = inp("Title: ").strip()
    body = inp("Body (one line): ")
    private_raw = inp("Private? [y/N]: ").strip().lower()
    is_private = private_raw == "y"
    try:
        note = manager.create_note(title=title, body=body, is_private=is_private)
    except AstraNotesError as exc:
        out.write(f"Could not save note: {exc}\n")
        return
    out.write(f"Saved note {note.id}.\n")


def print_notes(manager: NoteManager, out: TextIO) -> None:
    try:
        notes = manager.list_notes()
    except AstraNotesError as exc:
        out.write(f"Could not load notes: {exc}\n")
        return
    if not notes:
        out.write("No notes yet.\n")
        return
    for note in notes:
        snippet = note.body.replace("\n", " ")
        if len(snippet) > 60:
            snippet = snippet[:57] + "..."
        flag = "[private]" if note.is_private else "         "
        out.write(f"  {flag} {note.modified_at:%Y-%m-%d %H:%M}  {note.title}  -  {snippet}\n")


def run(
    inp: Callable[[str], str] = input,
    out: TextIO = sys.stdout,
) -> None:
    data_dir = resolve_data_dir()
    privacy = resolve_privacy(out)
    key_source = "ASTRANOTES_KEY" if os.environ.get("ASTRANOTES_KEY") else "dev key (session only)"

    repository = JsonFileRepository(data_dir)
    manager = NoteManager(
        repository=repository,
        validation=ValidationLayer(),
        privacy=privacy,
    )

    while True:
        out.write("\n" + build_main_menu())
        choice = inp("Choose [1-5]: ").strip()
        if choice == "1":
            prompt_create_note(manager, inp, out)
        elif choice == "2":
            print_notes(manager, out)
        elif choice == "3":
            out.write(render_settings(data_dir, key_source))
        elif choice == "4":
            out.write(render_about())
        elif choice == "5":
            out.write("Goodbye.\n")
            return
        else:
            out.write("Pick 1, 2, 3, 4, or 5.\n")

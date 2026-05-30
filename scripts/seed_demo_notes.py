"""Seed a fresh data directory with 12 demo notes for presentation/testing.

Usage:
    python scripts/seed_demo_notes.py [--data-dir demo-data] [--passphrase changeme123]

Defaults write to ./demo-data so the user's real notes at ~/.astranotes are
untouched. Run the app against the demo dir with:

    ASTRANOTES_DATA_DIR=demo-data \\
    ASTRANOTES_PASSPHRASE_PATH=demo-data/passphrase.json \\
    python -m astranotes

The passphrase is printed so a presentation audience can see it; obviously
not for real use.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from astranotes.repositories.json_file import JsonFileRepository  # noqa: E402
from astranotes.services.note_manager import NoteManager  # noqa: E402
from astranotes.services.passphrase import PassphraseStore  # noqa: E402
from astranotes.services.validation import ValidationLayer  # noqa: E402


DEMO_NOTES = [
    {"title": "Welcome to AstraNotes",
     "body": "This is your local-first notes app. Notes live in JSON files on disk. Toggle the Private switch to encrypt a note's body at rest.",
     "tags": ["welcome", "intro"]},
    {"title": "Grocery list",
     "body": "milk, eggs, sourdough, kale, lentils, olive oil, lemons, parmesan, cherry tomatoes",
     "tags": ["personal", "shopping"]},
    {"title": "Monday standup notes",
     "body": "Ship the search bar fix. Pair on the controller refactor with R. Review PR #42 by EOD. Tomorrow: planning session 10am.",
     "tags": ["work", "meeting"]},
    {"title": "Reading list",
     "body": "Designing Data-Intensive Applications - finish ch 8.\nThe Pragmatic Programmer - re-read ch 4.\nA Philosophy of Software Design - start.",
     "tags": ["reading", "personal"]},
    {"title": "Pasta carbonara",
     "body": "200g spaghetti. 100g guanciale. 2 yolks + 1 whole egg. 60g pecorino, finely grated. Black pepper. Reserve pasta water. Off heat, toss egg mix with pasta + water; fold in guanciale fat.",
     "tags": ["recipes", "personal"]},
    {"title": "Project ideas",
     "body": "1. Markdown-export plugin for AstraNotes.\n2. Background indexer for faster search.\n3. Sync via a tiny self-hosted endpoint (later, optional).",
     "tags": ["ideas", "work"]},
    {"title": "Apartment maintenance",
     "body": "Replace water filter (3-month cycle). Schedule HVAC service in October. Re-grout the bathroom this weekend.",
     "tags": ["personal", "todo"]},
    {"title": "Quote — Dijkstra",
     "body": "\"Simplicity is prerequisite for reliability.\" — Edsger W. Dijkstra. Keep this in mind when adding new abstractions.",
     "tags": ["quotes", "engineering"]},

    # --- private notes (encrypted at rest) ---
    {"title": "Vault: WiFi credentials",
     "body": "Home network SSID: maple-cottage-5g\nPassword: oak-river-cedar-99\nGuest SSID: maple-guest / password: visitor2026",
     "tags": ["private", "credentials"],
     "is_private": True},
    {"title": "Vault: Insurance policy",
     "body": "Auto policy #A-8821-2026. Renews March 14. Agent: Priya, (415) 555-0143. Roadside assist included, glass +$50 deductible.",
     "tags": ["private", "finance"],
     "is_private": True},
    {"title": "Vault: Therapy reflections",
     "body": "Reminder: the project's deadline is not a measure of self-worth. Three things that went well today: shipped the PR, called mom, walked Charlie before 8am.",
     "tags": ["private", "journal"],
     "is_private": True},
    {"title": "Vault: Future-me letter",
     "body": "Hey - when you read this you'll be done with the quarter. Whatever happens with the grade, you finished the thing. That counts. Take a real weekend off before the next one starts.",
     "tags": ["private", "journal"],
     "is_private": True},
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed demo notes")
    parser.add_argument("--data-dir", default="demo-data", type=Path)
    parser.add_argument("--passphrase", default="changeme123")
    parser.add_argument(
        "--clean", action="store_true", help="wipe data-dir before seeding"
    )
    args = parser.parse_args()

    data_dir: Path = args.data_dir
    if args.clean and data_dir.exists():
        shutil.rmtree(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)

    pass_path = data_dir / "passphrase.json"
    store = PassphraseStore(pass_path)
    if store.exists():
        privacy = store.unlock(args.passphrase)
    else:
        privacy = store.initialize(args.passphrase)

    manager = NoteManager(
        repository=JsonFileRepository(data_dir),
        validation=ValidationLayer(),
        privacy=privacy,
    )

    for entry in DEMO_NOTES:
        manager.create_note(
            title=entry["title"],
            body=entry["body"],
            tags=entry.get("tags", []),
            is_private=bool(entry.get("is_private", False)),
        )

    print(f"Seeded {len(DEMO_NOTES)} notes into {data_dir}")
    print(f"Passphrase: {args.passphrase}")
    print("Run the app:")
    print(
        f"  ASTRANOTES_DATA_DIR={data_dir} "
        f"ASTRANOTES_PASSPHRASE_PATH={pass_path} python -m astranotes"
    )


if __name__ == "__main__":
    main()

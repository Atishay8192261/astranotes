# AstraNotes

A local-first, single-user note-taking application with encryption-at-rest for private notes.

Notes live as one JSON file per note in a local data directory. Notes flagged
as private have their bodies encrypted with [Fernet][fernet] (authenticated
AES-128-CBC + HMAC-SHA256) before any disk write. The Fernet key is derived
from a user-supplied passphrase via PBKDF2-HMAC-SHA256 (600,000 iterations,
16-byte random salt) and kept only in memory. The key itself is never
persisted; only the salt and a Fernet-encrypted verifier blob land on disk.

## Architecture

Three tiers with dependency injection at every seam:

```
gui/  (CustomTkinter view + widget-free controller)
  │
services/   NoteManager  ·  PrivacyService  ·  ValidationLayer
  │
repositories/   NoteRepository (ABC)  ·  JsonFileRepository
```

The view holds no business logic, the logic tier holds no widgets, and the
repository interface means the storage backend can change without touching
the services. The 78 unit tests run headlessly (no Tk required) by exercising
the controller and services directly.

## Features

- Create / edit / delete notes (UUID, UTC timestamps, free-form tags).
- Mark any note as private — body is Fernet-encrypted at rest.
- Toggle private ↔ public on an existing note; failed decryption leaves the
  note encrypted rather than silently corrupting it.
- Case-insensitive keyword search across titles and bodies; private notes are
  decrypted before matching, and notes that fail to decrypt are skipped.
- Sorted by `modified_at` descending (ties broken by `created_at`).
- Auto-creates the data directory on first launch; skips corrupt JSON files
  on startup with an error logged.

## Setup

```bash
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

The GUI requires a Python build with Tcl/Tk. On macOS with Homebrew:

```bash
brew install python-tk@3.11
```

## Run

```bash
python -m astranotes
```

On first launch the app prompts for a passphrase the first time you save a
private note. The passphrase derives the encryption key in memory only and
is never written to disk; forgetting it means the private notes cannot be
recovered (by design — there is no backdoor).

### Seed demo data

```bash
python scripts/seed_demo_notes.py --clean --passphrase <pick-anything>
ASTRANOTES_DATA_DIR=demo-data \
ASTRANOTES_PASSPHRASE_PATH=demo-data/passphrase.json \
python -m astranotes
```

This populates `./demo-data/` with 12 example notes (8 public, 4 private),
leaving your real `~/.astranotes/` directory untouched. The passphrase is
required (no default) so nothing demo-y leaks into source control.

## Test

```bash
pytest -q
```

78 tests; 5 legacy CLI tests are quarantined behind `--run-cli`. All tests
are headless and use only `tmp_path` fixtures + real services (no mocked
storage in security-critical paths).

## Configuration

| Environment variable | Default | Purpose |
|----------------------|---------|---------|
| `ASTRANOTES_DATA_DIR` | `~/.astranotes/notes` | Where note JSON files live. |
| `ASTRANOTES_PASSPHRASE_PATH` | `~/.astranotes/passphrase.json` | Salt + verifier file location. |
| `ASTRANOTES_KEY` | unset | Legacy override: a 32-byte urlsafe-base64 Fernet key. When set, the passphrase flow is bypassed. |

## Dependencies

- [`cryptography`][cryptography] (Apache 2.0 / BSD) — Fernet + PBKDF2.
- [`customtkinter`][ctk] (CC0-1.0) — desktop GUI widgets.
- [`pytest`][pytest] (MIT) — test runner.

[fernet]: https://cryptography.io/en/latest/fernet/
[cryptography]: https://github.com/pyca/cryptography
[ctk]: https://github.com/TomSchimansky/CustomTkinter
[pytest]: https://github.com/pytest-dev/pytest

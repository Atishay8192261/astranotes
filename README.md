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
the services. The 95 unit tests run headlessly (no Tk required) by exercising
the controller and services directly.

## Features

- Create / edit / delete / **duplicate** notes (UUID, UTC timestamps, tags).
- **Master vault**: a single passphrase unlocks every secured note. Change the
  passphrase in-app (rotation requires proving you know the current one).
- Mark any note as private — body is Fernet-encrypted at rest. Toggle
  private ↔ public; failed decryption leaves the note encrypted rather than
  silently corrupting it.
- **Apple Notes-style sidebar**: slim rows grouped by date (Today / Yesterday /
  Previous 7 Days / …) with a dedicated **Secured** section and "Unlock All".
- Case-insensitive keyword search across titles and bodies; private notes are
  decrypted before matching, and notes that fail to decrypt are skipped.
- **Keyboard shortcuts** (⌘/Ctrl + N / S / F), live word & character count,
  and an unsaved-changes indicator.
- **System panel**: live telemetry (note counts, storage used, encryption
  status). Every UI action is logged to `~/.astranotes/events.log`.
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
astranotes

// or

python -m astranotes
```

On first launch the app prompts for a passphrase the first time you save a
private note. The passphrase derives the encryption key in memory only and
is never written to disk; forgetting it means the private notes cannot be
recovered (by design — there is no backdoor).

## Test

```bash
pytest -q
```

95 tests; 5 legacy CLI tests are quarantined behind `--run-cli`. All tests
are headless and use only `tmp_path` fixtures + real services (no mocked
storage in security-critical paths).

## Documentation

Full SDLC artifacts live under [`docs/`](docs/):

| Area | Files |
|------|-------|
| Requirements | [`PRD.md`](docs/requirements/PRD.md) (functional + non-functional + security reqs) |
| Traceability | [`traceability-matrix.md`](docs/requirements/traceability-matrix.md) (every requirement → UML → test) |
| UML | [class](docs/uml/class-diagram.md) · [object](docs/uml/object-diagram.md) · [use-case](docs/uml/use-case-diagram.md) · [activity](docs/uml/activity-diagram.md) · [deployment](docs/uml/deployment-diagram.md) |
| Testing | [`tdd-log.md`](docs/testing/tdd-log.md) (Red-Green-Refactor) · [`bdd-acceptance-criteria.md`](docs/testing/bdd-acceptance-criteria.md) (Gherkin) |
| AI use | [`prompt-log.md`](docs/ai-log/prompt-log.md) (architectural decisions made with AI + human oversight) |
| Operations | [`RUNBOOK.md`](RUNBOOK.md) (deploy / run / troubleshoot) |

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

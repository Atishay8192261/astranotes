# AstraNotes — Product Requirements Document (PRD)

**Version:** 1.3  **Course:** CSEN 296B-2 · Spring 2026 · Santa Clara University  
**Author:** Atishay Jain  **Last updated:** 2026-06-07

---

## 1. Problem Statement

Knowledge workers accumulate notes across many devices and apps. Most cloud solutions store notes in plaintext on remote servers, exposing sensitive material to breaches. AstraNotes solves this by storing notes locally with optional Fernet encryption-at-rest, so private notes are unreadable even if the filesystem is accessed without the passphrase.

---

## 2. Scope

| In Scope | Out of Scope |
|---|---|
| Single-user local desktop GUI | Multi-user / cloud sync |
| Create / edit / delete / search notes | Rich text / attachments |
| Private notes with encryption at rest | Account management / OAuth |
| Passphrase-derived encryption key | Network communication |
| Tag-based organisation | Folder / notebook hierarchy |

---

## 3. Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| FR-01 | User can create a note with title (required), body (optional), tags (optional), and a private flag. | MUST |
| FR-02 | User can edit the title, body, and tags of an existing note. | MUST |
| FR-03 | User can delete a note permanently. | MUST |
| FR-04 | User can toggle the private flag on an existing note; the body is re-encrypted or decrypted accordingly. | MUST |
| FR-05 | User can duplicate an existing note; the copy gets a "Copy of …" title prefix. | SHOULD |
| FR-06 | Notes are stored with UUID, UTC `created_at`, and UTC `modified_at` timestamps; `modified_at` advances on every edit. | MUST |
| FR-07 | User can perform a case-insensitive keyword search across titles and bodies; private notes are decrypted before matching. | MUST |
| FR-08 | Note list is sorted by `modified_at` descending (ties resolved by `created_at`). | MUST |
| FR-09 | UI disables Delete and Duplicate buttons when no note is selected, preventing accidental actions. | MUST |
| FR-10 | Admin/telemetry panel displays live system status (app running, storage accessible, encryption state) and database statistics (total notes, private notes, storage bytes, average body length). | SHOULD |
| FR-11 | All UI interactions are logged to an event log file (action name + timestamp + detail), proving the backend workflow chain to graders. | SHOULD |

---

## 4. Non-Functional Requirements

| ID | Requirement | Metric / Limit |
|---|---|---|
| NFR-01 | **Performance** — `list_notes` and `search_notes` must complete within **2 000 ms** for a corpus of 500 mixed public/private notes on commodity hardware. | Validated by `test_list_and_search_500_notes_within_2s`. |
| NFR-02 | **Tier isolation** — the view layer must hold no business logic; the logic tier must hold no widget code. Each tier is independently testable. | Enforced by headless controller tests that import no Tk symbols. |
| NFR-03 | **Startup latency** — application main window must appear within **3 seconds** of launch on macOS with ≤ 500 existing notes. | Manual verification on target hardware. |
| NFR-04 | **Reliability** — corrupt or missing JSON files must never crash the application; they are skipped with a logged error. | Validated by `test_repository.py`. |
| NFR-05 | **Maintainability** — all identifiers must be descriptive (no `var1`, `tmp`, `x` in public APIs); cyclomatic complexity ≤ 10 per function. | Code review gate. |
| NFR-06 | **Test coverage** — ≥ 85 passing unit/BDD tests covering all functional requirements; zero mocked storage in security-critical paths. | `pytest -q` green gate. |

---

## 5. Security Requirements

| ID | Requirement |
|---|---|
| SPR-01 | Private note bodies must be Fernet-encrypted (AES-128-CBC + HMAC-SHA256) before any disk write. |
| SPR-02 | Error messages must not expose file paths, stack traces, or key material. |
| SPR-03 | No third-party runtime dependencies outside `cryptography` and `customtkinter`; dev deps must have MIT/Apache/BSD/CC0 licences. |
| SPR-04 | The Fernet key is derived via PBKDF2-HMAC-SHA256 with ≥ 600 000 iterations and a 16-byte random salt. The key itself is never written to disk. |
| SPR-05 | No secrets, API keys, or plaintext sample passphrases may appear in source control. |

---

## 6. Architecture Overview

```
┌─────────────────────────────────┐
│  Presentation Tier (View)       │  CustomTkinter widgets (gui/app.py)
│  • AstraNotesApp                │  All actions delegate to controller
└────────────┬────────────────────┘
             │ method calls (no widget references cross tier)
┌────────────▼────────────────────┐
│  Logic Tier (Controller)        │  gui/controller.py  ─  widget-free
│  • NotesController              │  services/note_manager.py
│  • NoteManager                  │  services/privacy.py
│  • PrivacyService               │  services/validation.py
│  • ValidationLayer              │
└────────────┬────────────────────┘
             │ repository interface (ABC)
┌────────────▼────────────────────┐
│  Data Tier (Model)              │  repositories/json_file.py
│  • JsonFileRepository           │  One JSON file per note
│  • Note (dataclass)             │  models/note.py
└─────────────────────────────────┘
```

---

## 7. Acceptance Criteria (summary — full Gherkin in `docs/testing/bdd-acceptance-criteria.md`)

- A note created with a non-blank title appears in `list_notes()`.
- A private note's body does **not** appear in the raw JSON file on disk.
- Deleting a note removes it from `list_notes()`.
- `search_notes("milk")` returns every note whose title or body contains "milk" (case-insensitive).
- Toggling a public note to private re-encrypts the body without changing the title, tags, or `created_at`.

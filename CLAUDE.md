# CLAUDE.md - AstraNotes Project Knowledge Transfer

## Project Overview

AstraNotes is a secure, modular, local-first note-taking application built in Python. It is the quarter-long project for CSEN 296B-2 (AI-Driven Software Development) at Santa Clara University, Spring 2026.

**Student:** Atishay Jain
**Technical Path:** Python
**Quarter:** Spring 2026 (Weeks 1-11, March 30 - June 8)
**Current Status:** Week 9 (project complete: FR-01..FR-08 realized; ADR-005 resolved with PBKDF2 master passphrase; UI polished; 12-note seed for demos; 78 tests passing, 5 CLI quarantined.)

## Architecture

AstraNotes is a **3-tier application** (ADR-006, Week 7.2): presentation tier (`gui/` - CustomTkinter view + widget-free controller), logic tier (`services/`), data tier (`repositories/` + filesystem). The CLI (`cli/`) is retained only as a developer/test harness. Within the logic/data tiers the original layered components are unchanged:

| Component | Responsibility |
|-----------|---------------|
| **Note Entity** | Python dataclass: id (UUID), title (str), body (str), is_private (bool), created_at (datetime, UTC), modified_at (datetime, UTC), tags (list[str]) |
| **NoteRepository (ABC)** | Abstract interface with save(), get(), list_all(), update(), delete() |
| **JsonFileRepository** | Concrete adapter - one {id}.json file per note in a local data directory |
| **PrivacyService** | Encrypts/decrypts private note bodies using Fernet (cryptography library). Standalone - no storage logic. |
| **ValidationLayer** | Rejects empty/whitespace-only titles, malformed notes before they reach persistence |
| **Version History Service** | Stores snapshots of prior note states (deferred to later sprint) |
| **NoteManager** | Orchestrates validation, privacy, versioning, and storage into a single workflow |
| **NotesController** | Presentation-tier logic (`gui/controller.py`). Widget-free, headlessly testable; delegates to NoteManager via the same DI seam the CLI used. |
| **AstraNotesApp** | CustomTkinter view (`gui/app.py`). Thin shell - no business rule, encryption, or file path lives here. |

**Key architectural rules:**
- 3-tier separation: the GUI view talks only to NotesController, which talks only to NoteManager. The pivot (ADR-006) did not touch the logic or data tiers.
- PrivacyService sits BETWEEN business logic and storage. Private note bodies are NEVER written to disk in plaintext.
- Every component can be tested independently via dependency injection (NFR-03).
- The repository interface is abstract - storage backend can change without touching business logic.
- Domain exceptions: NoteNotFoundError, PersistenceError, ValidationError. No raw tracebacks exposed to user.

## Project Directory Structure (Target)

```
astranotes/
  __init__.py
  __main__.py              # Entry point: python -m astranotes (launches GUI; Tk-missing fallback)
  config.py                # resolve data dir + Fernet key from env (shared by GUI/CLI/tests)
  gui/
    __init__.py
    controller.py          # NotesController - presentation-tier logic, widget-free
    app.py                 # AstraNotesApp - CustomTkinter view (3-tier frontend)
  models/
    __init__.py
    note.py                # Note dataclass
    exceptions.py          # NoteNotFoundError, PersistenceError, ValidationError
  repositories/
    __init__.py
    base.py                # NoteRepository ABC
    json_file.py           # JsonFileRepository
  services/
    __init__.py
    privacy.py             # PrivacyService (Fernet encrypt/decrypt)
    validation.py          # ValidationLayer
    note_manager.py        # NoteManager orchestrator
  cli/
    __init__.py
    app.py                 # retained dev/test harness only (not the user entry point)
tests/
  __init__.py
  test_note.py
  test_repository.py
  test_privacy.py
  test_validation.py
  test_note_manager.py
  test_cli.py
  test_gui_controller.py   # headless presentation-tier tests (no Tk)
planning/
  requirements.md          # Week 1.2 original requirements
  refined-requirements.md  # Week 3.1 refined requirement baseline
  user-stories.md          # US-01 through US-08
  backlog.md               # Prioritized backlog
  sprint-zero-plan.md      # Sprint Zero objectives and exit criteria
docs/
  architecture-decision-log.md
  prompt-log.md
submissions/               # PDF submissions for class (reference only)
  Week1_2_Architecture_Decision_Log.pdf
  Week1_2_Initial_Requirement_Set.pdf
  Week2_1_Working_Agreement.pdf
  Week2_1_Definition_of_Done.pdf
  Week2_2_Backlog_Sprint_Zero.pdf
  Week3_1_Refined_Requirement_Baseline.pdf
pyproject.toml
.gitignore
README.md
```

## Requirements Summary (Refined - Week 3.1)

### Functional Requirements
- **FR-01:** Create note with non-empty title (whitespace-only rejected), optional body. UUID + timestamps auto-assigned.
- **FR-02:** Edit title/body. modified_at updates on save. created_at and UUID immutable.
- **FR-03:** Delete by UUID. Non-existent UUID returns clear error, no silent fail.
- **FR-04:** Toggle is_private. True = encrypt body via PrivacyService before disk write. False = re-save as plaintext. If decryption fails during toggle, operation fails and note stays encrypted.
- **FR-05:** Persist one-file-per-note. On startup, load valid files, skip corrupt ones with error logged. Auto-create data directory on first launch.
- **FR-06:** Metadata: UUID, created_at (UTC), modified_at (UTC), tags (list[str], case-sensitive, may be empty).
- **FR-07:** Keyword search across titles and bodies. Case-insensitive, plain string matching (not regex). Decrypted private notes included. Failed decryptions excluded with error logged. Empty collection returns empty list.
- **FR-08:** Sort by modified_at descending. Tiebreaker: created_at descending.

### Non-Functional Requirements
- **NFR-01:** List/search within 2 seconds for 500 notes (8 GB RAM, SSD, dual-core CPU).
- **NFR-02:** Separation of concerns - NoteManager, NoteRepository, PrivacyService independently testable.
- **NFR-03:** Startup to first display within 3 seconds on NFR-01 hardware.

### Security/Privacy/Governance Requirements
- **SPR-01:** Private bodies encrypted with Fernet before any disk write. Key NEVER in source code or data directory. Key management strategy documented in ADL before Sprint 1.
- **SPR-02:** All storage exceptions (FileNotFoundError, PermissionError, JSONDecodeError) translated to app-level messages. No file paths, stack traces, or internal state exposed.
- **SPR-03:** Core components have at least one automated unit test before each milestone. Tests run without external dependencies (use temp dirs, test keys).
- **SPR-04:** Third-party libs in pyproject.toml with pinned version, purpose comment, confirmed permissive license (MIT/Apache/BSD).

## User Stories (Priority Order = Backlog Order)

1. **US-08:** Project Setup and Structural Readiness (NFR-02, NFR-03, SPR-04)
2. **US-01:** Create a New Note (FR-01, FR-07)
3. **US-04:** Mark a Note as Private (FR-04, SPR-01)
4. **US-05:** Persist and Restore Notes Across Sessions (FR-05, FR-06, NFR-03)
5. **US-02:** Edit an Existing Note (FR-02)
6. **US-03:** Delete a Note (FR-03)
7. **US-06:** Search Notes by Keyword (FR-08, NFR-01)
8. **US-07:** Handle Storage Errors Gracefully (SPR-02, SPR-03)

## Sprint Zero Scope (Current Phase)

Sprint Zero is NOT a feature sprint. No user stories are marked Done. The goal is project foundation.

### Objectives:
1. **Project structure** - Create the directory layout above. pyproject.toml with cryptography + pytest. .gitignore for Python.
2. **Note dataclass** - Implement in models/note.py with all fields. Unit test for instantiation, auto-timestamps, valid UUID.
3. **NoteRepository ABC** - Abstract base class in repositories/base.py with save/get/list_all/update/delete signatures.
4. **JsonFileRepository** - Concrete adapter in repositories/json_file.py. One JSON file per note. Unit test for save/load round-trip using temp directory.
5. **PrivacyService skeleton** - encrypt(body) and decrypt(data) using Fernet in services/privacy.py. Unit test for round-trip. Hardcoded test key acceptable ONLY in tests.
6. **ValidationLayer skeleton** - Title non-empty (strip whitespace) in services/validation.py. Raises ValidationError. Unit test.
7. **Planning artifacts** - planning/ folder with all .md files mirroring class submissions.
8. **Docs** - architecture-decision-log.md and prompt-log.md in docs/.

### Sprint Zero Exit Criteria:
- Layered directory exists with all modules
- Note dataclass and NoteRepository ABC defined and importable
- JsonFileRepository passes save/load round-trip test
- PrivacyService passes encrypt/decrypt round-trip test
- ValidationLayer passes title validation test
- pyproject.toml lists dependencies with licenses
- pytest runs with all tests passing
- planning/ and docs/ folders populated

## Known Edge Cases (Must Handle)

**Storage:**
- Corrupt/malformed JSON on startup: skip file, log error, load rest
- Data directory missing on first launch: auto-create
- UUID in filename vs UUID in JSON body mismatch: JSON body is authoritative, log warning

**Privacy:**
- Key changed since encryption: catch failure, surface clear error, never return garbled content
- PrivacyService unavailable or key missing: raise error, block read, never return unencrypted private content
- Toggle private-to-public when decryption fails: fail with error, do not silently succeed

**Validation:**
- Whitespace-only title: strip then reject as empty
- Duplicate tags: allowed (preserves user intent), noted as known limitation

**Search:**
- Empty collection: return empty list, not error
- Special characters in keyword: use plain string matching, not regex

## Dependencies

| Library | Purpose | License |
|---------|---------|---------|
| cryptography | Fernet symmetric encryption for private notes (SPR-01) | Apache 2.0 / BSD |
| customtkinter | GUI presentation tier - 3-tier desktop frontend (NFR-02, ADR-006) | CC0-1.0 (SPR-04 exception, logged in ADR-006) |
| pytest | Unit testing framework (SPR-03) | MIT |

## Rules for Development

These come from the Working Agreement (Week 2.1) and Definition of Done (Week 2.1):

1. **Every task must trace to a requirement ID** (FR-01 through SPR-04). Work that cannot be traced is rejected or triggers a formal requirement update.
2. **Architecture alignment** - All code must be consistent with the layered architecture. Any deviation is logged as an Architecture Decision before acceptance.
3. **Privacy gate** - Any code touching note storage/retrieval/display must explicitly consider encryption. Private note bodies NEVER in plaintext on disk.
4. **Error handling** - Every component that reads/writes disk includes explicit handling for NoteNotFoundError, PersistenceError, ValidationError.
5. **No scope creep** - Do not add features not in the 15 committed requirements. New ideas go to backlog through formal evaluation.
6. **Testing required** - Automated test or documented manual verification for every component before milestone delivery. Tests must not depend on real infrastructure.
7. **Realistic scope** - This is a solo-developer, one-quarter project. Reject unnecessary complexity or external dependencies.

## What Has Been Completed

| Week | Deliverable | Status |
|------|-------------|--------|
| 1.1 | Waterfall Gantt Chart (baseline + change request impact) | Done |
| 1.2 | Architecture Decision Log (3-round prompt refinement) | Done |
| 1.2 | Initial Requirement Set (15 requirements: FR, NFR, SPR) | Done |
| 2.1 | Working Agreement (AI collaboration rules, scope discipline) | Done |
| 2.1 | Definition of Done (9 criteria checklist) | Done |
| 2.2 | User Stories (US-01 through US-08 with acceptance criteria) | Done |
| 2.2 | Prioritized Backlog (8 stories ordered by dependency/risk) | Done |
| 2.2 | Sprint Zero Plan (6 objectives, exit criteria, risk table) | Done |
| 3.1 | Refined Requirement Baseline (15 refined reqs, 6 ambiguities, 11 edge cases) | Done |
| Sprint Zero | Project setup, skeleton code, 21 unit tests passing | Done |
| 4.1 | UML Structural Design (class diagram + structural rationale, bundled into Week 4.2 package) | Done |
| 4.2 | Complete UML Design Package (class, object, use case, activity, deployment + rationale + AI reflection) | Done |
| 5.2 | Requirements-to-UML Traceability Matrix | Done |
| 6.1 | Development Environment + first realization slices (US-01 create, US-05 list; CLI shell) | Done |
| 6.1 | Closed Week 5.2 gaps: activity-search/startup/toggle-privacy diagrams, SPR-04 license labels | Done |
| 7.2 | Testing Strategy + first test set (40 tests passing) | Done |
| 7.2 | 3-tier GUI pivot to CustomTkinter (ADR-006); UML/docs updated | Done |
| 8.1 | Collaborative Git workflow: US-06/FR-07 keyword search merged via PR #1 (46 tests passing) | Done |
| 9.1 | Test improvement log (gap #4 brittle SPR-01 assertion replaced); 14-gap audit closed in PR #2; FR-02 edit, FR-03 delete-via-manager, FR-04 toggle landed | Done |
| 9.1 | ADR-005 resolved: master passphrase + PBKDF2 (PR #3); GUI polish + 12-note demo seed (PR #4) | Done |

## Upcoming Class Milestones

| Week | Topic | Expected Deliverable |
|------|-------|---------------------|
| 3.2 (Apr 15) | Ethics and Governance | Governance and ethics review memo |
| 4.1 (Apr 20) | UML Structural Design | Class diagram and structural rationale |
| 4.2 (Apr 22) | UML Behavioral Design | Sequence/state diagrams |
| 5.1 (Apr 27) | OOAD Validation | Design validation memo |
| 5.2 (Apr 29) | Midterm 1 | Assessment on SDLC, requirements, design |
| 6.1 (May 4) | From Design to Development | First realization slice with traceability |
| 6.2 (May 6) | Quality in Development | Development quality audit |

## How to Run

```bash
# Setup
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -e ".[dev]"

# Run tests (40 passing; headless - no display needed)
pytest

# Run the GUI app (requires a Python build with Tcl/Tk)
python -m astranotes
# If it reports missing _tkinter on macOS/Homebrew:
#   brew install python-tk@3.11
```

The 40-test suite is fully headless - the presentation tier is split so
`NotesController` is tested without Tk. Only launching the GUI window needs
Tcl/Tk; `python -m astranotes` prints the exact install hint if it is absent.

## graphify

This project has a graphify knowledge graph at graphify-out/.

Rules:
- Before answering architecture or codebase questions, read graphify-out/GRAPH_REPORT.md for god nodes and community structure
- If graphify-out/wiki/index.md exists, navigate it instead of reading raw files
- For cross-module "how does X relate to Y" questions, prefer `graphify query "<question>"`, `graphify path "<A>" "<B>"`, or `graphify explain "<concept>"` over grep — these traverse the graph's EXTRACTED + INFERRED edges instead of scanning files
- After modifying code files in this session, run `graphify update .` to keep the graph current (AST-only, no API cost)

# AstraNotes - Architecture Decision Log

**Student:** Atishay Jain | **Technical Path:** Python

---

## ADR-001: Layered Architecture with Repository Pattern
**Date:** April 1, 2026 (Week 1.2)
**Status:** Accepted

**Context:** AstraNotes needs a modular structure that separates concerns, supports testing in isolation, and allows future extension (e.g., VoiceNote, ImageNote) without rewriting storage or encryption.

**Decision:** Adopt a layered architecture with seven components: Note Entity, NoteRepository (ABC), JsonFileRepository, PrivacyService, ValidationLayer, Version History Service, and NoteManager.

**Rationale:** Each component has a single responsibility. The repository abstraction means storage can change from JSON to SQLite without touching business logic. Isolating PrivacyService from storage prevents encryption logic from leaking into persistence.

**Traces to:** NFR-02, NFR-03

---

## ADR-002: Fernet Symmetric Encryption for Private Notes
**Date:** April 1, 2026 (Week 1.2)
**Status:** Accepted

**Context:** Notes marked private need encryption at rest. The solution must be simple, auditable, and achievable with minimal external dependencies for a solo developer.

**Decision:** Use Fernet symmetric encryption from Python's cryptography library. PrivacyService handles all encrypt/decrypt operations independent of storage.

**Rationale:** Fernet provides authenticated encryption with a single key. It is well-documented, widely used, and available under a permissive license (Apache 2.0 / BSD).

**Traces to:** FR-04, SPR-01

---

## ADR-003: One JSON File Per Note for Local Persistence
**Date:** April 1, 2026 (Week 1.2)
**Status:** Accepted

**Context:** Notes need to persist between sessions on local disk. The persistence format should be human-readable for debugging and simple to implement.

**Decision:** Each note is serialized as an individual {id}.json file in a designated data directory. No external database server required.

**Rationale:** JSON is human-readable, Python's json module is in the standard library, and one-file-per-note avoids locking issues. For a 500-note local app, this is sufficient.

**Note (Week 3.1):** The refined requirement baseline (FR-05) separates the persistence requirement from the storage format decision. JSON is a design choice documented here, not a requirement constraint.

**Traces to:** FR-05, FR-06

---

## ADR-004: Domain-Specific Exception Hierarchy
**Date:** April 1, 2026 (Week 1.2)
**Status:** Accepted

**Context:** Storage and validation failures need consistent handling. Raw Python exceptions (FileNotFoundError, json.JSONDecodeError) should not reach the user.

**Decision:** Define three domain exceptions - NoteNotFoundError, PersistenceError, ValidationError. Catch low-level I/O failures at the adapter boundary and translate them.

**Rationale:** Clean error boundaries make the system testable and ensure user-facing messages are always non-technical per SPR-02.

**Traces to:** SPR-02

---

## ADR-005: Key Management Strategy (PENDING)
**Date:** April 13, 2026 (Week 3.1)
**Status:** Pending - must be resolved before Sprint 1

**Context:** SPR-01 requires Fernet encryption but the key must never be stored in source code or the notes data directory. The specific storage mechanism needs to be decided.

**Options under consideration:**
- Environment variable (simplest, works across OS)
- OS keychain (more secure, platform-dependent)
- User prompt at startup (most secure, less convenient)

**Decision:** TBD. Sprint Zero will use a hardcoded test key in the test suite only. Production key strategy documented here before Sprint 1 begins.

**Traces to:** SPR-01

---

## ADR-006: Pivot Presentation Tier to a 3-Tier GUI (CustomTkinter)
**Date:** May 17, 2026 (Week 7.2)
**Status:** Accepted

**Context:** Weeks 1-6 committed to a CLI presentation layer, consistent across the Sprint Zero plan, the Week 4.2 UML package, and the Week 5.2 traceability matrix. On May 17, 2026 the course instructor directed that AstraNotes must be "a 3-tier application with GUI frontend." This supersedes the CLI direction.

**Decision:** Replace the CLI as the user-facing entry point with a CustomTkinter desktop GUI. Keep the logic tier (NoteManager, ValidationLayer, PrivacyService) and data tier (JsonFileRepository) unchanged. Introduce a presentation split: `gui/controller.py` (NotesController - widget-free, headlessly testable presentation logic) and `gui/app.py` (the CustomTkinter view, a thin shell). The CLI module is retained only as a developer/test harness; `python -m astranotes` now launches the GUI.

**Rationale:** The architecture was already 3-tier with a dependency-injection seam, so the pivot swaps only the presentation tier - the controller talks to the same NoteManager the CLI used, and the existing 34 logic/data tests are unaffected. The controller/view split keeps NFR-02 intact: presentation behavior is unit-tested without a display (6 new headless tests).

**SPR-04 license exception:** CustomTkinter 5.2.2 is distributed under CC0-1.0 (public-domain dedication), which is outside SPR-04's literal MIT/Apache/BSD allowlist. CC0 imposes no copyleft and no attribution obligation - it is strictly more permissive than MIT/BSD - so it is accepted here as a deliberate, logged exception rather than a silent pass, per the Working Agreement rule that deviations are recorded as Architecture Decisions before acceptance.

**Consequences:** The deployment, use-case, and activity diagrams and CLAUDE.md must be updated to show `gui/` as the presentation tier (the prior CLI-based UML submissions are now historical). A Python build with Tcl/Tk is required to run the GUI; `__main__` degrades to a clear install hint when `_tkinter` is absent rather than crashing.

**Traces to:** NFR-02, SPR-04; supersedes the CLI presentation decisions implied by the Sprint Zero plan and the Week 4.2 UML package.

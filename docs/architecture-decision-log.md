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

## ADR-005: Key Management Strategy (RESOLVED 2026-05-30)
**Date opened:** April 13, 2026 (Week 3.1)
**Date resolved:** May 30, 2026 (Week 9.1)
**Status:** Accepted

**Context:** SPR-01 requires Fernet encryption at rest but the key must never be stored in source code or the notes data directory. Through Sprint Zero and the realization slices we used a session-only key (when `ASTRANOTES_KEY` was unset) or an env-var key (when set). Neither was the production strategy; ADR-005 had to be resolved before the project could be presented as ready.

**Options considered:**
- (a) Environment variable only — simplest, but the user has to manage a 32-byte base64 string. Not a real consumer UX.
- (b) OS keychain — most secure on a managed laptop, but platform-dependent (Keychain on macOS, libsecret on Linux, DPAPI on Windows) and brings a new dependency surface.
- (c) Per-note passphrase — most granular, but breaks the FR-04 toggle model and gives the user a passphrase-management problem proportional to the note count. Out of line with how Obsidian / Standard Notes / Bitwarden handle this.
- (d) **Master passphrase + PBKDF2-derived Fernet key (accepted).** The user sets one passphrase the first time a private note is created; the Fernet key is derived from passphrase + 16-byte random salt via PBKDF2-HMAC-SHA256 with 600,000 iterations. The derived key lives only in memory; only the salt and a small Fernet-encrypted verifier blob (`astranotes-passphrase-verifier-v1`) are persisted to `~/.astranotes/passphrase.json`. On launch, if the file exists, the GUI prompts for unlock; the typed passphrase derives the key and is verified against the stored verifier. The env-var path remains as a back-compat seam for tests and CI.

**Decision:** Option (d). Implemented in `astranotes/services/passphrase.py` (`PassphraseStore`) and `astranotes/gui/passphrase_dialog.py`.

**Rationale:** SPR-01 says "key never in source code or data directory." A passphrase-derived key never persists to either, so the spirit of SPR-01 holds. The salt is non-secret (PBKDF2 design) and lives outside the notes directory in its own file. PBKDF2 with 600k iterations is the current OWASP recommendation for SHA-256 and is enough to make a brute-force attempt on a typical 8+ character passphrase impractical on commodity hardware. We deliberately reject (b) keychain because its platform dependency would erase the "local-first, no infra" advantage of the project; (c) per-note because it adds operational pain with no concrete threat-model benefit for a single-user app.

**Consequences:**
- The GUI gains a launch-time unlock dialog and a "set passphrase on first private note" dialog.
- `ASTRANOTES_KEY` env var takes precedence and skips the passphrase flow (preserves 75 tests + CLI dev harness).
- There is no recovery path for a forgotten passphrase — by design. The dialog says so. This is the same trade-off Obsidian and Standard Notes make.
- Threat model: protects against disk theft; does NOT protect against a process that already has the running app's memory (out of scope for a desktop note app).

**Traces to:** SPR-01; resolves the ADL deadline that the refined-requirements set on this decision.

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

# AstraNotes — Refined Requirement Baseline (Week 3.1)

**Student:** Atishay Jain | **Date:** April 13, 2026 | **Technical Path:** Python

This is a direct refinement of the Week 1.2 Requirement Set. Each requirement has been reviewed for ambiguity, weak assumptions, and missing edge cases identified during the Week 2.1 and Week 2.2 planning work.

---

## Functional Requirements

| ID | Refined Requirement | Change from Week 1.2 |
|----|---------------------|----------------------|
| FR-01 | The system shall allow a user to create a new text note with a non-empty title and a body (which may be empty). The note shall be assigned a UUID, created_at timestamp, and modified_at timestamp automatically at creation time. Titles consisting only of whitespace are treated as empty. | Added: title must be non-empty (ValidationLayer). Body may be empty. Timestamps system-assigned. Whitespace-only titles rejected. |
| FR-02 | The system shall allow a user to edit the title or body of an existing note and save the updated version to local storage. On save, the modified_at timestamp shall be updated to the current time. The created_at timestamp and UUID shall not change. | Added: created_at and UUID immutable on edit. modified_at updates on every save. |
| FR-03 | The system shall allow a user to delete a note by its UUID. If the UUID does not exist, the system shall surface a clear error rather than silently succeed or crash. | Added: behavior for deleting a non-existent note. |
| FR-04 | The system shall allow a user to toggle a note's is_private flag. When True, the body is encrypted by PrivacyService before write; decrypted on retrieval. Toggling from True to False re-saves with plaintext body. If decryption fails during toggle, the operation fails with a clear error and the note remains encrypted. | Added: toggle-off behavior. Added: failure handling when decryption fails during toggle. |
| FR-05 | The system shall persist notes to local storage using a one-file-per-note format. On startup, valid note files load normally; corrupt/missing files are skipped with an error logged. If the data directory does not exist on first launch, the system creates it. | Added: corrupt file handling. Added: directory auto-creation. Separated storage format (JSON) as design decision per class guidance. |
| FR-06 | Each note shall carry metadata: UUID (id), created_at (datetime, UTC), modified_at (datetime, UTC), and tags (list of strings, may be empty). Tags are case-sensitive. | Added: UTC for timestamps. Tags case-sensitive, may be empty. |
| FR-07 | The system shall allow keyword search across note titles and bodies. Search is case-insensitive using plain string matching. Private notes that decrypt successfully are included; those that fail are excluded with error logged. Empty collection returns empty result set. | Added: private note behavior in search. Plain string matching. Empty collection handling. |
| FR-08 | Notes displayed sorted by modified_at descending by default. Identical modified_at values use created_at descending as stable tiebreaker. | Added: stable tiebreaker for ties. |

## Non-Functional Requirements

| ID | Refined Requirement | Change from Week 1.2 |
|----|---------------------|----------------------|
| NFR-01 | List and search within 2 seconds for up to 500 notes on minimum hardware (8 GB RAM, SSD, modern dual-core CPU). | Added: hardware baseline definition. |
| NFR-02 | Architecture enforces separation between NoteManager, NoteRepository/JsonFileRepository, and PrivacyService such that each can be unit-tested independently. | Added: testability as explicit constraint. Named layers. |
| NFR-03 | App loads and displays note list within 3 seconds of launch on NFR-01 hardware baseline, measured from process start to first interactive display. | Added: measurement definition. Referenced NFR-01 baseline. |

## Security, Privacy, Reliability, and Governance Requirements

| ID | Refined Requirement | Change from Week 1.2 |
|----|---------------------|----------------------|
| SPR-01 | Private note bodies encrypted with Fernet before any disk write. Key never stored in source code or notes directory. Key management documented in ADL before Sprint 1. | Added: key storage constraint and ADL deadline. |
| SPR-02 | All storage exceptions caught and translated to app-level messages. No file paths, stack traces, or internal state exposed. | Added: specific exception types and constraint against exposing internals. |
| SPR-03 | Core components have at least one automated unit test before each milestone. Tests run without external dependencies (use temp dirs, test keys). | Added: no external dependency requirement for tests. |
| SPR-04 | Third-party libraries recorded with pinned version, purpose comment, and confirmed permissive license (MIT, Apache 2.0, BSD). No unconfirmed licenses. | Added: pinned versions and license confirmation. |

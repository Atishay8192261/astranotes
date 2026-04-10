# AstraNotes — Prioritized Backlog

**Student:** Atishay Jain | **Date:** April 10, 2026 | **Technical Path:** Python

---

Stories are ordered by a dependency and risk criterion: stories that establish foundational infrastructure or de-risk the architecture are placed first. Stories that depend on a stable core follow.

| Priority | Story | Requirement(s) | Rationale |
|----------|-------|-----------------|-----------|
| 1 | US-08 — Project Setup and Structural Readiness | NFR-02, NFR-03, SPR-04 | Foundation: all other stories depend on the layered folder structure, repository interface, and DI support. |
| 2 | US-01 — Create a New Note | FR-01, FR-07 | Primary user action. Validates Note model, Validation Layer, and JSON File Adapter end-to-end. |
| 3 | US-04 — Mark a Note as Private | FR-04, SPR-01 | Highest architectural risk. PrivacyService must be verified before the save/load path is considered stable. |
| 4 | US-05 — Persist and Restore Notes | FR-05, FR-06, NFR-03 | Validates the full read/write round-trip including startup loading and 500-note performance target. |
| 5 | US-02 — Edit an Existing Note | FR-02 | Depends on create and persist. Validates the update path through NoteRepository. |
| 6 | US-03 — Delete a Note | FR-03 | Completes CRUD. Depends on create and persist being solid. |
| 7 | US-06 — Search Notes by Keyword | FR-08, NFR-01 | Depends on a populated note store and privacy decryption. Performance needs real data to validate. |
| 8 | US-07 — Handle Storage Errors Gracefully | SPR-02, SPR-03 | Cross-cutting concern; easier to finalize once all storage paths are implemented. |

### Prioritization Notes

**Why US-08 first:** The project structure and repository interface are prerequisites for every other story. Without the layered directory and the NoteRepository ABC, there is no contract for the JSON File Adapter, Privacy Service, or Validation Layer to implement against.

**Why US-04 third:** The Privacy Service is the highest architectural risk in AstraNotes. If encryption is not integrated into the save/load path early, every CRUD story built on top of the repository risks introducing plaintext storage bugs that violate SPR-01.

**Why US-07 last:** Error handling is a cross-cutting concern that touches every storage path. It is easier to finalize and test once the full CRUD loop and search are implemented.

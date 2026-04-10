# AstraNotes — User Stories and Acceptance Criteria

**Student:** Atishay Jain | **Date:** April 10, 2026 | **Technical Path:** Python

---

## US-01 — Create a New Note
**Requirement:** FR-01, FR-07

As a user, I want to create a new note by providing a title and body so that I can capture my thoughts and have them saved with a unique ID, timestamps, and an empty tag list.

**Acceptance Criteria:**
- When I submit a valid title and body, a Note is created with a UUID, created_at, and modified_at set automatically.
- The new note is persisted to the local JSON file store immediately after creation.
- Submitting an empty title or empty body is rejected with a non-technical validation error message (ValidationError per SPR-02).
- The created note can be retrieved by its ID in the same session and after restarting the application.

---

## US-02 — Edit an Existing Note
**Requirement:** FR-02

As a user, I want to edit an existing note's title or body so that I can keep my notes accurate and up to date, with the last-modified timestamp updating automatically.

**Acceptance Criteria:**
- When I modify and save a note, only the changed fields and the modified_at timestamp are updated; the original created_at and ID remain unchanged.
- The updated note is persisted to storage before the operation returns.
- If the target note does not exist, the system raises NoteNotFoundError and shows a user-friendly message.
- If the save operation fails, a clear error is shown and the existing note is not corrupted.

---

## US-03 — Delete a Note
**Requirement:** FR-03

As a user, I want to delete a note by its unique identifier so that I can remove notes I no longer need and keep my collection organized.

**Acceptance Criteria:**
- When I trigger delete and confirm, the note's JSON file is removed from the storage directory.
- After deletion, the note no longer appears in list or search results.
- Attempting to delete a non-existent note raises NoteNotFoundError with a clear, non-technical message per SPR-02.

---

## US-04 — Mark a Note as Private
**Requirement:** FR-04, SPR-01

As a user, I want to flag a note as private so that its body is encrypted at rest and my sensitive content is protected even if someone accesses the storage files directly.

**Acceptance Criteria:**
- When is_private is set to True and the note is saved, the body is encrypted by PrivacyService using Fernet before being written to disk.
- The raw note file on disk contains no plaintext body content for any private note.
- When a private note is retrieved, the body is decrypted by PrivacyService transparently so the user sees readable content.
- If encryption or decryption fails, a clear error is shown and no partial or garbled content is displayed.
- Toggling a note from private back to non-private stores the body in plaintext and removes the encrypted version.

---

## US-05 — Persist and Restore Notes Across Sessions
**Requirement:** FR-05, FR-06, NFR-03

As a user, I want my notes to be saved to local files and automatically restored when I reopen the application so that I never lose data between sessions.

**Acceptance Criteria:**
- On startup, all previously saved notes are loaded from local file storage and displayed.
- Each note is stored as an individual {id}.json file in the designated storage directory.
- Notes created or edited in the current session are available in the next session without additional action.
- If a note file is missing or corrupt on startup, the app logs a PersistenceError and continues loading the remaining notes.
- Startup and list operations for a collection of 500 notes complete within 2 seconds per NFR-01.

---

## US-06 — Search Notes by Keyword
**Requirement:** FR-08, NFR-01

As a user, I want to search my notes by keyword so that I can find relevant notes without scrolling through my entire collection.

**Acceptance Criteria:**
- Entering a keyword returns all notes whose title or body contains it (case-insensitive).
- Results are returned as a list of matching note summaries (ID, title, snippet).
- If no notes match, a clear empty-state message is shown.
- Search across up to 500 notes completes within 2 seconds per NFR-01.
- Private note bodies are decrypted before searching so that keyword matches are not missed.

---

## US-07 — Handle Storage Errors Gracefully
**Requirement:** SPR-02, SPR-03

As a user, I want clear and non-technical error messages when something goes wrong with saving or loading my notes so that I understand what happened without seeing raw stack traces.

**Acceptance Criteria:**
- File-not-found, permission-denied, and corrupt-data scenarios each produce a distinct, user-friendly message.
- Domain exceptions (NoteNotFoundError, PersistenceError, ValidationError) are used consistently throughout the codebase.
- No raw Python tracebacks or file paths are displayed to the user.
- Every error path has either an automated test or a documented manual verification procedure per SPR-03.

---

## US-08 — Project Setup and Structural Readiness
**Requirement:** NFR-02, NFR-03, SPR-04

As a developer, I want the project to be organized into distinct layers (models, services, repositories, app logic) with dependency injection support so that I can build, test, and extend each component independently.

**Acceptance Criteria:**
- The project directory follows the layered structure: models/, services/, repositories/, app/, tests/ per NFR-02.
- The NoteRepository abstract base class is defined with save(), get(), list_all(), update(), and delete() method signatures.
- A requirements.txt or pyproject.toml file documents all third-party dependencies with their purpose and license per SPR-04.
- A simple test can instantiate any service with a mock repository, confirming dependency injection works per NFR-03.
- The project runs with `python -m astranotes` without errors (placeholder CLI acceptable).

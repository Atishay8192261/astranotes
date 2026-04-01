# AstraNotes — Requirements

**Student:** Atishay Jain | **Date:** April 10, 2026 | **Technical Path:** Python

---

## Functional Requirements

| ID   | Requirement |
|------|-------------|
| FR-01 | The system shall enable a user to create a new note by providing a title and body in plain text. |
| FR-02 | The system shall enable a user to modify an existing note's title or body and persist the changes with an automatically updated last-modified timestamp. |
| FR-03 | The system shall enable a user to remove a note from the collection using its unique identifier. |
| FR-04 | The system shall enable a user to flag a note as private, causing its body to be encrypted before it is written to storage. |
| FR-05 | The system shall save all notes to a local file-based store so that data is retained between application sessions. |
| FR-06 | The system shall restore all previously saved notes from local storage on startup. |
| FR-07 | Each note shall carry metadata including a unique identifier (UUID), creation timestamp, last-modified timestamp, and a list of user-assigned tags. |
| FR-08 | The system shall provide keyword-based search across note titles and bodies, returning a list of all matching notes. |

## Non-Functional Requirements

| ID    | Requirement |
|-------|-------------|
| NFR-01 | The system shall handle a local collection of up to 500 notes without degradation, completing list and search operations in under 2 seconds. |
| NFR-02 | The codebase shall enforce separation of concerns by organizing source files into distinct layers for models, services, repositories, and application logic. |
| NFR-03 | The architecture shall allow individual components (e.g., storage adapter, privacy service) to be tested in isolation through dependency injection or interface substitution. |

## Security, Privacy, Reliability, and Governance Requirements

| ID    | Requirement |
|-------|-------------|
| SPR-01 | Notes marked as private shall be encrypted at rest using symmetric encryption (e.g., Fernet from Python's cryptography package) so that raw content is never stored in plaintext. |
| SPR-02 | The system shall catch and handle all storage-related failures (file not found, permission denied, corrupt data) and surface clear, non-technical error messages to the user. |
| SPR-03 | All major components shall be covered by automated tests or a documented manual verification procedure to support quality assurance before each milestone delivery. |
| SPR-04 | Any third-party library introduced into the project shall be documented with its purpose and license; unverified or unnecessary dependencies shall be avoided. |

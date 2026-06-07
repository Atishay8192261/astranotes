# Class Diagram — AstraNotes

Rendered with [Mermaid](https://mermaid.js.org/) (GitHub renders automatically).

```mermaid
classDiagram
    %% ── Domain model ─────────────────────────────────────────────────────
    class Note {
        +UUID id
        +str title
        +str body
        +bool is_private
        +datetime created_at
        +datetime modified_at
        +list~str~ tags
    }

    %% ── Repository interface (ABC) ───────────────────────────────────────
    class NoteRepository {
        <<interface>>
        +save(note: Note) None
        +get(note_id: UUID) Note
        +list_all() list~Note~
        +update(note: Note) None
        +delete(note_id: UUID) None
    }

    class JsonFileRepository {
        -Path _data_dir
        +save(note: Note) None
        +get(note_id: UUID) Note
        +list_all() list~Note~
        +update(note: Note) None
        +delete(note_id: UUID) None
    }

    NoteRepository <|.. JsonFileRepository : implements

    %% ── Service tier ─────────────────────────────────────────────────────
    class PrivacyService {
        -bytes _key
        +generate_key()$ bytes
        +encrypt(plaintext: str) str
        +decrypt(ciphertext: str) str
    }

    class ValidationLayer {
        +validate(note: Note) None
    }

    class NoteManager {
        -NoteRepository _repository
        -ValidationLayer _validation
        -PrivacyService _privacy
        +create_note(title, body, is_private, tags) Note
        +list_notes() list~Note~
        +list_all_for_display() list~Note~
        +get_note(note_id) Note
        +update_note(note_id, title, body, tags) Note
        +delete_note(note_id) None
        +set_private(note_id, is_private) Note
        +duplicate_note(note_id) Note
        +search_notes(keyword) list~Note~
        +get_stats() dict
    }

    class EventLogger {
        +Path log_path
        +log(action: str, detail: str) None
    }

    NoteManager --> NoteRepository : uses
    NoteManager --> PrivacyService : uses
    NoteManager --> ValidationLayer : uses
    NoteManager --> Note : produces/consumes

    %% ── Presentation tier ────────────────────────────────────────────────
    class ActionResult {
        +bool ok
        +str message
    }

    class NotesController {
        -NoteManager _manager
        +has_privacy_key bool
        +set_privacy_service(privacy) None
        +list_notes() list~Note~
        +list_all_for_display() list~Note~
        +create_note(title, body, is_private, tags_csv) ActionResult
        +update_note(note_id, title, body, tags_csv) ActionResult
        +delete_note(note_id) ActionResult
        +duplicate_note(note_id) ActionResult
        +get_note(note_id) Note
        +set_private(note_id, is_private) ActionResult
        +search_notes(keyword) list~Note~
        +get_stats() dict
    }

    class AstraNotesApp {
        -NotesController _controller
        -EventLogger _event_log
        -Note _selected
        +refresh_notes_list() None
        +_new_note() None
        +_save_note() None
        +_delete_note() None
        +_duplicate_note() None
        +_open_admin() None
    }

    NotesController --> NoteManager : delegates to
    NotesController --> ActionResult : returns
    AstraNotesApp --> NotesController : delegates all actions
    AstraNotesApp --> EventLogger : logs UI events

    %% ── Passphrase store ─────────────────────────────────────────────────
    class PassphraseStore {
        -Path _path
        +exists() bool
        +initialize(passphrase) PrivacyService
        +unlock(passphrase) PrivacyService
    }

    AstraNotesApp --> PassphraseStore : unlock on launch
    PassphraseStore --> PrivacyService : produces
```

## Tier Boundaries

| Tier | Package | Key Classes |
|------|---------|-------------|
| Presentation | `astranotes.gui` | `AstraNotesApp`, `NotesController`, `EventLogger` |
| Logic | `astranotes.services` | `NoteManager`, `PrivacyService`, `ValidationLayer` |
| Data | `astranotes.repositories`, `astranotes.models` | `JsonFileRepository`, `Note` |

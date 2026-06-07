# Object Diagram — AstraNotes (demo session snapshot)

Shows concrete runtime instances during a demo session with two notes loaded.

```mermaid
classDiagram
    direction LR

    class app_instance {
        <<AstraNotesApp object>>
        _key_source = "passphrase (PBKDF2)"
        _selected = note_shopping
    }

    class controller_instance {
        <<NotesController object>>
        has_privacy_key = true
    }

    class manager_instance {
        <<NoteManager object>>
        _privacy = privacy_instance
    }

    class privacy_instance {
        <<PrivacyService object>>
        _key = b"[32-byte Fernet key in memory]"
    }

    class repo_instance {
        <<JsonFileRepository object>>
        _data_dir = "~/.astranotes/notes"
    }

    class note_shopping {
        <<Note object>>
        id = "a1b2c3d4-..."
        title = "Shopping List"
        body = "Milk, Eggs, Bread"
        is_private = false
        created_at = 2026-06-07T10:00:00Z
        modified_at = 2026-06-07T10:05:00Z
        tags = ["home", "weekly"]
    }

    class note_diary {
        <<Note object>>
        id = "e5f6a7b8-..."
        title = "Private Diary"
        body = "[decrypted in memory]"
        is_private = true
        created_at = 2026-06-06T22:00:00Z
        modified_at = 2026-06-06T22:30:00Z
        tags = ["personal"]
    }

    class event_log_instance {
        <<EventLogger object>>
        log_path = "~/.astranotes/events.log"
    }

    app_instance --> controller_instance : _controller
    app_instance --> event_log_instance : _event_log
    app_instance --> note_shopping : _selected
    controller_instance --> manager_instance : _manager
    manager_instance --> privacy_instance : _privacy
    manager_instance --> repo_instance : _repository
    manager_instance --> note_shopping : manages
    manager_instance --> note_diary : manages
```

> **Note:** `note_diary.body` is stored as Fernet ciphertext on disk.  
> It only appears as plaintext in this in-memory object after decryption.

# Activity Diagram — AstraNotes

## Activity 1: Save Note (FR-01 / FR-02 / FR-04 / SPR-01)

This is the primary workflow. Every node has exactly one entry path;
the diagram starts at ● and ends at ◉.

```mermaid
flowchart TD
    Start(["● Start"])
    ReadFields["Read title, body, tags, private-switch from view"]
    CheckPrivate{Private switch ON?}
    CheckKey{Privacy key in memory?}
    PromptPassphrase["Prompt: Enter passphrase"]
    PassOK{Passphrase valid?}
    StatusFail["Status bar: 'Passphrase required'\nButtons stay enabled"]
    CheckNewOrEdit{Existing note selected?}
    CallCreate["Controller.create_note(\n  title, body, is_private, tags\n)"]
    CallUpdate["Controller.update_note(\n  id, title, body, tags\n)"]
    CheckPrivacyChanged{Privacy flag changed?}
    CallSetPrivate["Controller.set_private(id, new_flag)"]
    Validate["ValidationLayer.validate(note)\nRaises ValidationError if title blank"]
    EncryptBody{is_private?}
    Encrypt["PrivacyService.encrypt(body)\n→ Fernet ciphertext"]
    SaveToDisk["JsonFileRepository.save / update\nWrites JSON to data_dir/‹uuid›.json"]
    LogEvent["EventLogger.log(note_created | note_updated)"]
    ClearEditor["Clear editor fields\n_selected = None"]
    RefreshList["refresh_notes_list()\nReloads sidebar from disk"]
    StatusOK["Status bar: 'Saved note …' / 'Note updated'"]
    End(["◉ End"])

    Start --> ReadFields
    ReadFields --> CheckPrivate
    CheckPrivate -- No --> CheckNewOrEdit
    CheckPrivate -- Yes --> CheckKey
    CheckKey -- Yes --> CheckNewOrEdit
    CheckKey -- No --> PromptPassphrase
    PromptPassphrase --> PassOK
    PassOK -- Yes --> CheckNewOrEdit
    PassOK -- No --> StatusFail --> End

    CheckNewOrEdit -- No (new) --> CallCreate
    CheckNewOrEdit -- Yes (edit) --> CallUpdate

    CallCreate --> Validate
    CallUpdate --> Validate
    CallUpdate --> CheckPrivacyChanged
    CheckPrivacyChanged -- Yes --> CallSetPrivate --> Validate
    CheckPrivacyChanged -- No --> Validate

    Validate --> EncryptBody
    EncryptBody -- Yes --> Encrypt --> SaveToDisk
    EncryptBody -- No --> SaveToDisk
    SaveToDisk --> LogEvent
    LogEvent --> ClearEditor
    ClearEditor --> RefreshList
    RefreshList --> StatusOK
    StatusOK --> End

    style Start fill:#1a1c20,color:#fff,stroke:#fff
    style End fill:#1a1c20,color:#fff,stroke:#fff
    style StatusFail fill:#b91c1c,color:#fff
    style Encrypt fill:#1d4ed8,color:#fff
```

---

## Activity 2: Search Notes (FR-07)

```mermaid
flowchart TD
    S2(["● Start"])
    KeyRelease["User types in search box\n(KeyRelease event)"]
    GetKeyword["Read keyword from entry widget"]
    IsBlank{Keyword blank?}
    CallListAll["controller.list_all_for_display()\n→ all notes (locked shown as 🔒)"]
    CallSearch["controller.search_notes(keyword)"]
    IterNotes["For each note in results"]
    IsPrivate{note.is_private?}
    HasKey{privacy key set?}
    Decrypt["PrivacyService.decrypt(body)"]
    DecryptFail{Decrypt failed?}
    SkipNote["Skip note\nlog error"]
    MatchKeyword{keyword in title.lower()\nor body.lower()?}
    Collect["Append to match list"]
    RenderSidebar["Render sidebar items\n(🔒 for locked notes)"]
    E2(["◉ End"])

    S2 --> KeyRelease --> GetKeyword --> IsBlank
    IsBlank -- Yes (show all) --> CallListAll --> RenderSidebar
    IsBlank -- No --> CallSearch --> IterNotes
    IterNotes --> IsPrivate
    IsPrivate -- Yes --> HasKey
    HasKey -- No --> SkipNote
    HasKey -- Yes --> Decrypt --> DecryptFail
    DecryptFail -- Yes --> SkipNote
    DecryptFail -- No --> MatchKeyword
    IsPrivate -- No --> MatchKeyword
    MatchKeyword -- Yes --> Collect --> IterNotes
    MatchKeyword -- No --> IterNotes
    SkipNote --> IterNotes
    IterNotes -- done --> RenderSidebar --> E2

    style S2 fill:#1a1c20,color:#fff,stroke:#fff
    style E2 fill:#1a1c20,color:#fff,stroke:#fff
    style SkipNote fill:#b91c1c,color:#fff
    style Decrypt fill:#1d4ed8,color:#fff
```

---

## Activity 3: Unlock Passphrase on Locked Note Click (SPR-04)

```mermaid
flowchart TD
    S3(["● Start"])
    ClickLocked["User clicks 🔒 note in sidebar"]
    ShowLockMsg["Display: '🔒 This note is encrypted'\nDisable Delete + Duplicate"]
    PromptUnlock["Show passphrase dialog\n(up to 3 attempts)"]
    AttemptOK{Passphrase correct?}
    AttemptsLeft{Attempts < 3?}
    SetKey["controller.set_privacy_service(key)"]
    RefreshList["refresh_notes_list() — locked notes now readable"]
    OpenNote["Load decrypted note into editor\nEnable Delete + Duplicate"]
    TooMany["Status: 'Passphrase failed'\nNote stays locked"]
    Cancelled["Status: 'Locked note'"]
    E3(["◉ End"])

    S3 --> ClickLocked --> ShowLockMsg --> PromptUnlock
    PromptUnlock --> AttemptOK
    AttemptOK -- Yes --> SetKey --> RefreshList --> OpenNote --> E3
    AttemptOK -- No --> AttemptsLeft
    AttemptsLeft -- Yes --> PromptUnlock
    AttemptsLeft -- No --> TooMany --> E3
    PromptUnlock -- Cancelled --> Cancelled --> E3

    style S3 fill:#1a1c20,color:#fff,stroke:#fff
    style E3 fill:#1a1c20,color:#fff,stroke:#fff
    style TooMany fill:#b91c1c,color:#fff
    style SetKey fill:#1d4ed8,color:#fff
```

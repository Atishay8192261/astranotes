# Deployment Diagram — AstraNotes

```mermaid
graph TB
    subgraph MacOS_Node["macOS Node (developer / end-user machine)"]
        subgraph Python_Runtime["Python 3.11 Runtime"]
            subgraph Presentation["Presentation Tier (gui/)"]
                AppPy["AstraNotesApp\n(customtkinter)"]
                Controller["NotesController"]
                EventLog["EventLogger"]
            end
            subgraph Logic["Logic Tier (services/)"]
                NoteManager["NoteManager"]
                PrivacySvc["PrivacyService\n(Fernet + PBKDF2)"]
                Validation["ValidationLayer"]
            end
            subgraph Data["Data Tier (repositories/)"]
                Repo["JsonFileRepository"]
            end
        end

        subgraph FileSystem["Local Filesystem"]
            DataDir["~/.astranotes/notes/\n*.json (one per note)"]
            PassFile["~/.astranotes/passphrase.json\n(salt + verifier — no key)"]
            EventFile["~/.astranotes/events.log\n(JSON-lines action log)"]
        end

        subgraph DemoData["Demo Data (optional)"]
            DemoDir["./demo-data/\n*.json (12 sample notes)"]
        end
    end

    AppPy -->|"delegates all actions"| Controller
    AppPy -->|"logs UI events"| EventLog
    Controller -->|"calls"| NoteManager
    NoteManager -->|"encrypt/decrypt"| PrivacySvc
    NoteManager -->|"validate"| Validation
    NoteManager -->|"CRUD"| Repo
    Repo -->|"read/write JSON"| DataDir
    PrivacySvc -->|"read salt + verifier"| PassFile
    EventLog -->|"append JSON lines"| EventFile

    classDef tier fill:#1d4ed8,color:#fff,stroke:#1e40af
    classDef file fill:#374151,color:#fff,stroke:#6b7280
    classDef demo fill:#92400e,color:#fff,stroke:#b45309
    class AppPy,Controller,EventLog tier
    class NoteManager,PrivacySvc,Validation tier
    class Repo tier
    class DataDir,PassFile,EventFile file
    class DemoDir demo
```

## Deployment Notes

| Artefact | Location | Notes |
|----------|----------|-------|
| Application source | `~/Documents/astranotes-project/` | Git-tracked |
| Installed package | `venv/` (editable install via `pip install -e .`) | Not committed |
| Note store | `~/.astranotes/notes/*.json` | Not committed |
| Passphrase verifier | `~/.astranotes/passphrase.json` | Not committed |
| Event log | `~/.astranotes/events.log` | Not committed |
| Demo data | `./demo-data/` | Committed (encrypted payloads only; passphrase is a CLI arg) |
| Mac app bundle | `~/Desktop/AstraNotes.app` | Shell-script launcher; not committed |

## CI/CD Deployment (GitHub Actions)

```
push → .github/workflows/ci.yml
         ├── test job    (pytest, Python 3.11 + 3.12)
         ├── security    (bandit SAST scan)
         └── lint        (ruff)
```

No production server or network deployment — AstraNotes is local-first by design.

# AstraNotes - UML Design Package Rationale

**Student:** Atishay Jain  |  **Course:** CSEN 296B-2  |  **Date:** April 27, 2026  |  **Project:** AstraNotes

This document explains how the five UML views in `docs/uml/` describe one coherent system. The package is built around the layered architecture from CLAUDE.md: `Note` (entity), `NoteRepository` (abstract storage interface) and `JsonFileRepository` (concrete adapter), `PrivacyService` (Fernet encryption), `ValidationLayer` (input rules), `NoteManager` (orchestrator), and the `AstraNotesError` family (`NoteNotFoundError`, `PersistenceError`, `ValidationError`).

## How the five views fit together

- **Class diagram** (`class-diagram.mmd`) is the structural anchor. It names every class, attribute, method signature, and relationship used in the rest of the package. `NoteRepository` is shown as `<<abstract>>` and `JsonFileRepository` as its only realization, matching the dependency-injection rule from NFR-02 and the storage choice in FR-05. The exception hierarchy (`AstraNotesError` parent with three subclasses) appears here so that the activity diagram and the rationale can refer to them by exact name. `NoteManager` is included even though it is planned for Sprint 1; including it now keeps the orchestration story consistent across all later views.

- **Object diagram** (`object-diagram.mmd`) is a concrete snapshot at a single instant (`2026-04-27T13:42:00Z`). It instantiates exactly the classes from the class diagram - one `NoteManager`, one `JsonFileRepository`, one `PrivacyService`, one `ValidationLayer`, plus three `Note` instances (a public grocery list, a private journal whose body is shown as Fernet ciphertext, and a tagged class note). The disk subgraph shows the three `{uuid}.json` files those instances persist to, which makes FR-05 and FR-06 visible in concrete form. The private note's body field shows ciphertext to enforce SPR-01: private bodies never appear in plaintext on disk.

- **Use case diagram** (`use-case-diagram.mmd`) shows the eight user-visible behaviors, each tagged with the requirement IDs that justify it (FR-01 through FR-08, plus SPR-01, SPR-02, SPR-03, NFR-03). There is exactly one actor - the Solo User - because the project is explicitly single-user (CLAUDE.md "Realistic scope" rule). Two cross-cutting behaviors ("Persist and restore on startup" and "Surface storage errors safely") are linked by `<<include>>` arrows from every write-side use case, which is the use-case-level expression of the SPR-02 error-translation rule.

- **Activity diagram** (`activity-diagram.mmd`) drills into one use case - "Create a private note" - because it is the workflow that exercises every layer in one pass. The activity nodes call out the exact methods from the class diagram (`NoteManager.create_note`, `ValidationLayer.validate`, `PrivacyService.encrypt`, `NoteRepository.save`). Two decision diamonds reflect real branches the code already implements: the validation gate (FR-01), and the OSError-to-PersistenceError translation (SPR-02). The "is_private?" branch shows where SPR-01 takes effect: the body becomes Fernet ciphertext bytes before `JsonFileRepository.save` writes anything to disk.

- **Deployment diagram** (`deployment-diagram.mmd`) shows the runtime topology: one user workstation, one OS process (`python -m astranotes`), the `astranotes/` package decomposed into the same `cli/`, `services/`, `repositories/`, `models/` folders that exist in the repo, the third-party `cryptography` library (with a license/version comment per SPR-04), and the local filesystem holding the `data/` directory and the Fernet key store. The key store node carries an explicit "ADR pending in Sprint 1" annotation to keep the SPR-01 risk visible until the Architecture Decision Log is updated.

## Consistency claims (cross-checked)

- Every class on the class diagram appears either as an instance on the object diagram or as a deployable component on the deployment diagram.
- Every method called in the activity diagram (`create_note`, `validate`, `encrypt`, `save`) is declared on the class diagram with matching signature.
- The exception names used in the activity diagram (`ValidationError`, `PersistenceError`) are declared in the class diagram's exception hierarchy.
- The use case "Toggle note privacy (FR-04, SPR-01)" maps to `NoteManager.toggle_privacy` on the class diagram; the use case "Search notes by keyword (FR-07)" maps to `NoteManager.search_notes`.
- The directory subgraphs in the deployment diagram (`models/`, `services/`, `repositories/`, `gui/`) match the actual project layout in CLAUDE.md and the `astranotes/` folder on disk. (Originally `cli/`; see the Week 7.2 addendum below.)
- The single-actor scope on the use case diagram matches the single-process, single-workstation topology on the deployment diagram.

## Requirements coverage map

| Requirement | View(s) where it is visible |
|---|---|
| FR-01 (create / non-empty title) | Class (`ValidationLayer.validate`), Use case UC1, Activity (validation gate) |
| FR-02 (edit) | Class (`NoteManager.edit_note`), Use case UC2 |
| FR-03 (delete) | Class (`NoteRepository.delete`, `NoteManager.delete_note`), Use case UC3 |
| FR-04 (toggle privacy) | Class (`NoteManager.toggle_privacy`), Use case UC4, Activity (is_private branch) |
| FR-05, FR-06 (one file per note, metadata) | Object (Disk subgraph), Deployment (`data/` node), Class (`JsonFileRepository`) |
| FR-07 (keyword search) | Class (`NoteManager.search_notes`), Use case UC6 |
| FR-08 (sort by modified_at) | Class (`NoteManager.list_notes`), Use case UC5 |
| NFR-02 (separation of concerns) | Class (ABC + concrete), Deployment (each layer in its own folder) |
| NFR-03 (startup under 3s) | Use case UC7, Deployment (single local process, no network) |
| SPR-01 (encrypt private bodies) | Class (`PrivacyService`), Activity (Encrypt step), Object (note2 ciphertext), Deployment (Fernet key store) |
| SPR-02 (translate storage errors) | Class (exception hierarchy), Use case UC8, Activity (Surface message steps) |
| SPR-03 (testable units) | Class (each component has a single, mockable interface) |
| SPR-04 (licensed third-party deps) | Deployment (cryptography 44.0.0, pytest 8.3.4 with license note) |

NFR-01 (500-note benchmark) is not visible in any single diagram - it is a runtime-performance assertion better demonstrated by a benchmark harness in Sprint 1 than by a UML view, and is noted here so reviewers know it is intentionally out of scope.

## Design tradeoffs worth flagging

- The use case diagram is rendered with Mermaid `flowchart` because Mermaid does not yet have a native UML use-case shape. Stadium-shaped nodes inside a labeled subgraph are the closest faithful approximation, and the `<<include>>` semantics are preserved with dotted "include" edges.
- `NoteManager` is in every diagram even though no production code for it exists yet. This is deliberate: the package's value is showing the target architecture, and adding it later would force reissuing all five diagrams. The class diagram's method list defines the contract Sprint 1 must implement.
- The Fernet key store appears as a separate node on the deployment diagram with an "ADR pending" label rather than being elided. The unresolved key-management strategy is the single largest known risk from Sprint Zero, and burying it would be misleading.

## Week 7.2 addendum - 3-tier GUI pivot (May 17, 2026)

The instructor directed that AstraNotes be a 3-tier application with a GUI frontend (ADR-006). The original package above described a CLI presentation layer; this addendum records what changed so the earlier text stays honest rather than being silently rewritten.

- **Deployment diagram** now shows three explicit tiers: presentation (`gui/` - `AstraNotesApp` view plus the widget-free `NotesController`), logic (`services/`), and data (`repositories/` + the filesystem). `customtkinter 5.2.2` is added to the dependency subgraph with its CC0-1.0 license per SPR-04/ADR-006. The retained `cli.app` is drawn as a dev/test harness only.
- **Use case diagram** boundary is relabeled "AstraNotes - local GUI app (3-tier)". The eight use cases and the actor are unchanged - the user-visible behaviors did not change, only the frontend that exposes them.
- **Activity diagram** "Create a private note" now begins at the GUI view and routes through `NotesController`; the SPR-02 message steps are now GUI status-bar updates instead of CLI prints. The method calls into the logic/data tiers (`create_note`, `validate`, `encrypt`, `save`) are unchanged, which is the whole point of the dependency-injection seam: the pivot did not touch the logic or data tiers, and all 34 pre-pivot logic/data tests still pass with 6 new headless controller tests added.
- **Class and object diagrams** are unaffected: no logic-tier or data-tier class changed. The presentation split (`NotesController` / `AstraNotesApp`) lives entirely above `NoteManager` and consumes the same public surface the CLI did.

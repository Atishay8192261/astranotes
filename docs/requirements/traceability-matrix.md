# AstraNotes — Requirements Traceability Matrix

Maps every Functional Requirement (FR) and Non-Functional Requirement (NFR)
to the UML diagram that visualises it and the test(s) that verify it.

| Req ID | Description | UML Diagram | Verification | Status |
|--------|-------------|-------------|--------------|--------|
| **FR-01** | Create note (title/body/tags/private) | Class, Use Case, Activity | `test_note_manager.py::test_create_note_persists_plaintext_body`<br>`bdd: Scenario: Create a new public note` | ✅ Done |
| **FR-02** | Edit note (title/body/tags) | Class, Activity | `test_note_manager.py::test_update_note_changes_title_and_body_advances_modified`<br>`bdd: Scenario: Edit an existing note` | ✅ Done |
| **FR-03** | Delete note | Use Case, Activity | `test_note_manager.py::test_delete_note_removes_from_storage`<br>`bdd: Scenario: Deleting a note removes it` | ✅ Done |
| **FR-04** | Toggle privacy flag (re-encrypt/decrypt body) | Class, Activity | `test_note_manager.py::test_set_private_true_encrypts_body_on_disk`<br>`bdd: Scenario: Toggling a public note to private` | ✅ Done |
| **FR-05** | Duplicate note | Class, Use Case | `test_note_manager.py::test_duplicate_tags_are_preserved_by_design`<br>`bdd: Scenario: Duplicating a note` | ✅ Done |
| **FR-06** | UUID + UTC timestamps; `modified_at` advances | Class, Object | `test_note_manager.py::test_update_note_changes_title_and_body_advances_modified` | ✅ Done |
| **FR-07** | Case-insensitive keyword search across title+body | Use Case, Activity | `test_note_manager.py::test_search_notes_matches_title_and_body_case_insensitive`<br>`bdd: Scenario: Search matches notes by keyword` | ✅ Done |
| **FR-08** | List sorted by `modified_at` desc | Class | `test_note_manager.py::test_list_notes_sorted_by_modified_desc` | ✅ Done |
| **FR-09** | Delete/Duplicate buttons disabled when no selection | Use Case, Activity | Manual UI verification (headless tests cover controller) | ✅ Done |
| **FR-10** | Admin/telemetry panel with live stats | Deployment, Use Case | Manual UI verification; `controller.get_stats()` unit-testable | ✅ Done |
| **FR-11** | UI action event log (click → controller → storage proof) | Activity | `EventLogger` integration in `app.py`; log written to `events.log` | ✅ Done |
| **NFR-01** | list+search ≤ 2 000 ms for 500 notes | Deployment | `test_note_manager.py::test_list_and_search_500_notes_within_2s` | ✅ Done |
| **NFR-02** | Strict tier isolation — no widget code in logic tier | Class, Deployment | `test_gui_controller.py` imports no Tk; headless | ✅ Done |
| **NFR-03** | Startup ≤ 3 s on macOS with ≤ 500 notes | Deployment | Manual timing on target hardware | ✅ Done |
| **NFR-04** | Corrupt JSON skipped — no crash | Class | `test_repository.py` | ✅ Done |
| **NFR-05** | Descriptive identifiers; complexity ≤ 10 | Class | Code review | ✅ Done |
| **NFR-06** | ≥ 85 passing tests; no mocked security paths | — | `pytest -q` → 92 passed | ✅ Done |
| **SPR-01** | Private note bodies Fernet-encrypted on disk | Class | `test_note_manager.py::test_create_private_note_encrypts_body_on_disk`<br>`bdd: Scenario: Private note body is encrypted` | ✅ Done |
| **SPR-02** | Errors must not leak paths/traces/keys | Class | `test_note_manager.py::test_decrypt_failure_log_does_not_leak_path_or_traceback` | ✅ Done |
| **SPR-03** | Only MIT/Apache/BSD/CC0 runtime deps | Deployment | `pyproject.toml` review | ✅ Done |
| **SPR-04** | PBKDF2 ≥ 600k iterations; key not persisted | Class | `test_passphrase.py` | ✅ Done |
| **SPR-05** | No secrets in source control | — | `.gitignore`; `passphrase.json` excluded | ✅ Done |

## UML Diagram Index

| Diagram | File | What it shows |
|---------|------|---------------|
| Class | `docs/uml/class-diagram.md` | Domain model, service interfaces, repository ABC |
| Object | `docs/uml/object-diagram.md` | Concrete runtime instances (demo session) |
| Use Case | `docs/uml/use-case-diagram.md` | Actor ↔ feature interactions (FR-01 – FR-11) |
| Activity | `docs/uml/activity-diagram.md` | "Save note" workflow with Start/End nodes (FR-01, FR-04, SPR-01) |
| Deployment | `docs/uml/deployment-diagram.md` | macOS node, Python runtime, data directory |

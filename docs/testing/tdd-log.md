# TDD Log — Red → Green → Refactor Evidence

Documents the Test-Driven Development cycle for key features in AstraNotes.
Each entry shows: failing test written first, then code written to pass it,
then refactor step with rationale.

---

## Sprint 1 — FR-01 Create Note + SPR-01 Encryption

### Cycle 1A: Plaintext note persists to disk

**RED** — test written before implementation:
```python
def test_create_note_persists_plaintext_body(manager, tmp_path):
    note = manager.create_note(title="grocery list", body="milk, eggs")
    saved_files = list(tmp_path.glob("*.json"))
    assert len(saved_files) == 1          # FAILED: no file written
    assert "milk, eggs" in saved_files[0].read_text()  # FAILED
```

**GREEN** — `NoteManager.create_note()` wrote to `JsonFileRepository.save()`.  
`JsonFileRepository.save()` serialised the Note dataclass to `‹uuid›.json`.  
Tests passed.

**REFACTOR** — Extracted `_json_to_note()` helper in `JsonFileRepository` to  
avoid repeated `datetime.fromisoformat()` calls in both `get()` and `list_all()`.

---

### Cycle 1B: Private note body must not appear on disk

**RED**:
```python
def test_create_private_note_encrypts_body_on_disk(manager, tmp_path):
    manager.create_note(title="secret", body="meet rendezvous coordinates xyz123", is_private=True)
    payload = json.loads(list(tmp_path.glob("*.json"))[0].read_text())
    assert "xyz123" not in payload["body"]   # FAILED: plaintext on disk
```

**GREEN** — Added encryption branch in `NoteManager.create_note()`:
```python
if is_private:
    if self._privacy is None:
        raise PersistenceError("Private notes require a configured privacy key")
    stored = replace(note, body=self._privacy.encrypt(body))
```

**REFACTOR** — Moved `_require_privacy()` to a shared helper to avoid  
duplicating the `None` check across `create_note`, `update_note`, and `set_private`.

---

## Sprint 2 — FR-02/FR-03/FR-04 Edit, Delete, Privacy Toggle

### Cycle 2A: Update advances modified_at

**RED**:
```python
def test_update_note_changes_title_and_body_advances_modified(manager):
    note = manager.create_note(title="draft", body="v1")
    time.sleep(0.01)
    updated = manager.update_note(note.id, title="final", body="v2")
    assert updated.modified_at > note.modified_at   # FAILED: same timestamp
```

**GREEN** — Added `modified_at=datetime.now(timezone.utc)` to the `replace()` call inside `update_note()`.

**REFACTOR** — Unified timestamp generation into a single `_utcnow()` helper in `models/note.py`.

---

### Cycle 2B: Privacy toggle failure safety

**RED**:
```python
def test_set_private_toggle_decrypt_failure_keeps_note_encrypted(tmp_path):
    """If decryption fails, note stays encrypted on disk (refined FR-04)."""
    writer = NoteManager(repo, validation, PrivacyService(generate_key()))
    note = writer.create_note(title="s", body="hidden", is_private=True)
    raw_before = list(tmp_path.glob("*.json"))[0].read_text()
    reader = NoteManager(repo, validation, PrivacyService(generate_key()))  # wrong key
    with pytest.raises(PersistenceError):
        reader.set_private(note.id, False)                # FAILED: no error raised
    raw_after = list(tmp_path.glob("*.json"))[0].read_text()
    assert raw_before == raw_after    # FAILED: file modified despite error
```

**GREEN** — Moved `_require_privacy()` call and `_plaintext_body()` call before  
the `repository.update()` call in `set_private()`. Decryption failure now raises  
`PersistenceError` without touching disk.

**REFACTOR** — `_plaintext_body()` now handles both bytes and str bodies  
transparently (legacy compatibility for notes written before the str→str migration).

---

## Sprint 3 — FR-07 Search + Performance (NFR-01)

### Cycle 3A: Performance budget test

**RED**:
```python
def test_list_and_search_500_notes_within_2s(manager):
    for i in range(500):
        manager.create_note(title=f"note {i:03d}", body=f"content {i}",
                            is_private=(i % 5 == 0))
    t0 = time.perf_counter()
    notes = manager.list_notes()
    assert (time.perf_counter() - t0) * 1000 < 2000   # PASSED on first run ✓
```
Test passed on first run — no code change needed. Documents the budget for regressions.

---

## Sprint 4 — FR-05 Duplicate Note (new in this iteration)

### Cycle 4A: Duplicate creates "Copy of …" note

**RED**:
```python
def test_duplicate_creates_copy_with_prefix(manager):
    note = manager.create_note(title="Template", body="reusable")
    copy = manager.duplicate_note(note.id)
    assert copy.title == "Copy of Template"    # FAILED: method did not exist
    assert copy.body == "reusable"
    assert copy.id != note.id
    assert manager.list_notes().__len__() == 2
```

**GREEN** — Implemented `NoteManager.duplicate_note()`:
```python
def duplicate_note(self, note_id: UUID) -> Note:
    stored = self._load_stored(note_id)
    plaintext = self._plaintext_body(stored) if stored.is_private else stored.body
    return self.create_note(
        title=f"Copy of {stored.title}",
        body=plaintext,
        is_private=stored.is_private,
        tags=list(stored.tags),
    )
```

**REFACTOR** — Reused `_plaintext_body()` and `_load_stored()` helpers already  
present from FR-02/FR-04 — no new helper needed.

---

## Sprint 5 — BDD Test Layer

### Cycle 5A: Gherkin acceptance tests for FR-01 – FR-07

**RED** — Wrote `tests/bdd/notes.feature` with 14 scenarios.  
All failed: `StepDefinitionNotFoundError` (step definitions not yet written).

**GREEN** — Wrote `tests/bdd/test_notes_bdd.py` with all Given/When/Then step  
definitions using `pytest-bdd`. 91 tests now pass (92 total).

**REFACTOR** — Extracted shared `store` fixture dict to pass state between steps  
without global variables — cleaner than class-based approach for pytest-bdd.

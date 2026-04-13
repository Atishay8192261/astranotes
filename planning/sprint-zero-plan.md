# AstraNotes — Sprint Zero Plan

**Student:** Atishay Jain | **Date:** April 10, 2026 | **Technical Path:** Python

**Sprint Duration:** Week 2.2 through end of Week 3
**Goal:** Establish the project foundation so that Sprint 1 can begin implementation with zero ambiguity about structure, tools, workflow, or architecture.

Sprint Zero is not a feature sprint. No user stories are marked Done at the end of Sprint Zero. The sprint is complete when the working environment, architecture skeleton, and planning artifacts are all in place and verified against the Definition of Done.

---

## Objective 1: Repository and Project Structure (NFR-02, SPR-04)
- Initialize a Python project repository with folders: `astranotes/` (models, repository, privacy, validation, cli), `tests/`, `planning/`, `docs/`.
- Add `pyproject.toml` listing only verified, licensed dependencies (cryptography for Fernet, pytest for testing) per SPR-04.
- Add a `.gitignore` appropriate for Python projects.
- Confirm the project runs with `python -m astranotes` without errors (placeholder CLI acceptable).
- **DoD check:** Structure matches architecture from Submission 1; no untracked dependencies; project runs cleanly.

## Objective 2: Note Data Model (FR-01, FR-07)
- Implement the Note dataclass: id (UUID), title (str), body (str), is_private (bool), created_at (datetime), modified_at (datetime), tags (list of str).
- Write unit tests: Note instantiates with valid fields; created_at and modified_at are set automatically; id is a valid UUID.
- **DoD check:** Model is explainable, tested, and traced to FR-01 and FR-07.

## Objective 3: NoteRepository Interface and JsonFileRepository (FR-05)
- Implement abstract NoteRepository with method signatures: save, get, list_all, update, delete.
- Implement JsonFileRepository that reads/writes individual `.json` files per note to a local data directory.
- Write unit test: a note can be saved to a temp directory and retrieved with matching fields.
- **DoD check:** Repository interface in place; save/load round trip passes; traced to FR-05.

## Objective 4: PrivacyService Skeleton (FR-04, SPR-01)
- Implement PrivacyService with `encrypt(body: str) -> bytes` and `decrypt(data: bytes) -> str` using Fernet (cryptography library).
- Write unit test: encrypting a string and decrypting it returns the original value; encrypted output is not equal to plaintext.
- *Risk note:* Key management is deferred to Sprint 1. A hardcoded test key is acceptable in the test suite only.
- **DoD check:** PrivacyService tested for basic round-trip; no plaintext stored for private notes; traced to SPR-01 and FR-04.

## Objective 5: ValidationLayer Skeleton (FR-01)
- Implement ValidationLayer with at least one rule: note title must be a non-empty string.
- Raise a custom ValidationError when the rule is violated.
- Write unit test: empty title raises ValidationError; valid title passes.
- **DoD check:** ValidationLayer tested and traced to FR-01.

## Objective 6: Planning Artifacts and Workflow Readiness (All)
- Create `planning/` directory containing requirements.md, user-stories.md, backlog.md, and sprint-zero-plan.md mirroring the Week 2.2 submission.
- Confirm the Architecture Decision Log from Week 1.2 is accessible and up to date in `docs/`.
- Establish `docs/prompt-log.md` and record Sprint Zero decisions as first entries.
- Confirm the Working Agreement and Definition of Done from Week 2.1 are applied to every Sprint Zero task.
- Run all unit tests and confirm 100% pass rate before Sprint Zero is closed.

---

## Sprint Zero Risks

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Fernet key management unclear for production use | Medium | Defer to Sprint 1; use test key only in Sprint Zero. Document in ADL. |
| JSON edge cases (corrupt files, missing notes) | Low | Implement basic error handling in Sprint Zero. Defer advanced recovery to US-07. |
| Sprint Zero expands into feature work | Medium | No user story is marked Done in Sprint Zero. Feature work stays in the backlog. |
| Architecture needs adjustment once skeleton code is written | Low–Med | Sprint Zero skeleton is the test. Update ADL before Sprint 1 if changes needed. |
| Scope creep from AI suggestions or own impulses | Medium | Working Agreement Section 1.2 and 1.5 scope discipline rules apply. |

---

## Sprint Zero Exit Criteria

Sprint Zero is complete only when all of the following are true:

- [ ] Project repository is initialized with the layered folder structure defined above.
- [ ] Note dataclass is implemented and has passing unit tests.
- [ ] NoteRepository interface and JsonFileRepository are implemented with a passing save/load round-trip test.
- [ ] PrivacyService is implemented with a passing encrypt/decrypt test.
- [ ] ValidationLayer is implemented with a passing title validation test.
- [ ] planning/ and docs/ folders are populated and current.
- [ ] All tests pass with 100% pass rate.
- [ ] No user story from the backlog is prematurely marked Done.

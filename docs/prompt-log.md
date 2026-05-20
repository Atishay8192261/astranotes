# AstraNotes - Prompt and Decision Log

**Student:** Atishay Jain | **Technical Path:** Python

This log records AI-assisted decisions following the Working Agreement (Section 1.3): for every significant decision, record the prompt used, the AI response summary, the quality assessment, and the action taken.

---

## Entry 001: Architecture Design (Week 1.2)
**Date:** April 1, 2026

**Prompt used:** Three-round refinement (weak -> strong -> refined) to design AstraNotes architecture. See submissions/Week1_2_Architecture_Decision_Log.pdf for full prompt text.

**AI response summary:** Produced a layered architecture with Note Entity, Repository Interface, JSON File Adapter, Privacy Service, Validation Layer, Version History Service, and Note Manager.

**Assessment:** The strong prompt produced a significantly better result than the weak prompt. The weak prompt lumped business logic and persistence together. The refined prompt produced clear component boundaries with single responsibilities.

**Action:** Accepted the refined architecture. Logged as ADR-001 through ADR-004.

---

## Entry 002: User Stories and Backlog (Week 2.2)
**Date:** April 10, 2026

**Prompt used:** Generate user stories from FR-01 through SPR-04 and the architecture components.

**AI response summary:** Produced 8 user stories with acceptance criteria. Suggested backlog ordering with search at priority 2.

**Assessment:** Stories were generic - restated requirements in "As a user..." format without referencing architecture components. Backlog ordering optimized for user value rather than technical dependency.

**Action:** Revised all stories to reference actual components (PrivacyService, JsonFileRepository, ValidationLayer) and domain exceptions. Reordered backlog: project setup first, privacy third (risk reduction). Rejected suggested tag-filtering story (not in committed requirements). Rejected Version History in initial backlog (premature).

---

## Entry 003: Requirement Refinement (Week 3.1)
**Date:** April 13, 2026

**Prompt used:** Challenge the Week 1.2 requirement set - find ambiguities, missing edge cases, weak assumptions.

**AI response summary:** Flagged hardware baseline gap (NFR-01/03), privacy toggle-off undefined state (FR-04), private notes in search gap (FR-07). Produced storage-layer edge case list.

**Assessment:** Accurate on the gaps that matched my own Sprint Zero observations. Some suggestions were out of scope.

**Action:** Accepted 6 ambiguities and 11 edge cases. Rejected: "no offline support" (scope decision, not ambiguity), "note versioning" (new feature, not refinement), "OS keychain as requirement" (design decision, not requirement), "concurrent writes" (single-user app).

---

## Entry 004: Sprint Zero Skeleton Implementation (Week 3.2)
**Date:** April 24, 2026

**Prompt used:** Execute Sprint Zero objectives 1-6 from planning/sprint-zero-plan.md, running pytest after each.

**AI response summary:** Produced the layered skeleton: `Note` dataclass (FR-01, FR-06), `NoteRepository` ABC and `JsonFileRepository` adapter (FR-05) with corrupt-file skip and PersistenceError translation, `PrivacyService` Fernet wrapper (SPR-01) wrapping InvalidToken into PersistenceError, and `ValidationLayer` enforcing non-empty/non-whitespace title (FR-01). Domain exceptions consolidated in `models/exceptions.py` (SPR-02). 21 unit tests, all passing.

**Assessment:** Build backend in `pyproject.toml` was set to a non-existent `setuptools.backends._legacy:_Backend` and editable install failed because setuptools auto-discovery picked up `planning/` and `submissions/` as packages. Both fixed by switching to `setuptools.build_meta` and adding an explicit `[tool.setuptools.packages.find]` include list. PrivacyService key management remains deferred to Sprint 1 per the Sprint Zero plan; tests use a hardcoded Fernet key only.

**Action:** Sprint Zero exit criteria met. No user story marked Done. Ready for Week 4.1 UML structural design and key-management ADR ahead of Sprint 1.

---

## Entry 005: UML Design Package (Week 4.2)
**Date:** April 27, 2026

**Prompt used:** Generate the complete UML design package for AstraNotes (class, object, use case, activity, deployment) as Mermaid files in docs/uml/ that reflect the implemented architecture from CLAUDE.md, then build a single submission PDF with reportlab.

**AI response summary:** Produced first-draft Mermaid for all five views, the requirements coverage matrix, and the design-rationale skeleton. Suggested using flowchart with stadium nodes as the closest faithful approximation for the (unsupported) UML use-case shape in Mermaid.

**Assessment:** Drafts were structurally fine but missed several real-code details: the AstraNotesError parent class, the InvalidToken to PersistenceError translation in PrivacyService, the SPR-02 user-friendly message step on both the validation and the persistence failure branches of the activity diagram, and the on-disk Disk subgraph that makes FR-05 / FR-06 visible in the object diagram. AI also overreached on scope (proposed an Administrator actor and an Export-to-cloud use case, and a separate Tag class), which all violate the single-user, single-tag-list reality of the implemented model.

**Action:** Accepted scaffolds, rewrote the exception hierarchy and added the missing edges and decision branches, added the Disk subgraph and the Fernet key store node with an "ADR pending" annotation, and rejected the scope-creep suggestions. Cross-checked all five diagrams against each other before building the PDF (no dashes, only hyphens). Submission saved to submissions/Week4_2_UML_Design_Package.pdf.

---

## Entry 006: Requirements-to-UML Traceability Matrix (Week 5.2)
**Date:** May 4, 2026

**Prompt used:** Build a requirements-to-UML traceability matrix for AstraNotes that validates the Week 4.2 UML package against the Week 3.1 refined requirement baseline; include a metrics summary, a gap analysis, and an AI reflection; produce a submittable PDF.

**AI response summary:** Drafted the matrix scaffold from refined-requirements.md and the coverage table already present in docs/uml/design-rationale.md, proposed status labels based on whether each requirement was named in any one diagram, and listed candidate orphan UML elements.

**Assessment:** AI's first-pass status labels were too generous because they treated "named in a diagram" as equivalent to "behaviorally modeled". FR-04, FR-05, and FR-07 each had use cases and class-diagram methods but were missing critical activity-diagram branches (toggle-off, corrupt-file skip, decrypt-during-search). AI also suggested adding NFR-01 and NFR-03 to the matrix as Not Traced, which would inflate the gap count without revealing a real design problem since both are runtime-performance assertions explicitly deferred to a Sprint 1 benchmark harness.

**Action:** Downgraded FR-04 and FR-05 to Partially Traced and FR-07 to Weakly Traced after re-reading the refined baseline. Rewrote every "Gap Note" cell to name a specific missing diagram or branch. Rejected adding NFR-01/NFR-03 to the scope of review. Identified two genuine orphan elements (the cross-platform OS list on the Workstation node, and PrivacyService.generate_key) and noted both as candidates for a Sprint 1 ADR-driven cleanup. Submission saved to submissions/Week5_2_Traceability_Matrix.pdf.

---

## Entry 007: Development Environment and First Realization Slices (Week 6.1)
**Date:** May 10, 2026

**Prompt used:** Implement the first two functionality slices behind the Week 4.2 UML package (US-01 create note, US-05 list/load on startup), wire them into a CLI shell, close the four Partial/Weak traceability gaps from Week 5.2 in-project (activity diagrams for FR-04 toggle, FR-05 startup, FR-07 search, and SPR-04 license labels on the deployment diagram), and produce a submittable PDF.

**AI response summary:** Copilot drafted NoteManager with self-constructed dependencies, suggested a Search menu item alongside list, and offered a delete-on-decrypt-fail path for list_notes. It also gave usable Mermaid skeletons for all three new activity diagrams in one pass and most of the test fixtures.

**Assessment:** The NoteManager scaffold violated NFR-02 because it instantiated its own JsonFileRepository and PrivacyService inside __init__, removing the DI seam that the class diagram has shown since Week 4.1 and that test_list_notes_skips_undecryptable_private_note needs. The Search menu suggestion was premature - US-06 is item 7 in the backlog and the service-layer search method does not exist yet. The delete-on-decrypt-fail suggestion conflicted with FR-07 ("exclude with error logged", not "remove from disk") and would have created silent data loss against SPR-02.

**Action:** Rewrote NoteManager constructor to accept repository, validation, and privacy as injected arguments. Rejected the Search menu and the delete-on-decrypt-fail behavior. Kept the Mermaid skeletons and only renamed nodes to match the existing class-diagram method names. Tightened list_notes to catch PersistenceError specifically, added the FR-08 created_at tiebreaker, and switched to dataclasses.replace so loaded Notes are not mutated in place (these three changes came from my own slice review, not from AI). 21 Sprint Zero tests still pass; 13 new tests cover NoteManager and the CLI shell. Submission saved to submissions/Week6_1_Development_Realization.pdf.

---

## Entry 008: Testing Strategy and First Test Set (Week 7.2)
**Date:** May 17, 2026

**Prompt used:** Build a shift-left testing strategy and a first test set for one or two AstraNotes features, trace every test to a requirement or user story, classify by unit/integration/feature level and development timing, and produce a submittable PDF following the established submission conventions.

**AI response summary:** Copilot brainstormed candidate test cases for the create and private-note features, critiqued the draft set for gaps, and proposed a negative on-disk assertion plus a no-key-configured case. It also suggested one combined create/list/edit/delete end-to-end test, a duplicate-tags-rejected test, and mocking Path.write_text in the repository tests.

**Assessment:** The negative security assertion (plaintext string must be absent from the file, not merely "looks encrypted") was the strongest suggestion and is now the most important assertion in the suite. The no-key-configured gap was real. The combined four-step end-to-end test was poor practice (a failure would not localize, and it smuggled US-02/US-03 into the create/private first set). The duplicate-tags-rejected test contradicted CLAUDE.md, which records duplicate tags as an accepted known limitation. Mocking the filesystem would create a false green if the real serialization path regressed - unacceptable for the persistence/privacy features specifically.

**Action:** Kept the absent-plaintext assertion, the no-key case, and the parametrize-whitespace-inputs idea. Split the combined test back into focused per-behavior tests. Rejected the duplicate-tags test and the filesystem mock; retained the tmp_path real-directory pattern per SPR-03. Documented the deliberate out-of-scope list (NFR-01/03, GUI rendering, US-06 search, FR-08 edge cases) as evidence of realistic first choices. Submission saved to submissions/Week7_2_Testing_Strategy.pdf. (Note: this session also begins the professor-mandated 3-tier GUI pivot and git history setup, logged separately as it lands.)

---

## Entry 009: Collaborative Git Workflow - Search Slice PR (Week 8.1)
**Date:** May 19, 2026

**Prompt used:** Use AstraNotes to practice the full branch -> commit -> PR -> review -> merge workflow with traceability. Implement the US-06 / FR-07 keyword-search slice on a focused feature branch, open a PR with a structured summary, self-review with at least one real (non-rubber-stamp) finding, and decide merge vs. hold based on whether the diff satisfies the acceptance criteria.

**AI response summary:** Copilot suggested an explicit `keyword.strip()` empty-guard plus an empty-and-whitespace-keyword test pair; a duplicated decrypt loop inside `search_notes` (initial draft); using two distinct `PrivacyService` instances for the undecryptable-search test instead of monkeypatching; a "search by tag" extension and a regex-mode toggle; a self-review PR comment that just listed the changes; and a critique of my review prose flagging "this might be slow" as un-quantified.

**Assessment:** The empty-keyword guard and the two-PrivacyService test pattern were strong - they honored FR-07's empty-collection rule for the empty-keyword edge and matched the project's no-mocked-storage convention from Week 7.2. The duplicated decrypt loop was the wrong shape: keeping decrypt-and-skip in one place (inside `list_notes()`) makes the SPR-01 contract easier to defend over time. Tag-search and regex-mode were direct violations of FR-07 ("plain string matching, not regex") and the Working Agreement's no-scope-creep rule. A PR comment that recaps the diff is review theater - reviews exist to surface what the diff is silent about. The critique on my own review prose was correct and made the keystroke-rebuild finding actionable instead of vague.

**Action:** Kept the empty-keyword guard, the test pair, and the two-PrivacyService pattern. Rewrote `search_notes` to delegate to `list_notes()` rather than duplicating the decrypt loop. Rejected the tag-search extension, the regex-mode toggle, and the recap-style PR comment. Rewrote the keystroke-rebuild review note to name the NFR-01 target and the dominating cost (Fernet decryption). The keep/change/reject decisions, the two review findings (silent-skip-on-decrypt-failure + keystroke-rate sidebar rebuild), and the merge call were mine, not AI's. Branch: `feature/search-notes`. PR: #1 (squash-merged into main). Tests: 40 -> 46 passing. Submission saved to submissions/Week8_1_Collaborative_Git_Workflow.pdf.

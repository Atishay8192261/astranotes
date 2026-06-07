# AI Interaction Log — AstraNotes

Records the major architectural decisions, technology stack choices, and
design tradeoffs made with AI assistance (an AI pair-programming assistant).
Only architectural decision points are logged here — routine coding prompts
are omitted per the course guidance.

---

## Decision 1 — GUI Framework Choice (ADR-006)

**Date:** 2026-05-17  
**Prompt summary:** "We need to pivot from CLI to a GUI. What GUI framework should I use for a single-user Python desktop app that needs to pass SCU CSEN 296B grading?"

**Options considered:**

| Framework | Pros | Cons |
|-----------|------|-------|
| Tkinter (built-in) | Zero extra dependency | Dated look; hard to theme |
| PyQt6 | Polished, powerful | GPL licence; large; needs Qt runtime |
| **CustomTkinter** | Modern look, pure Python, CC0 licence | Smaller community |
| Electron + Python | Web-like UI | Too complex; mixed-language stack |

**Decision:** CustomTkinter — licence is compatible with SPR-03 (CC0 > MIT/Apache/BSD); no Qt runtime needed; pure Python means existing test infrastructure runs unchanged.

**Rationale recorded in:** `docs/uml/deployment-diagram.md` (tier labels), ADR-006 in commit `de5bbd5`.

---

## Decision 2 — Encryption Architecture (SPR-01 / SPR-04)

**Date:** 2026-05-10  
**Prompt summary:** "What's the right way to encrypt private note bodies? I need authenticated encryption, no key persisted to disk."

**Options considered:**

| Approach | Security | Complexity |
|----------|----------|------------|
| AES-CBC raw (manual) | Good if done right | High — need IV, padding, HMAC manually |
| **Fernet (cryptography lib)** | Authenticated AES-128-CBC + HMAC-SHA256 | Low — single call |
| AES-GCM | Modern AEAD | Slightly more complex; overkill for local |
| GPG | Battle-tested | External binary dependency |

**Decision:** Fernet from the `cryptography` library. It provides authenticated encryption (prevents ciphertext tampering), has a one-call API, and the library is Apache 2.0 / BSD licensed.

**Key derivation decision:** PBKDF2-HMAC-SHA256 with 600 000 iterations and a 16-byte random salt. 600 k chosen as OWASP 2023 recommendation. Key stored only in memory — `passphrase.json` holds only the salt + a Fernet-encrypted verifier blob.

---

## Decision 3 — Single-User vs Multi-User Scope

**Date:** 2026-05-10  
**Prompt summary:** "The professor says web app with multiple authenticated users is preferred. Should we pivot to Flask/Django?"

**Trade-offs considered:**

| Factor | Web (multi-user) | Local desktop (single-user) |
|--------|------------------|-----------------------------|
| Complexity | High (auth, sessions, DB migrations, HTTPS) | Low |
| Grading impression | Higher ceiling | Lower ceiling — "simple app" risk |
| Development time remaining | 4 weeks | 4 weeks |
| 3-tier MVC clarity | Easy with Django | Equally demonstrable with GUI |

**Decision:** Stay with local desktop. Rationale: The 3-tier MVC is demonstrably strict (view holds no business logic, controller is headlessly testable), encryption-at-rest is a real security feature not typically found in class projects, and the remaining week budget did not allow a safe web pivot. The admin/telemetry panel, BDD tests, GitHub Actions CI, and desktop .app bundle close the impressiveness gap.

---

## Decision 4 — Privacy Model: "Private" vs "Public" semantics

**Date:** 2026-06-07  
**Prompt summary:** Friend identified that private notes disappeared silently when app had no passphrase. Professor expects locked notes to be visible but unreadable. How to fix?

**Options:**
1. Keep current: silently skip locked notes in `list_notes()` ← tests already cover this
2. Add `list_all_for_display()` that shows locked notes with 🔒, keep `list_notes()` unchanged

**Decision:** Option 2. `list_notes()` behaviour (skip locked) is correct for programmatic/security use; `list_all_for_display()` is the new GUI path. Tests for `list_notes()` don't break. The UI shows locked notes with a lock icon and prompts for passphrase on click — matching professor's expected UX.

---

## Decision 5 — Repository Storage Format

**Date:** 2026-05-10  
**Prompt summary:** "Should notes be stored in a single SQLite database, individual JSON files, or YAML?"

**Decision:** One JSON file per note (UUID as filename). 

**Rationale:** Simplest path to implement the repository pattern (ABC); no schema migrations; each note is an independent file so corruption of one does not affect others; easy to inspect/debug during development; NFR-01 performance budget (2 s for 500 notes) is easily met.

**Future migration path:** The `NoteRepository` ABC means switching to SQLite is a one-file change (`repositories/sqlite.py`) with zero changes to `NoteManager` or the GUI.

---

## Decision 6 — Test Infrastructure: Real Storage vs Mocks

**Date:** 2026-05-30  
**Prompt summary:** "Our security tests got burned last quarter when mocked storage masked a real bug. How should we test encryption?"

**Decision:** All security-critical test paths (`test_note_manager.py`, `test_privacy.py`, BDD encryption scenarios) use real `JsonFileRepository` with `tmp_path` pytest fixtures. No mocked storage in any encryption test.

**Rationale:** A mocked encrypt/decrypt path would not catch ciphertext-to-disk bugs (SPR-01). The one-file-per-note JSON design makes real-storage tests trivially fast (< 10 s for 92 tests).

---

## Human Oversight Summary — Accepted / Refined / Rejected

The rubric asks specifically what was accepted, refined, or rejected through
human oversight. AI was used as a pair-programmer across the SDLC (requirements
drafting, UML generation, code scaffolding, test design), but no AI output was
merged without human cross-examination. Concrete examples:

### Accepted (verified, then kept)
- **Fernet + PBKDF2-HMAC-SHA256 (600k)** for encryption. Accepted *after*
  confirming Fernet is authenticated (AES-128-CBC + HMAC) and the iteration
  count against the OWASP 2023 guidance — not on the AI's word alone.
- **One-JSON-file-per-note repository** behind a `NoteRepository` ABC. Accepted
  because it kept the migration path to SQLite a single-file change.
- **3-tier separation** (view → controller → services → repository). Accepted
  and then *enforced* with headless controller tests to prove the view holds
  no logic.

### Refined (AI draft was a starting point, then changed)
- **Theme:** AI defaulted to CustomTkinter's stock blue. Refined into a custom
  warm-white / violet token palette so the UI is distinguishable and readable.
- **Private-note visibility:** AI's first implementation silently skipped
  locked notes. Refined into `list_all_for_display()` so locked notes appear
  with a 🔒 and an unlock prompt — `list_notes()` kept for the secure path.
- **Vault UX:** refined the single-passphrase model into an explicit
  lock/unlock-all control and a passphrase-change flow that re-verifies the
  current passphrase before rotating.

### Rejected (AI suggestion declined after review)
- **Mocked storage in security tests** — rejected. A mocked encrypt/decrypt
  path can hide a real ciphertext-to-disk bug, so all encryption tests use a
  real `JsonFileRepository` on a `tmp_path`.
- **Raw manual AES-CBC** — rejected in favour of Fernet to avoid hand-rolling
  IV/padding/HMAC, a classic source of crypto bugs.
- **Pivot to a Flask/Django multi-user web app** — rejected given the remaining
  time budget; the risk of a half-finished web app outweighed the ceiling.
- **AI-generated `fg_color=("transparent", "transparent")`** — rejected at the
  code level; CustomTkinter forbids a transparency tuple and it crashed on
  launch. Caught by running the app, not by trusting the snippet.
- **`source venv/bin/activate` in the macOS .app launcher** — rejected after it
  failed under the macOS sandbox; replaced with a direct interpreter path.

The throughline: AI accelerated drafting, but every security-, architecture-,
and correctness-relevant output was tested or reasoned through before adoption.

# AstraNotes — Runbook

Operational guide for deploying, running, and demonstrating AstraNotes.

---

## Prerequisites

| Tool | Required version | Check |
|------|-----------------|-------|
| Python | ≥ 3.10 | `python3 --version` |
| Tcl/Tk (macOS) | bundled with Python or via Homebrew | `python3 -c "import tkinter"` |
| Git | any | `git --version` |

**macOS — install Tk if missing:**
```bash
brew install python-tk@3.11
```

---

## 1. First-Time Setup

```bash
# Clone
git clone https://github.com/Atishay8192261/astranotes.git
cd astranotes-project

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate

# Install app + dev dependencies
pip install -e ".[dev]"
```

---

## 2. Run the Application

```bash
source venv/bin/activate
python -m astranotes
```

Or double-click **AstraNotes.app** on your Desktop (macOS, no terminal needed).

### First-launch behaviour

- No passphrase configured → app opens unlocked.
- First time you save a private note → passphrase setup dialog appears.
- Subsequent launches → passphrase unlock dialog appears if `~/.astranotes/passphrase.json` exists.

---

## 3. Seed Demo Data (for grader demos)

```bash
# Generates 12 notes (8 public + 4 private) in ./demo-data/
python scripts/seed_demo_notes.py --clean --passphrase <choose-any-passphrase>

# Launch app pointing at demo data (leaves ~/.astranotes/ untouched)
ASTRANOTES_DATA_DIR=demo-data \
ASTRANOTES_PASSPHRASE_PATH=demo-data/passphrase.json \
python -m astranotes
```

Enter the same passphrase you used above when the unlock dialog appears.

---

## 4. Run Tests

```bash
source venv/bin/activate

# All unit + BDD tests
pytest -q

# BDD tests only (Gherkin scenarios)
pytest tests/bdd/ -v

# With legacy CLI tests
pytest -q --run-cli
```

Expected: **92 passed, 5 skipped** (CLI tests quarantined; pass `--run-cli` to include).

---

## 5. Configuration

| Environment variable | Default | Purpose |
|----------------------|---------|---------|
| `ASTRANOTES_DATA_DIR` | `~/.astranotes/notes` | Directory where note JSON files are stored |
| `ASTRANOTES_PASSPHRASE_PATH` | `~/.astranotes/passphrase.json` | Path to salt + verifier file |
| `ASTRANOTES_KEY` | unset | Legacy: raw 32-byte Fernet key (bypasses passphrase dialog) |

---

## 6. Application Layout

```
astranotes-project/
├── astranotes/
│   ├── gui/          ← Presentation tier (CustomTkinter view + controller)
│   ├── services/     ← Logic tier (NoteManager, PrivacyService, EventLogger)
│   ├── repositories/ ← Data tier (JsonFileRepository)
│   └── models/       ← Domain entities (Note) + exceptions
├── tests/
│   ├── bdd/          ← Gherkin .feature file + pytest-bdd step definitions
│   └── test_*.py     ← Unit tests (headless, real storage)
├── docs/
│   ├── requirements/ ← PRD, Traceability Matrix
│   ├── uml/          ← 5 UML diagrams (Mermaid, renders on GitHub)
│   ├── testing/      ← BDD acceptance criteria, TDD log
│   └── ai-log/       ← AI-assisted decision log (architectural decisions only)
├── demo-data/        ← Encrypted demo notes (passphrase supplied at runtime)
├── scripts/          ← seed_demo_notes.py
├── .github/
│   └── workflows/
│       └── ci.yml    ← GitHub Actions: test + SAST + lint
├── pyproject.toml
├── RUNBOOK.md        ← This file
└── README.md
```

---

## 7. Event Log

Every button click and action is recorded to `~/.astranotes/events.log`
(JSON-lines format) for grader inspection:

```jsonc
{"ts": "2026-06-07T10:30:00Z", "action": "app_started",    "detail": "AstraNotes launched"}
{"ts": "2026-06-07T10:30:05Z", "action": "note_created",   "detail": "title='Shopping List' private=False"}
{"ts": "2026-06-07T10:30:12Z", "action": "note_selected",  "detail": "id=abc... title='Shopping List' locked=False"}
{"ts": "2026-06-07T10:30:20Z", "action": "admin_panel_opened", "detail": ""}
```

---

## 8. Security Review

```bash
# Run SAST scan locally (same as CI)
pip install bandit
bandit -r astranotes/ -ll --skip B603,B607
```

Known findings: none above MEDIUM severity.

---

## 9. Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ModuleNotFoundError: No module named 'customtkinter'` | venv not activated or deps not installed | `source venv/bin/activate && pip install -e ".[dev]"` |
| `_tkinter.TclError` or blank window on macOS | Tk not installed for this Python version | `brew install python-tk@3.11` |
| Unlock dialog appears on every launch | `passphrase.json` exists from a previous session | Enter your passphrase, or delete `~/.astranotes/passphrase.json` to reset |
| Private notes show 🔒 in sidebar | App launched without entering passphrase | Click a 🔒 note to trigger the unlock dialog |
| `pytest: command not found` | venv not active | `source venv/bin/activate` |

---

## 10. CI / CD

GitHub Actions runs on every push and pull request:

- **test** — `pytest -q` on Python 3.11 and 3.12
- **security** — `bandit` SAST scan on the `astranotes/` package
- **lint** — `ruff` on `astranotes/` and `tests/`

All three jobs must pass for a PR to be mergeable.

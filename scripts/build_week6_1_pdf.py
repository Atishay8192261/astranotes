"""Build the Week 6.1 Development Environment and First Realization Slices PDF.

Run from the project root:
    python scripts/build_week6_1_pdf.py
"""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Table,
    TableStyle,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = PROJECT_ROOT / "submissions" / "Week6_1_Development_Realization.pdf"


def cell(text: str, font_size: float = 9.5, color: str = "#111111") -> Paragraph:
    style = ParagraphStyle(
        "cell",
        fontName="Helvetica",
        fontSize=font_size,
        leading=font_size + 2.5,
        textColor=colors.HexColor(color),
    )
    return Paragraph(text, style)


def header_cell(text: str) -> Paragraph:
    style = ParagraphStyle(
        "hdr",
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=12,
        textColor=colors.white,
    )
    return Paragraph(text, style)


def styled_table(data, col_widths) -> Table:
    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#222222")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#f7f7f7")],
                ),
            ]
        )
    )
    return table


def build() -> Path:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    page_size = LETTER

    doc = BaseDocTemplate(
        str(OUT_PATH),
        pagesize=page_size,
        leftMargin=0.65 * inch,
        rightMargin=0.65 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
        title="Week 6.1 Development Environment and First Realization Slices - AstraNotes",
        author="Atishay Jain",
    )

    frame = Frame(
        0.65 * inch,
        0.6 * inch,
        page_size[0] - 1.3 * inch,
        page_size[1] - 1.2 * inch,
        id="portrait",
    )
    doc.addPageTemplates([PageTemplate(id="P", frames=[frame], pagesize=page_size)])

    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=15, spaceAfter=4)
    sub = ParagraphStyle(
        "sub", parent=styles["Heading3"], fontSize=11, textColor=colors.grey, spaceAfter=10
    )
    info = ParagraphStyle("info", parent=styles["Normal"], fontSize=10, leading=14, spaceAfter=12)
    h2 = ParagraphStyle(
        "h2", parent=styles["Heading2"], fontSize=13, spaceBefore=10, spaceAfter=6
    )
    h3 = ParagraphStyle(
        "h3", parent=styles["Heading3"], fontSize=11.5, spaceBefore=8, spaceAfter=4
    )
    body = ParagraphStyle(
        "body", parent=styles["Normal"], fontSize=10.5, leading=14, spaceAfter=8
    )
    code = ParagraphStyle(
        "code",
        parent=styles["Code"],
        fontName="Courier",
        fontSize=8.5,
        leading=10.5,
        leftIndent=8,
        spaceBefore=4,
        spaceAfter=10,
        textColor=colors.HexColor("#222222"),
        backColor=colors.HexColor("#f3f3f3"),
        borderPadding=4,
    )

    page_w = page_size[0] - 1.3 * inch

    story = []

    # ---- Cover ----------------------------------------------------------------
    story.append(Paragraph("CSEN 296B-2 | Week 6.1 Lab Submission", h1))
    story.append(
        Paragraph("Connecting Design to Prototype - AstraNotes Realization Slices", sub)
    )
    story.append(
        Paragraph(
            "<b>Student Name:</b> Atishay Jain &nbsp;|&nbsp; "
            "<b>Date:</b> May 10, 2026 &nbsp;|&nbsp; "
            "<b>Project:</b> AstraNotes &nbsp;|&nbsp; "
            "<b>Technical Path:</b> Python",
            info,
        )
    )
    story.append(
        Paragraph(
            "This is the first week I am writing code that a user could "
            "actually run. I took two slices that have been waiting in the "
            "backlog since Week 2.2 (US-01 create a note, US-05 list and load "
            "on startup) and wired them through the layered architecture that "
            "the Week 4.2 UML package committed to. The Sprint Zero skeleton "
            "already had the entity, repository adapter, privacy service, and "
            "validation layer; the missing pieces were the <i>NoteManager</i> "
            "orchestrator and a runnable CLI shell that ties the layers "
            "together. Everything below sits inside that frame - I did not "
            "introduce new components, new dependencies, or new requirements.",
            body,
        )
    )

    # ---- Development Direction ------------------------------------------------
    story.append(Paragraph("Development Direction", h2))
    direction_rows = [
        [header_cell("Decision"), header_cell("Choice"), header_cell("Reason")],
        [
            cell("Language"),
            cell("Python 3.10+"),
            cell(
                "Locked in Week 1.2 (ADR-001). Every diagram, test, and "
                "dependency I have already submitted assumes it."
            ),
        ],
        [
            cell("App form"),
            cell("Local desktop CLI<br/>(<i>python -m astranotes</i>)"),
            cell(
                "Already committed in five places: Sprint Zero plan, use case "
                "diagram, activity diagram, deployment diagram (<i>cli/</i> "
                "subgraph), and CLAUDE.md. A GUI or TUI this week would "
                "contradict the Week 4.2 UML package."
            ),
        ],
        [
            cell("UI library"),
            cell("None - plain <i>input()</i> / stdout"),
            cell(
                "Matches the deployment diagram. Avoids adding a third-party "
                "UI dep that has not been vetted under SPR-04."
            ),
        ],
        [
            cell("Encryption library"),
            cell("cryptography 44.0.0 (Fernet)"),
            cell(
                "Already in <i>pyproject.toml</i>, already documented under "
                "SPR-01 and SPR-04. No change."
            ),
        ],
    ]
    story.append(styled_table(direction_rows, [1.3 * inch, 1.9 * inch, page_w - 3.2 * inch]))

    story.append(
        Paragraph(
            "The rubric mentions menu/profile/settings/notes as UI areas to "
            "make decisions about. I read that as a checklist of "
            "<i>decisions</i>, not a checklist of <i>screens</i> - the "
            "professor's wording is 'layout decisions'. Since AstraNotes is "
            "single-user with no accounts (a Sprint Zero design call), I do "
            "not ship a profile screen. The Settings screen states this "
            "explicitly so the omission is visible rather than silent.",
            body,
        )
    )

    # ---- Project Structure and Run Environment --------------------------------
    story.append(Paragraph("Project Structure and Run Environment", h2))
    story.append(
        Paragraph(
            "The Sprint Zero layout is the same one the Week 4.2 deployment "
            "diagram drew. Week 6 added one new module "
            "(<i>services/note_manager.py</i>) and filled in the previously-"
            "empty <i>cli/</i> folder.",
            body,
        )
    )
    tree = (
        "astranotes/\n"
        "  __main__.py                # entry point: python -m astranotes\n"
        "  cli/\n"
        "    app.py                   # NEW this week - text menu shell\n"
        "  models/\n"
        "    note.py                  # Note dataclass            (Sprint Zero)\n"
        "    exceptions.py            # AstraNotesError family    (Sprint Zero)\n"
        "  repositories/\n"
        "    base.py                  # NoteRepository ABC        (Sprint Zero)\n"
        "    json_file.py             # JsonFileRepository        (Sprint Zero)\n"
        "  services/\n"
        "    note_manager.py          # NEW this week - orchestrator\n"
        "    privacy.py               # PrivacyService (Fernet)   (Sprint Zero)\n"
        "    validation.py            # ValidationLayer           (Sprint Zero)\n"
        "tests/\n"
        "  test_note.py, test_repository.py, test_privacy.py,\n"
        "  test_validation.py         # 21 tests from Sprint Zero, still passing\n"
        "  test_note_manager.py       # NEW - 8 tests\n"
        "  test_cli.py                # NEW - 5 tests\n"
        "pyproject.toml               # cryptography==44.0.0, pytest==8.3.4 [dev]"
    )
    story.append(Preformatted(tree, code))

    story.append(
        Paragraph(
            "<b>Run environment.</b> macOS / Linux / Windows with Python "
            "3.10+ and a virtualenv. Install with "
            "<i>pip install -e \".[dev]\"</i>. Tests run with <i>pytest</i> "
            "(no external services; all I/O goes through <i>tmp_path</i> "
            "fixtures per SPR-03). The app runs with "
            "<i>python -m astranotes</i>. Data directory is "
            "<i>~/.astranotes/notes</i> by default, overridable via "
            "<i>ASTRANOTES_DATA_DIR</i>. The Fernet key is read from "
            "<i>ASTRANOTES_KEY</i>; if it is not set, the app prints a visible "
            "warning and generates a session-only key so private notes still "
            "work for a demo run - the persistent-key storage decision is the "
            "open SPR-01 ADR.",
            body,
        )
    )

    # ---- UI Shell -------------------------------------------------------------
    story.append(PageBreak())
    story.append(Paragraph("UI Shell", h2))
    story.append(Paragraph("The CLI presents one main menu:", body))
    menu_text = (
        "AstraNotes - main menu\n"
        "  1) Create a note\n"
        "  2) List notes\n"
        "  3) Settings\n"
        "  4) About\n"
        "  5) Quit\n"
        "Choose [1-5]:"
    )
    story.append(Preformatted(menu_text, code))

    story.append(
        Paragraph(
            "<b>Notes workspace</b> = options 1 and 2. Option 1 prompts for "
            "title, body, and a y/N for <i>is_private</i>, then calls "
            "<i>NoteManager.create_note</i>. Option 2 calls "
            "<i>NoteManager.list_notes</i> and prints each note in "
            "<i>modified_at</i> descending order with a <i>[private]</i> "
            "flag and a 60-char snippet.",
            body,
        )
    )
    story.append(
        Paragraph(
            "<b>Settings</b> = option 3. Prints the resolved data directory, "
            "the privacy key source (<i>ASTRANOTES_KEY</i> env var or "
            "'dev key (session only)'), and an explicit note that the profile "
            "screen is intentionally omitted.",
            body,
        )
    )
    story.append(
        Paragraph(
            "<b>About</b> = option 4. App name, version, course, and "
            "one-line summary of the storage and privacy rules. "
            "<b>Quit</b> = option 5.",
            body,
        )
    )
    story.append(
        Paragraph(
            "All four behavioral paths are covered by "
            "<i>tests/test_cli.py</i>. <i>run()</i> takes <i>inp</i> and "
            "<i>out</i> as parameters so the tests drive it with a "
            "<i>StringIO</i> and an iterator of scripted answers - no real "
            "keyboard or screen involved. That dependency-injection seam is "
            "exactly what NFR-02 asked for.",
            body,
        )
    )

    # ---- Slices ---------------------------------------------------------------
    story.append(Paragraph("First Functionality Slices", h2))

    story.append(Paragraph("Slice 1 - Create a note (US-01, FR-01, FR-04, SPR-01)", h3))
    story.append(
        Paragraph(
            "<i>NoteManager.create_note(title, body, is_private, tags)</i> "
            "does four things in order:",
            body,
        )
    )
    for n, line in enumerate(
        [
            "Build a fresh Note dataclass - UUID and timestamps come from "
            "the entity's default factories (FR-01, FR-06).",
            "<i>ValidationLayer.validate(note)</i> - raises "
            "<i>ValidationError</i> on whitespace-only titles before "
            "anything touches disk.",
            "If <i>is_private</i> is true, encrypt the body with "
            "<i>PrivacyService.encrypt</i> and store a copy of the Note "
            "with the ciphertext body. If <i>is_private</i> is true and no "
            "<i>PrivacyService</i> was injected, raise <i>PersistenceError</i> "
            "rather than silently downgrading. The plaintext stays in the "
            "return value so the caller sees the readable note.",
            "<i>JsonFileRepository.save(stored)</i> - one "
            "<i>{uuid}.json</i> file per note.",
        ],
        start=1,
    ):
        story.append(Paragraph(f"<b>{n}.</b> {line}", body))
    story.append(
        Paragraph(
            "This slice realizes the exact left-hand and middle columns of "
            "<i>docs/uml/activity-diagram.mmd</i> (the 'Create a private "
            "note' workflow). The validation gate, the <i>is_private?</i> "
            "branch, and the encrypt-before-save ordering are all preserved.",
            body,
        )
    )

    story.append(
        Paragraph(
            "Slice 2 - List and load on startup (US-05, FR-05, FR-07, FR-08, SPR-02)",
            h3,
        )
    )
    story.append(
        Paragraph(
            "<i>NoteManager.list_notes()</i> walks the repository, decrypts "
            "private notes that have a working key, and sorts the result.",
            body,
        )
    )
    list_code = (
        "def list_notes(self) -> list[Note]:\n"
        "    loaded = self._repository.list_all()\n"
        "    visible: list[Note] = []\n"
        "    for stored in loaded:\n"
        "        if stored.is_private:\n"
        "            if self._privacy is None:\n"
        "                logger.error(\"Skipping private note %s: no privacy key\", stored.id)\n"
        "                continue\n"
        "            try:\n"
        "                plaintext = self._privacy.decrypt(stored.body)\n"
        "            except PersistenceError as exc:\n"
        "                logger.error(\"Skipping note %s: decrypt failed (%s)\", stored.id, exc)\n"
        "                continue\n"
        "            visible.append(replace(stored, body=plaintext))\n"
        "        else:\n"
        "            visible.append(stored)\n"
        "    visible.sort(key=lambda n: (n.modified_at, n.created_at), reverse=True)\n"
        "    return visible"
    )
    story.append(Preformatted(list_code, code))
    story.append(
        Paragraph(
            "<i>JsonFileRepository.list_all()</i> was already doing the "
            "corrupt-file skip-and-log on disk-side errors (Sprint Zero). "
            "<i>NoteManager.list_notes()</i> adds the privacy-side "
            "skip-and-log: a note that cannot be decrypted does not crash the "
            "list, it is just hidden with an error logged. That is exactly "
            "the behavior the refined baseline asked for under FR-07.",
            body,
        )
    )

    # ---- Self-Review ----------------------------------------------------------
    story.append(PageBreak())
    story.append(Paragraph("Self-Review of Slice 2", h2))
    story.append(
        Paragraph(
            "I reviewed <i>NoteManager.list_notes()</i> in detail before "
            "declaring it done. Three things I noticed and fixed:",
            body,
        )
    )
    for n, line in enumerate(
        [
            "<b>First draft caught a bare <i>Exception</i> around <i>decrypt</i>.</b> "
            "I tightened it to <i>PersistenceError</i> so an unrelated bug "
            "(say, a <i>TypeError</i> from a corrupt payload) does not look "
            "like a decrypt failure. The narrower catch is consistent with "
            "<i>JsonFileRepository</i>, which only catches <i>OSError</i>, "
            "<i>JSONDecodeError</i>, <i>KeyError</i>, and <i>ValueError</i>.",
            "<b>First draft sorted by <i>modified_at</i> only.</b> FR-08 "
            "specifies <i>created_at</i> as the tiebreaker, so I changed the "
            "key to <i>(modified_at, created_at)</i>. Two notes saved in the "
            "same millisecond would otherwise come back in undefined order "
            "on different file systems.",
            "<b>First draft mutated the loaded Note in place</b> by "
            "reassigning <i>stored.body = plaintext</i>. That works but it "
            "edits the object the repository handed back, which would be "
            "confusing if anyone holds a reference to it. I switched to "
            "<i>dataclasses.replace</i>, which returns a fresh Note with the "
            "plaintext body and leaves the original alone. This matches the "
            "same pattern in <i>create_note</i> and keeps the function "
            "side-effect free.",
        ],
        start=1,
    ):
        story.append(Paragraph(f"<b>{n}.</b> {line}", body))

    story.append(
        Paragraph(
            "<b>Quality lesson.</b> The pattern I keep falling into is 'make "
            "it work, then notice the failure mode'. For Slice 2 the issues I "
            "noticed before shipping (missing tiebreaker, broad except, "
            "in-place mutation) were all things a code reviewer would flag "
            "in five seconds. The lesson is to run each slice through the "
            "SPR-02 / NFR-02 lens explicitly before calling it done - 'what "
            "fails, what gets logged, can I still test this in isolation' - "
            "instead of waiting for the tests to surface it. Two of the three "
            "issues above had no failing test, just bad shape.",
            body,
        )
    )

    # ---- Traceability ---------------------------------------------------------
    story.append(Paragraph("Traceability", h2))
    trace_rows = [
        [
            header_cell("Slice"),
            header_cell("Requirements realized"),
            header_cell("UML elements realized"),
        ],
        [
            cell("Slice 1<br/><i>NoteManager.create_note</i>"),
            cell(
                "FR-01 (create + validate + auto-id/timestamps), FR-04 "
                "(encrypt-on-save when <i>is_private</i>), FR-06 (UTC "
                "timestamps via Note factories), SPR-01 (Fernet before disk), "
                "SPR-02 (<i>ValidationError</i> / <i>PersistenceError</i> "
                "raised, never raw tracebacks)"
            ),
            cell(
                "<i>class-diagram.mmd</i>: <i>NoteManager</i>, "
                "<i>ValidationLayer</i>, <i>PrivacyService</i>, "
                "<i>JsonFileRepository</i>, <i>Note</i>, AstraNotesError "
                "family. <i>activity-diagram.mmd</i>: every step on the "
                "create-private path. <i>use-case-diagram.mmd</i>: UC1, UC4. "
                "<i>object-diagram.mmd</i>: note2 (the encrypted runtime "
                "instance)."
            ),
        ],
        [
            cell("Slice 2<br/><i>NoteManager.list_notes</i> + CLI option 2"),
            cell(
                "FR-05 (load from disk, skip corrupt), FR-07 "
                "(decrypt-then-include, skip-decrypt-fail), FR-08 (sort by "
                "modified_at desc with created_at tiebreaker), NFR-02 (DI "
                "seam exercised), SPR-02 (errors logged, never surfaced as "
                "tracebacks)"
            ),
            cell(
                "<i>class-diagram.mmd</i>: <i>NoteManager.list_notes</i>, "
                "<i>JsonFileRepository.list_all</i>. New "
                "<i>activity-startup.mmd</i> and <i>activity-search.mmd</i> "
                "(added this week to close the Week 5.2 gaps). "
                "<i>use-case-diagram.mmd</i>: UC6, UC7."
            ),
        ],
        [
            cell("CLI shell"),
            cell(
                "NFR-02 (DI for <i>inp</i> / <i>out</i>), SPR-02 "
                "(AstraNotesError caught at the top of each menu action)"
            ),
            cell(
                "<i>deployment-diagram.mmd</i>: the <i>cli/</i> subgraph that "
                "was previously tagged 'Sprint 1' is now populated."
            ),
        ],
    ]
    story.append(styled_table(trace_rows, [1.4 * inch, 2.6 * inch, page_w - 4.0 * inch]))
    story.append(
        Paragraph(
            "The deployment diagram's <i>cli/</i> node is no longer a "
            "placeholder - <i>astranotes/cli/app.py</i> exists and is the "
            "entry point the menu actually runs from.",
            body,
        )
    )

    # ---- In-project clean-up --------------------------------------------------
    story.append(PageBreak())
    story.append(Paragraph("In-Project Clean-up Shipped Alongside This Slice", h2))
    story.append(
        Paragraph(
            "These were the four 'Partially Traced' and 'Weakly Traced' "
            "items I flagged at the end of the Week 5.2 traceability matrix. "
            "They are now closed at the artifact level, not just on paper:",
            body,
        )
    )
    cleanup_rows = [
        [header_cell("Artifact"), header_cell("Change")],
        [
            cell("<i>docs/uml/activity-search.mmd</i>"),
            cell(
                "New. FR-07 decrypt-then-match with skip-and-log and "
                "empty-collection short-circuit."
            ),
        ],
        [
            cell("<i>docs/uml/activity-startup.mmd</i>"),
            cell(
                "New. FR-05 first-launch directory creation plus the load "
                "loop's skip-and-log."
            ),
        ],
        [
            cell("<i>docs/uml/activity-toggle-privacy.mmd</i>"),
            cell(
                "New. FR-04 toggle-back-to-plaintext and "
                "decrypt-failure-keeps-encrypted branches."
            ),
        ],
        [
            cell("<i>docs/uml/deployment-diagram.mmd</i>"),
            cell(
                "Updated. SPR-04 license strings (Apache 2.0 / BSD for "
                "cryptography, MIT for pytest) now visible on the Deps nodes."
            ),
        ],
    ]
    story.append(styled_table(cleanup_rows, [2.4 * inch, page_w - 2.4 * inch]))

    # ---- AI Reflection --------------------------------------------------------
    story.append(Paragraph("AI Reflection", h2))
    story.append(
        Paragraph(
            "I used GitHub Copilot in two modes this week.",
            body,
        )
    )
    story.append(
        Paragraph(
            "<b>Where Copilot helped.</b> Inside the editor it suggested most "
            "of the boilerplate I expected - <i>from __future__ import "
            "annotations</i> at the top of each new module, the "
            "abstract-method docstrings I had already written once, the test "
            "fixtures (<i>tmp_path</i>, the scripted-input pattern for the "
            "CLI). For the new activity diagrams it gave me a usable Mermaid "
            "skeleton in a single completion; I kept the structure and only "
            "renamed nodes to match the method names already on the class "
            "diagram.",
            body,
        )
    )
    story.append(
        Paragraph(
            "<b>What I changed or rejected.</b> Copilot's first pass at "
            "<i>NoteManager</i> had the orchestrator constructing its own "
            "<i>JsonFileRepository</i> and <i>PrivacyService</i> inside "
            "<i>__init__</i>. That breaks NFR-02 - there is no DI seam, the "
            "tests cannot substitute a fake, and "
            "<i>test_list_notes_skips_undecryptable_private_note</i> could "
            "not even be written. I rewrote the constructor to take all "
            "three collaborators as arguments, which is what the class "
            "diagram aggregation edges have shown since Week 4.1. Copilot "
            "also offered a 'delete note that can't be decrypted' path "
            "inside <i>list_notes</i>; I rejected it because FR-07 says "
            "'exclude with an error logged', not 'delete from disk'. Silent "
            "data loss is the worst possible reading of SPR-02. For the CLI "
            "it suggested adding a 'Search' menu item at the same time as "
            "Slice 2 - I left that out because US-06 (search) is item 7 in "
            "the backlog and adding a UI affordance before the service-layer "
            "search method exists is exactly the kind of half-finished "
            "implementation the Working Agreement warns against.",
            body,
        )
    )
    story.append(
        Paragraph(
            "The actual code that landed, the test list, and the "
            "traceability claims above are mine. Copilot accelerated typing, "
            "not design.",
            body,
        )
    )

    doc.build(story)
    return OUT_PATH


def main() -> None:
    path = build()
    print(f"Wrote {path} ({path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()

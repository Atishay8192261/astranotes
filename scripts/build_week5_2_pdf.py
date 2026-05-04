"""Build the Week 5.2 Requirements-to-UML Traceability Matrix PDF submission.

Run from the project root:
    python scripts/build_week5_2_pdf.py
"""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    NextPageTemplate,
    PageTemplate,
    Paragraph,
    PageBreak,
    Table,
    TableStyle,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = PROJECT_ROOT / "submissions" / "Week5_2_Traceability_Matrix.pdf"


def cell(text: str, font_size: float = 8.5, color: str = "#111111") -> Paragraph:
    style = ParagraphStyle(
        "cell",
        fontName="Helvetica",
        fontSize=font_size,
        leading=font_size + 2,
        textColor=colors.HexColor(color),
    )
    return Paragraph(text, style)


def header_cell(text: str) -> Paragraph:
    style = ParagraphStyle(
        "hdr",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
        textColor=colors.white,
    )
    return Paragraph(text, style)


def build() -> Path:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    portrait_size = LETTER
    landscape_size = landscape(LETTER)

    doc = BaseDocTemplate(
        str(OUT_PATH),
        pagesize=portrait_size,
        leftMargin=0.6 * inch,
        rightMargin=0.6 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
        title="Week 5.2 Requirements-to-UML Traceability Matrix - AstraNotes",
        author="Atishay Jain",
    )

    portrait_frame = Frame(
        0.6 * inch,
        0.6 * inch,
        portrait_size[0] - 1.2 * inch,
        portrait_size[1] - 1.2 * inch,
        id="portrait",
    )
    landscape_frame = Frame(
        0.55 * inch,
        0.55 * inch,
        landscape_size[0] - 1.1 * inch,
        landscape_size[1] - 1.1 * inch,
        id="landscape",
    )
    doc.addPageTemplates(
        [
            PageTemplate(id="P", frames=[portrait_frame], pagesize=portrait_size),
            PageTemplate(id="L", frames=[landscape_frame], pagesize=landscape_size),
        ]
    )

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
        "h3", parent=styles["Heading3"], fontSize=11.5, spaceBefore=10, spaceAfter=4
    )
    body = ParagraphStyle(
        "body", parent=styles["Normal"], fontSize=10.5, leading=14, spaceAfter=8
    )

    story = []

    story.append(Paragraph("CSEN 296B-2 | Week 5.2 Lab Submission", h1))
    story.append(Paragraph("Requirements-to-UML Traceability Matrix for AstraNotes", sub))
    story.append(
        Paragraph(
            "<b>Student Name:</b> Atishay Jain &nbsp;|&nbsp; "
            "<b>Date:</b> May 4, 2026 &nbsp;|&nbsp; "
            "<b>Project:</b> AstraNotes &nbsp;|&nbsp; "
            "<b>Technical Path:</b> Python",
            info,
        )
    )
    story.append(
        Paragraph(
            "I picked the eight highest-risk requirements from "
            "<i>planning/refined-requirements.md</i>: one validation gate "
            "(FR-01), two cross-cutting workflows (FR-04, FR-05), one read-side "
            "feature (FR-07), one architectural rule (NFR-02), the privacy "
            "backbone (SPR-01), error handling (SPR-02), and the dependency "
            "governance rule (SPR-04). NFR-01 and NFR-03 are runtime-performance "
            "assertions and were skipped on purpose; they belong to a Sprint 1 "
            "benchmark harness, not a UML view.",
            body,
        )
    )

    # ---- Matrix on a landscape page ------------------------------------------
    story.append(NextPageTemplate("L"))
    story.append(PageBreak())
    story.append(Paragraph("Traceability Matrix", h2))

    headers = [
        "ID",
        "Requirement",
        "Class / Object Evidence",
        "Use Case / Activity Evidence",
        "Deployment Evidence",
        "Status",
        "Gap Note",
    ]

    rows = [
        [
            "FR-01",
            (
                "Create a note with a non-empty title and an optional body. UUID "
                "and timestamps are auto-assigned. Whitespace-only titles are "
                "rejected."
            ),
            (
                "Class diagram declares <b>Note</b>, "
                "<b>ValidationLayer.validate(note)</b>, and "
                "<b>NoteManager.create_note(...)</b>. Object diagram shows three "
                "Note instances with valid titles and timestamps."
            ),
            (
                "UC1 'Create note (FR-01)'. Activity diagram has the "
                "<b>ValidationLayer.validate</b> decision diamond branching to "
                "'Raise ValidationError - FR-01'."
            ),
            "<b>services/</b> has ValidationLayer and NoteManager; <b>models/</b> has Note.",
            "Fully Traced",
            "None.",
        ],
        [
            "FR-04",
            (
                "Toggle a note's is_private flag. When True, body is encrypted "
                "before write. When toggled back to False, body is re-saved as "
                "plaintext. If decryption fails during toggle, the operation "
                "fails and the note stays encrypted."
            ),
            (
                "Class diagram declares <b>NoteManager.toggle_privacy(note_id)</b> "
                "and <b>PrivacyService.encrypt/decrypt</b>. Object diagram's "
                "note2 shows the encrypted state (body = b'gAAAAAB...')."
            ),
            (
                "UC4 'Toggle note privacy (FR-04, SPR-01)'. The activity "
                "diagram covers the encrypt path of create-private; the "
                "toggle-back-to-plaintext path and the decrypt-failure path "
                "share the same Save and SPR-02 surface steps but are not "
                "drawn as a separate flow."
            ),
            "PrivacyService in services/; Fernet key store in FS.",
            "Partially Traced",
            (
                "All structural pieces are present; missing piece is a "
                "dedicated activity flow for the toggle-back and decrypt-fail "
                "paths. Planned for Sprint 1 prerequisite diagrams."
            ),
        ],
        [
            "FR-05",
            (
                "Persist notes one file per note. On startup, valid files load "
                "and any unreadable file is skipped with an error logged. The "
                "data directory is created on first launch if it does not exist."
            ),
            (
                "Class diagram declares <b>JsonFileRepository(data_dir: Path)</b> "
                "with save/get/list_all/update/delete. Object diagram's Disk "
                "subgraph shows three {uuid}.json files."
            ),
            (
                "UC7 'Persist and restore on startup (FR-05, FR-06, NFR-03)'. "
                "Activity diagram shows JsonFileRepository writing "
                "data_dir/{id}.json plus the OSError-to-PersistenceError "
                "translation."
            ),
            "<b>data/</b> filesystem node tagged FR-05, FR-06; JsonFileRepository in repositories/.",
            "Partially Traced",
            (
                "Class, object, and use case views cover the rule. The "
                "startup-time load loop (with skip-and-log on a bad file and "
                "first-launch directory creation) is not drawn as an activity. "
                "Planned for Sprint 1 prerequisite diagrams."
            ),
        ],
        [
            "FR-07",
            (
                "Keyword search across titles and bodies; case-insensitive, "
                "plain string matching. Successfully decrypted private notes "
                "are included; notes that fail to decrypt are excluded with an "
                "error logged. Empty collection returns an empty list."
            ),
            (
                "Class diagram declares "
                "<b>NoteManager.search_notes(keyword: str) list~Note~</b>. "
                "PrivacyService.decrypt is on the same diagram, so the "
                "decrypt-then-match coupling is structurally available."
            ),
            (
                "UC6 'Search notes by keyword (FR-07)'. No activity diagram "
                "yet for the search workflow itself."
            ),
            "NoteManager and PrivacyService co-located in services/.",
            "Weakly Traced",
            (
                "Method signature and use case are present; the "
                "decrypt-then-match loop and the empty-collection branch need "
                "their own activity diagram. Planned for Sprint 1 prerequisite "
                "diagrams."
            ),
        ],
        [
            "NFR-02",
            (
                "Architecture enforces separation between NoteManager, "
                "NoteRepository / JsonFileRepository, and PrivacyService so "
                "each can be unit-tested independently."
            ),
            (
                "Class diagram shows "
                "<b>NoteRepository &lt;|-- JsonFileRepository</b> realization "
                "and three explicit aggregation edges from NoteManager to "
                "NoteRepository, PrivacyService, and ValidationLayer (the "
                "dependency-injection seam)."
            ),
            "Not directly visible (NFR-02 is structural, not behavioral).",
            (
                "Each layer lives in its own folder (models/, repositories/, "
                "services/, cli/) inside one process."
            ),
            "Fully Traced",
            "None.",
        ],
        [
            "SPR-01",
            (
                "Private bodies encrypted with Fernet before any disk write. "
                "Key is never stored in source code or in the notes directory. "
                "Key management strategy documented in the ADL before Sprint 1."
            ),
            (
                "Class diagram declares "
                "<b>PrivacyService(fernet, encrypt, decrypt, generate_key)</b>. "
                "Object diagram's note2 body is shown as Fernet ciphertext."
            ),
            (
                "UC4 (tagged SPR-01). Activity diagram's <b>Encrypt</b> step "
                "explicitly precedes JsonFileRepository.save when is_private "
                "is true."
            ),
            (
                "Fernet key store node is separate from data/ and labelled "
                "'ADR pending in Sprint 1 - SPR-01' so the open key-storage "
                "decision stays visible."
            ),
            "Fully Traced",
            "None.",
        ],
        [
            "SPR-02",
            (
                "All storage exceptions are caught and translated to "
                "user-level messages. No file paths, stack traces, or internal "
                "state is exposed."
            ),
            (
                "Class diagram declares <b>AstraNotesError</b> parent with "
                "NoteNotFoundError, PersistenceError, ValidationError "
                "subclasses. Explicit ..&gt; raises edges from "
                "JsonFileRepository, PrivacyService, and ValidationLayer."
            ),
            (
                "UC8 'Surface storage errors safely (SPR-02, SPR-03)' with "
                "&lt;&lt;include&gt;&gt; arrows from every write-side use case. "
                "Activity diagram surfaces a user-friendly message on both the "
                "validation failure branch and the persistence failure branch."
            ),
            "Exception module models/exceptions: listed in deployment diagram.",
            "Fully Traced",
            "None.",
        ],
        [
            "SPR-04",
            (
                "Third-party libraries are recorded with pinned version, "
                "purpose comment, and confirmed permissive license (MIT, "
                "Apache 2.0, BSD)."
            ),
            "Not visible in class or object diagram (this is a build-time governance rule).",
            "Not visible in use case or activity diagram.",
            (
                "Deployment diagram's Deps subgraph lists "
                "<b>cryptography 44.0.0</b> (Fernet) and "
                "<b>pytest 8.3.4 dev only</b>, with the SPR-04 tag inline."
            ),
            "Partially Traced",
            (
                "Versions and purpose are visible; license strings are not. "
                "I will add the license label to each Deps node in the "
                "deployment diagram before Sprint 1."
            ),
        ],
    ]

    # Landscape usable width: 11 - 1.1 = 9.9 in
    col_widths = [
        0.45 * inch,  # ID
        1.75 * inch,  # Requirement
        2.05 * inch,  # Class/Object
        2.05 * inch,  # Use Case/Activity
        1.30 * inch,  # Deployment
        0.85 * inch,  # Status
        1.45 * inch,  # Gap Note
    ]

    status_color_map = {
        "Fully Traced": "#1b5e20",
        "Partially Traced": "#bf6c00",
        "Weakly Traced": "#9a0007",
        "Not Traced": "#9a0007",
    }

    data = [[header_cell(h) for h in headers]]
    for row in rows:
        rendered = []
        for col_idx, val in enumerate(row):
            if col_idx == 5:
                color_hex = status_color_map.get(val, "#111111")
                rendered.append(
                    Paragraph(
                        f'<b>{val}</b>',
                        ParagraphStyle(
                            "status",
                            fontName="Helvetica-Bold",
                            fontSize=9,
                            leading=11,
                            textColor=colors.HexColor(color_hex),
                        ),
                    )
                )
            else:
                rendered.append(cell(val, font_size=8.5))
        data.append(rendered)

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
    story.append(table)

    # ---- Back to portrait for the rest ---------------------------------------
    story.append(NextPageTemplate("P"))
    story.append(PageBreak())

    story.append(Paragraph("Traceability Metrics", h2))
    metrics = [
        [header_cell("Metric"), header_cell("Value")],
        [cell("Total requirements reviewed", 10), cell("8", 10)],
        [
            cell("Fully Traced", 10),
            cell("4 (FR-01, NFR-02, SPR-01, SPR-02)", 10),
        ],
        [cell("Partially Traced", 10), cell("3 (FR-04, FR-05, SPR-04)", 10)],
        [cell("Weakly Traced", 10), cell("1 (FR-07)", 10)],
        [cell("Not Traced", 10), cell("0", 10)],
        [
            cell("Major UML elements without a clear requirement reason", 10),
            cell("2", 10),
        ],
    ]
    portrait_w = portrait_size[0] - 1.2 * inch
    metrics_table = Table(metrics, colWidths=[3.5 * inch, portrait_w - 3.5 * inch])
    metrics_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#222222")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
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
    story.append(metrics_table)

    story.append(Paragraph("Orphaned UML elements", h3))
    story.append(
        Paragraph(
            "Two design elements appear in the UML package without a clear "
            "requirement reason behind them:",
            body,
        )
    )
    story.append(
        Paragraph(
            "<b>1. The 'User Workstation - macOS / Linux / Windows, "
            "Python 3.10+' node</b> on the deployment diagram. The "
            "cross-platform OS list and the specific minimum Python version "
            "are not pinned by any FR / NFR / SPR. They are reasonable Python "
            "defaults, but they imply portability coverage I have not "
            "committed to. I will either add a portability NFR or trim the "
            "label to a generic 'Local workstation' before Sprint 1.",
            body,
        )
    )
    story.append(
        Paragraph(
            "<b>2. The <i>generate_key()</i> method on PrivacyService</b>. "
            "It is useful tooling but SPR-01 only requires that the key not "
            "live in source code or the data directory; it does not require "
            "an in-process key-generation API. The Sprint 1 SPR-01 ADR will "
            "either tie this method to a concrete requirement or move it "
            "into a dev-only script.",
            body,
        )
    )

    story.append(PageBreak())
    story.append(Paragraph("Gap Analysis", h2))
    story.append(
        Paragraph(
            "All eight requirements have at least structural and use-case "
            "coverage. The gaps are concentrated in the activity diagrams: "
            "today there is one (create-private), and three more are needed "
            "before Sprint 1 implementation work begins.",
            body,
        )
    )
    story.append(
        Paragraph(
            "<b>1. FR-07 (search) is the largest gap.</b> The search workflow "
            "is the most subtle behavior in the system because it cuts across "
            "encryption, error logging, and an empty-collection short-circuit. "
            "Today it is represented only by a method signature and a use-case "
            "oval. A search activity diagram is needed before "
            "<i>NoteManager.search_notes</i> is written.",
            body,
        )
    )
    story.append(
        Paragraph(
            "<b>2. FR-04 (toggle privacy) needs the toggle-back and "
            "decryption-failure branches drawn.</b> The pieces are all on the "
            "class diagram, but the only activity flow is for create-private. "
            "Drawing the inverse path and the decrypt-failure path will lock "
            "down the failure semantics before code.",
            body,
        )
    )
    story.append(
        Paragraph(
            "<b>3. FR-05 (persistence) needs a startup-flow activity diagram.</b> "
            "Save and OSError translation are covered, but the load loop with "
            "skip-and-log on a bad file and the first-launch directory "
            "creation are only described in prose, not modeled.",
            body,
        )
    )
    story.append(
        Paragraph(
            "A fourth, lower-priority refinement is <b>SPR-04</b>: each "
            "third-party library node on the deployment diagram should carry "
            "its license string (cryptography 44.0.0 - Apache 2.0 / BSD, "
            "pytest 8.3.4 - MIT) so the license-confirmation rule shows up in "
            "UML as well as in pyproject.toml.",
            body,
        )
    )

    story.append(Paragraph("Planned Refinements Before Sprint 1", h2))
    story.append(
        Paragraph(
            "Each Partially / Weakly Traced requirement above has a concrete "
            "plan to close it before Week 6.1 implementation kickoff:",
            body,
        )
    )
    plan_rows = [
        [
            header_cell("Requirement"),
            header_cell("Status today"),
            header_cell("Action before Sprint 1"),
        ],
        [
            cell("FR-04 (toggle privacy)", 9.5),
            cell("Partially Traced", 9.5),
            cell(
                "Extend the create-private activity diagram with the "
                "toggle-back-to-plaintext path and the "
                "decrypt-failure-keeps-encrypted path.",
                9.5,
            ),
        ],
        [
            cell("FR-05 (persistence)", 9.5),
            cell("Partially Traced", 9.5),
            cell(
                "Add a startup-flow activity diagram covering load-loop, "
                "skip-and-log on a bad file, and first-launch directory "
                "creation.",
                9.5,
            ),
        ],
        [
            cell("FR-07 (search)", 9.5),
            cell("Weakly Traced", 9.5),
            cell(
                "Add a search activity diagram showing decrypt-then-match, "
                "skip-and-log on decrypt failure, and empty-collection "
                "short-circuit.",
                9.5,
            ),
        ],
        [
            cell("SPR-04 (deps governance)", 9.5),
            cell("Partially Traced", 9.5),
            cell(
                "Add a license string to each library node in the deployment "
                "diagram (cryptography 44.0.0 - Apache 2.0 / BSD, pytest "
                "8.3.4 - MIT).",
                9.5,
            ),
        ],
    ]
    plan_table = Table(
        plan_rows,
        colWidths=[1.7 * inch, 1.3 * inch, portrait_w - 3.0 * inch],
        repeatRows=1,
    )
    plan_table.setStyle(
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
    story.append(plan_table)

    story.append(PageBreak())
    story.append(Paragraph("How AI Helped Build This Matrix", h2))
    story.append(
        Paragraph(
            "I used AI as a drafting and consistency-checking helper, not as "
            "the source of truth for the status labels.",
            body,
        )
    )
    story.append(
        Paragraph(
            "<b>What AI did.</b> Scaffolded the table from "
            "<i>planning/refined-requirements.md</i> and the requirements "
            "coverage list at the bottom of "
            "<i>docs/uml/design-rationale.md</i>, normalized the requirement "
            "wording to match the refined baseline, and proposed a first-pass "
            "status assignment based on whether each requirement was named in "
            "any single diagram. It also enumerated UML elements as candidates "
            "for the no-clear-requirement-reason list.",
            body,
        )
    )
    story.append(
        Paragraph(
            "<b>What I changed.</b> AI's first pass marked FR-04 and FR-05 as "
            "Fully Traced because each had a use case plus a class-diagram "
            "method. After re-reading the refined baseline I downgraded both "
            "to Partially Traced, since the toggle-back, decrypt-failure, "
            "load-loop, and first-launch-directory behaviors are required by "
            "the requirement wording but not yet drawn as activity flows. "
            "FR-07 went from Partially to Weakly Traced for the same reason - "
            "a method signature is not behavioral evidence for the "
            "algorithmically subtlest feature in the system. Every gap note "
            "was rewritten to name a specific missing artifact and to point "
            "to the planned refinement table.",
            body,
        )
    )
    story.append(
        Paragraph(
            "<b>What I rejected.</b> AI suggested adding NFR-01 and NFR-03 "
            "to the matrix and labelling them Not Traced. I rejected that: "
            "those are runtime-performance assertions, not design "
            "requirements, and the design rationale already documents that "
            "they are deferred to a Sprint 1 benchmark harness. Marking them "
            "Not Traced would inflate the gap count without exposing a real "
            "design problem. AI also suggested treating NoteManager as an "
            "orphan because it is not yet implemented; I rejected that for "
            "the same reason given in the Week 4.2 reflection - the class "
            "diagram describes the target architecture, and NoteManager is "
            "the orchestrator the other views depend on.",
            body,
        )
    )
    story.append(
        Paragraph(
            "The final mapping, status labels, metrics, gap analysis, and "
            "planned-refinement actions are my judgment.",
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

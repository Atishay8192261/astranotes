"""Build the Week 4.2 UML Design Package PDF submission.

Run from the project root:
    python scripts/build_week4_2_pdf.py
"""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    Paragraph,
    PageBreak,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.utils import ImageReader

PROJECT_ROOT = Path(__file__).resolve().parents[1]
UML_DIR = PROJECT_ROOT / "docs" / "uml"
RENDERED_DIR = UML_DIR / "rendered"
OUT_PATH = PROJECT_ROOT / "submissions" / "Week4_2_UML_Design_Package.pdf"


DIAGRAMS = [
    {
        "title": "1. Class Diagram",
        "file": "class-diagram.mmd",
        "image": "class-diagram.png",
        "description": (
            "Structural anchor of the package. Shows every implemented class "
            "(Note, NoteRepository ABC, JsonFileRepository, PrivacyService, "
            "ValidationLayer) plus the planned NoteManager orchestrator, with "
            "method signatures, attributes, the AstraNotesError exception "
            "hierarchy, and the inheritance / aggregation / dependency edges "
            "every other view refers back to."
        ),
    },
    {
        "title": "2. Object Diagram",
        "file": "object-diagram.mmd",
        "image": "object-diagram.png",
        "description": (
            "Concrete runtime snapshot at 2026-04-27T13:42:00Z. One instance of "
            "each service (manager, repo, privacy, validator) and three Note "
            "instances: a public grocery list, a private journal whose body is "
            "shown as Fernet ciphertext (SPR-01 in action), and a tagged class "
            "note. The Disk subgraph shows the corresponding {uuid}.json files "
            "in data_dir, making FR-05 / FR-06 visible in concrete form."
        ),
    },
    {
        "title": "3. Use Case Diagram",
        "file": "use-case-diagram.mmd",
        "image": "use-case-diagram.png",
        "description": (
            "Eight user-visible behaviors inside the AstraNotes system "
            "boundary, each tagged with the requirement IDs that justify it. "
            "The single actor (Solo User) reflects the explicitly single-user "
            "scope. Two cross-cutting use cases (Persist and restore on "
            "startup, Surface storage errors safely) are linked from every "
            "write-side use case via include arrows, expressing SPR-02 at the "
            "use-case level. Mermaid lacks a native UML use-case shape, so "
            "stadium nodes inside a labeled subgraph approximate the standard "
            "ovals-inside-a-boundary notation."
        ),
    },
    {
        "title": "4. Activity Diagram - Create a Private Note",
        "file": "activity-diagram.mmd",
        "image": "activity-diagram.png",
        "description": (
            "The workflow that exercises every layer in one pass: CLI input, "
            "NoteManager.create_note, ValidationLayer.validate (FR-01 gate), "
            "PrivacyService.encrypt when is_private is true (SPR-01 gate), "
            "JsonFileRepository.save, and the OSError-to-PersistenceError "
            "translation step (SPR-02 gate). Every method name and exception "
            "class on this diagram is declared on the class diagram with the "
            "same signature."
        ),
    },
    {
        "title": "5. Deployment Diagram",
        "file": "deployment-diagram.mmd",
        "image": "deployment-diagram.png",
        "description": (
            "Runtime topology: one user workstation (macOS / Linux / Windows, "
            "Python 3.10+), one OS process (python -m astranotes), the "
            "astranotes/ package decomposed into the same cli/, services/, "
            "repositories/, models/ folders that exist in the repo, the "
            "third-party cryptography 44.0.0 library (with license / version "
            "annotation per SPR-04), and the local filesystem holding the "
            "data/ directory and the Fernet key store. The key store carries "
            "an explicit ADR pending in Sprint 1 label so the open SPR-01 "
            "risk stays visible."
        ),
    },
]


AI_REFLECTION = """\
What AI helped generate. The first-pass scaffold for each Mermaid file (class \
diagram syntax, flowchart layout for the use case and activity views, the \
deployment subgraph nesting). Picking flowchart with stadium nodes as the \
closest faithful approximation for a UML use-case view (Mermaid does not \
support that shape natively) was an AI suggestion I accepted. The requirements \
coverage matrix in the rationale was sketched by AI from the requirement IDs \
in CLAUDE.md.

What I refined. I rewrote the class diagram's exception block to use the \
actual AstraNotesError parent class from astranotes/models/exceptions.py rather \
than the flat list AI initially produced. I added the InvalidToken to \
PersistenceError translation edge for PrivacyService because it is in the code \
but the first draft missed it. I expanded the activity diagram's failure \
branches to include the SPR-02 user-friendly message step on both the \
ValidationError and the PersistenceError paths, since the original draft only \
handled the happy path. The object diagram's Disk subgraph (showing the actual \
{uuid}.json files) was added by me to make FR-05 and FR-06 visible in a \
concrete instance, not just declarable in the schema.

What I rejected. AI suggested adding an Administrator actor and an "Export to \
cloud" use case to the use case diagram. Both rejected as scope creep - the \
project is explicitly single-user and local-only per CLAUDE.md. AI suggested \
modeling each note's tags as a separate Tag class with a many-to-many \
relationship to Note. Rejected as over-modeling: the implemented Note \
dataclass stores tags as list[str], and inventing a Tag class in the UML \
would diverge from real code. AI suggested removing NoteManager from the \
class diagram because it is not yet implemented. Rejected: leaving it out \
would force a complete reissue once Sprint 1 lands the orchestrator, and the \
package's job is to describe the target architecture, not just today's code."""


def cell(text: str) -> Paragraph:
    """Wrap a string in a Paragraph so it word-wraps inside table cells."""
    return Paragraph(text, ParagraphStyle("cell", fontName="Helvetica", fontSize=9, leading=11))


def build() -> Path:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(OUT_PATH),
        pagesize=LETTER,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
        title="Week 4.2 UML Design Package - AstraNotes",
        author="Atishay Jain",
    )

    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=16, spaceAfter=4)
    sub = ParagraphStyle("sub", parent=styles["Heading3"], fontSize=11, textColor=colors.grey, spaceAfter=10)
    info = ParagraphStyle("info", parent=styles["Normal"], fontSize=10, leading=14, spaceAfter=10)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=13, spaceBefore=14, spaceAfter=6)
    body = ParagraphStyle("body", parent=styles["Normal"], fontSize=10.5, leading=14, spaceAfter=8)
    code = ParagraphStyle(
        "code",
        parent=styles["Code"],
        fontName="Courier",
        fontSize=8,
        leading=9.5,
        leftIndent=8,
        rightIndent=8,
        textColor=colors.HexColor("#222222"),
        backColor=colors.HexColor("#f4f4f4"),
        borderColor=colors.HexColor("#cccccc"),
        borderWidth=0.5,
        borderPadding=6,
    )

    story = []

    story.append(Paragraph("CSEN 296B-2 | Week 4.2 Lab Submission", h1))
    story.append(Paragraph("Complete UML Design Package for AstraNotes", sub))
    story.append(
        Paragraph(
            "<b>Student Name:</b> Atishay Jain &nbsp;|&nbsp; "
            "<b>Date:</b> April 27, 2026 &nbsp;|&nbsp; "
            "<b>Project:</b> AstraNotes &nbsp;|&nbsp; "
            "<b>Technical Path:</b> Python",
            info,
        )
    )

    story.append(Paragraph("Overview", h2))
    story.append(
        Paragraph(
            "This package contains five UML views of AstraNotes (class, object, "
            "use case, activity, deployment), a written rationale tying them "
            "together with explicit references to the FR / NFR / SPR IDs from "
            "the refined requirement baseline, and an AI reflection covering "
            "what the model generated, what I refined, and what I rejected. "
            "Every diagram reflects the implemented architecture in the "
            "astranotes/ package: Note, NoteRepository (ABC) with "
            "JsonFileRepository, PrivacyService, ValidationLayer, the planned "
            "NoteManager orchestrator, and the AstraNotesError family of "
            "domain exceptions.",
            body,
        )
    )

    story.append(Paragraph("Diagram Inventory", h2))
    inventory = [
        ["#", "View", "Source file"],
        ["1", "Class diagram", "docs/uml/class-diagram.mmd"],
        ["2", "Object diagram (runtime snapshot)", "docs/uml/object-diagram.mmd"],
        ["3", "Use case diagram", "docs/uml/use-case-diagram.mmd"],
        ["4", "Activity diagram - Create a private note", "docs/uml/activity-diagram.mmd"],
        ["5", "Deployment diagram", "docs/uml/deployment-diagram.mmd"],
    ]
    table = Table(inventory, colWidths=[0.4 * inch, 3.0 * inch, 3.5 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#222222")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9.5),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7f7f7")]),
            ]
        )
    )
    story.append(table)

    # Available width on page after margins (LETTER is 8.5 in wide).
    page_width = LETTER[0] - 1.4 * inch
    max_image_height = LETTER[1] - 3.0 * inch

    for diagram in DIAGRAMS:
        story.append(PageBreak())
        story.append(Paragraph(diagram["title"], h2))
        story.append(Paragraph(diagram["description"], body))
        story.append(Spacer(1, 6))

        image_path = RENDERED_DIR / diagram["image"]
        reader = ImageReader(str(image_path))
        iw, ih = reader.getSize()
        ratio = ih / iw
        target_w = page_width
        target_h = target_w * ratio
        if target_h > max_image_height:
            target_h = max_image_height
            target_w = target_h / ratio
        img = Image(str(image_path), width=target_w, height=target_h)
        img.hAlign = "CENTER"
        story.append(img)
        story.append(Spacer(1, 4))
        story.append(
            Paragraph(
                f"<i>Rendered from docs/uml/{diagram['file']} via mermaid-cli. "
                f"Source listing in Appendix A.</i>",
                body,
            )
        )

    story.append(PageBreak())
    story.append(Paragraph("Design Rationale", h2))
    rationale = (UML_DIR / "design-rationale.md").read_text(encoding="utf-8")
    for block in render_markdown(rationale, body, code):
        story.append(block)

    story.append(PageBreak())
    story.append(Paragraph("AI Reflection", h2))
    for paragraph in AI_REFLECTION.split("\n\n"):
        story.append(Paragraph(paragraph.replace("\n", " "), body))

    story.append(PageBreak())
    story.append(Paragraph("Appendix A - Mermaid Source", h2))
    story.append(
        Paragraph(
            "Each diagram above was rendered from the corresponding .mmd file "
            "below using @mermaid-js/mermaid-cli. The source is included so a "
            "reviewer can re-render or edit any view without losing fidelity.",
            body,
        )
    )
    for diagram in DIAGRAMS:
        story.append(Spacer(1, 8))
        story.append(Paragraph(f"<b>docs/uml/{diagram['file']}</b>", body))
        source = (UML_DIR / diagram["file"]).read_text(encoding="utf-8")
        story.append(Preformatted(source, code))

    doc.build(story)
    return OUT_PATH


def render_markdown(md_text: str, body_style: ParagraphStyle, code_style: ParagraphStyle):
    """Tiny markdown subset renderer: headings, paragraphs, tables, lists.

    The rationale uses only these constructs, so a full parser is overkill.
    """
    blocks = []
    lines = md_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith("# "):
            blocks.append(Paragraph(escape(line[2:].strip()), ParagraphStyle("md_h1", parent=body_style, fontSize=14, leading=18, spaceAfter=8, fontName="Helvetica-Bold")))
            i += 1
            continue
        if line.startswith("## "):
            blocks.append(Paragraph(escape(line[3:].strip()), ParagraphStyle("md_h2", parent=body_style, fontSize=12, leading=15, spaceAfter=6, spaceBefore=10, fontName="Helvetica-Bold")))
            i += 1
            continue
        if line.startswith("### "):
            blocks.append(Paragraph(escape(line[4:].strip()), ParagraphStyle("md_h3", parent=body_style, fontSize=11, leading=14, spaceAfter=4, spaceBefore=8, fontName="Helvetica-Bold")))
            i += 1
            continue
        if line.startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].startswith("|"):
                table_lines.append(lines[i])
                i += 1
            blocks.append(_render_md_table(table_lines))
            continue
        if line.lstrip().startswith("- "):
            items = []
            while i < len(lines) and lines[i].lstrip().startswith("- "):
                items.append(lines[i].lstrip()[2:].strip())
                i += 1
            for item in items:
                blocks.append(Paragraph("&bull;&nbsp; " + inline_md(item), ParagraphStyle("md_li", parent=body_style, leftIndent=10, spaceAfter=2)))
            continue
        # Paragraph: collect contiguous non-empty, non-special lines.
        para_lines = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].startswith(("#", "|", "-")):
            para_lines.append(lines[i])
            i += 1
        blocks.append(Paragraph(inline_md(" ".join(para_lines)), body_style))
    return blocks


def _render_md_table(table_lines):
    rows = []
    for raw in table_lines:
        cells_raw = [c.strip() for c in raw.strip().strip("|").split("|")]
        rows.append(cells_raw)
    if len(rows) >= 2 and set("".join(rows[1])).issubset(set("-: ")):
        header = rows[0]
        body_rows = rows[2:]
    else:
        header = rows[0]
        body_rows = rows[1:]

    data = [[cell(inline_md(c)) for c in header]]
    for r in body_rows:
        data.append([cell(inline_md(c)) for c in r])

    col_count = len(header)
    width = (LETTER[0] - 1.4 * inch) / col_count
    table = Table(data, colWidths=[width] * col_count, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#222222")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7f7f7")]),
            ]
        )
    )
    return table


def escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def inline_md(text: str) -> str:
    """Apply minimal inline markdown: bold (**...**), italics (*...*), and code (`...`)."""
    out = escape(text)
    # Bold
    while "**" in out:
        first = out.find("**")
        second = out.find("**", first + 2)
        if second == -1:
            break
        out = out[:first] + "<b>" + out[first + 2 : second] + "</b>" + out[second + 2 :]
    # Code spans
    while "`" in out:
        first = out.find("`")
        second = out.find("`", first + 1)
        if second == -1:
            break
        out = (
            out[:first]
            + '<font face="Courier" size="9">'
            + out[first + 1 : second]
            + "</font>"
            + out[second + 1 :]
        )
    return out


def main() -> None:
    path = build()
    print(f"Wrote {path} ({path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()

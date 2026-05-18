"""Build the Week 7.2 Testing Strategy and First Test Set PDF.

Run from the project root:
    python scripts/build_week7_2_pdf.py
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
    Table,
    TableStyle,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = PROJECT_ROOT / "submissions" / "Week7_2_Testing_Strategy.pdf"


def cell(text: str, font_size: float = 9.0, color: str = "#111111") -> Paragraph:
    style = ParagraphStyle(
        "cell",
        fontName="Helvetica",
        fontSize=font_size,
        leading=font_size + 2.5,
        textColor=colors.HexColor(color),
    )
    return Paragraph(text, style)


def mono(text: str, font_size: float = 8.5) -> Paragraph:
    style = ParagraphStyle(
        "mono",
        fontName="Courier",
        fontSize=font_size,
        leading=font_size + 2.5,
        textColor=colors.HexColor("#1a1a1a"),
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
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
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
        title="Week 7.2 Testing Strategy and First Test Set - AstraNotes",
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
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=13, spaceBefore=10, spaceAfter=6)
    h3 = ParagraphStyle("h3", parent=styles["Heading3"], fontSize=11.5, spaceBefore=8, spaceAfter=4)
    body = ParagraphStyle("body", parent=styles["Normal"], fontSize=10.5, leading=14, spaceAfter=8)

    page_w = page_size[0] - 1.3 * inch
    story = []

    # ---- Cover ----
    story.append(Paragraph("CSEN 296B-2 | Week 7.2 Lab Submission", h1))
    story.append(Paragraph("AstraNotes Testing Strategy and First Test Set", sub))
    story.append(
        Paragraph(
            "<b>Student Name:</b> Atishay Jain &nbsp;|&nbsp; "
            "<b>Date:</b> May 17, 2026 &nbsp;|&nbsp; "
            "<b>Project:</b> AstraNotes &nbsp;|&nbsp; "
            "<b>Technical Path:</b> Python",
            info,
        )
    )

    # ---- Strategy ----
    story.append(Paragraph("Testing Strategy", h2))
    story.append(
        Paragraph(
            "AstraNotes is a 3-tier app: a thin presentation tier, a logic "
            "tier (<i>NoteManager</i>, <i>ValidationLayer</i>, "
            "<i>PrivacyService</i>), and a data tier "
            "(<i>JsonFileRepository</i>). My testing money goes where the "
            "risk is, and the risk is not in the presentation tier - it is "
            "in the two places where a bug is silent and expensive: a note "
            "that fails to persist, and a private note whose body leaks to "
            "disk in plaintext. So the strategy is <b>test the logic and "
            "data tiers hard and first, test the presentation tier only at "
            "the seam, and do not chase coverage where a failure would be "
            "loud and obvious anyway.</b>",
            body,
        )
    )
    for n, line in enumerate(
        [
            "<b>Trace before you test.</b> Every test names the requirement "
            "or user story it defends. An untraceable test is noise and gets "
            "cut - the same Working Agreement rule that governs feature work.",
            "<b>Test behavior at the right level.</b> A title rule is a unit "
            "concern. 'A private note is unreadable on disk' is an "
            "integration concern. 'Create a note then see it listed' is a "
            "feature concern.",
            "<b>Realistic first choices.</b> I am not testing everything in "
            "week one. Performance (NFR-01/03), the GUI widget tree, search "
            "(US-06, not built yet), and FR-08 sort edge cases are "
            "deliberately out of the first set, with reasons given at the end.",
        ],
        start=1,
    ):
        story.append(Paragraph(f"<b>{n}.</b> {line}", body))

    # ---- Two features ----
    story.append(Paragraph("Two Features Tested First", h2))
    story.append(
        Paragraph(
            "I picked the two features whose failure modes are the most "
            "damaging and the least visible.",
            body,
        )
    )
    story.append(Paragraph("Feature A - Create a note (US-01; FR-01, FR-06, SPR-02)", h3))
    story.append(
        Paragraph(
            "Creating a note is the entry point for every other story; if "
            "create is wrong, everything downstream is built on sand. The "
            "subtle part is the validation gate: a whitespace-only title "
            "must be rejected <i>before</i> anything touches disk, and the "
            "rejection must be a domain error, not a raw traceback.",
            body,
        )
    )
    story.append(
        Paragraph("Feature B - Private note encrypted at rest (US-04; FR-04, SPR-01, SPR-02)", h3)
    )
    story.append(
        Paragraph(
            "This is the highest-risk behavior in the whole system. If it "
            "silently fails, a user's private note is written to disk in "
            "plaintext and nobody notices until it is too late. It is also "
            "the one behavior that <i>only</i> exists when three components "
            "are wired together (manager - privacy - repository), so it "
            "cannot be proven by any single unit test.",
            body,
        )
    )

    # ---- First test set ----
    story.append(PageBreak())
    story.append(Paragraph("First Test Set", h2))
    story.append(
        Paragraph(
            "These are real tests in the suite today (34 passing), grouped "
            "by the level each one belongs to. I present the actual set "
            "rather than an outline because the code exists and the set is "
            "small and focused on purpose.",
            body,
        )
    )

    story.append(Paragraph("Feature A - Create a note", h3))
    fa_rows = [
        [header_cell("Level"), header_cell("Test"), header_cell("What it pins"), header_cell("Traces to")],
        [cell("Unit"), mono("test_valid_title_passes"), cell("Non-empty title passes the gate"), cell("FR-01")],
        [cell("Unit"), mono("test_empty_title_raises"), cell("Empty title to ValidationError"), cell("FR-01, SPR-02")],
        [cell("Unit"), mono("test_whitespace_only_<br/>title_raises"), cell("Whitespace title stripped then rejected"), cell("FR-01")],
        [cell("Unit"), mono("test_note_timestamps_<br/>default_to_utc_now"), cell("created_at/modified_at UTC-aware on construction"), cell("FR-06")],
        [cell("Unit"), mono("test_note_ids_are_unique"), cell("Each note gets a distinct UUID"), cell("FR-01")],
        [cell("Integration"), mono("test_create_note_<br/>persists_plaintext_body"), cell("create_note validates then writes one {uuid}.json"), cell("FR-01, FR-05")],
        [cell("Integration"), mono("test_create_note_<br/>rejects_whitespace_title"), cell("Gate fires through the manager, nothing written"), cell("FR-01, SPR-02")],
        [cell("Feature"), mono("test_create_then_<br/>list_round_trip"), cell("Created note is visible via the user-facing entry point"), cell("US-01")],
        [cell("Feature"), mono("test_create_<br/>rejects_empty_title"), cell("User sees a friendly message, not a stack trace"), cell("US-01, SPR-02")],
    ]
    story.append(
        styled_table(fa_rows, [0.85 * inch, 1.85 * inch, page_w - 4.05 * inch, 1.35 * inch])
    )

    story.append(Paragraph("Feature B - Private note encrypted at rest", h3))
    fb_rows = [
        [header_cell("Level"), header_cell("Test"), header_cell("What it pins"), header_cell("Traces to")],
        [cell("Unit"), mono("test_encrypt_decrypt_<br/>round_trip"), cell("Ciphertext is bytes, differs from plaintext, decrypts back"), cell("SPR-01")],
        [cell("Unit"), mono("test_decrypt_with_wrong_<br/>key_raises_persistence_error"), cell("Wrong key fails loud, never returns garbled text"), cell("FR-04, SPR-02")],
        [cell("Integration"), mono("test_create_private_note_<br/>encrypts_body_on_disk"), cell("On-disk JSON has NO plaintext body; base64 ciphertext"), cell("SPR-01")],
        [cell("Integration"), mono("test_list_notes_<br/>decrypts_private_bodies"), cell("Private note transparently readable on read-back"), cell("US-04, FR-04")],
        [cell("Integration"), mono("test_list_notes_skips_<br/>undecryptable_private_note"), cell("Undecryptable note excluded + logged, not crashed/leaked"), cell("FR-07, SPR-02")],
        [cell("Integration"), mono("test_create_private_<br/>without_privacy_service_raises"), cell("No key configured to refuse, never silent plaintext"), cell("SPR-01")],
    ]
    story.append(
        styled_table(fb_rows, [0.85 * inch, 1.95 * inch, page_w - 4.05 * inch, 1.25 * inch])
    )
    story.append(
        Paragraph(
            "The single most important test in this document is "
            "<i>test_create_private_note_encrypts_body_on_disk</i>. It "
            "asserts the literal <b>absence</b> of the plaintext string in "
            "the file on disk. That one assertion is the difference between "
            "'we believe it is encrypted' and 'we proved it is.'",
            body,
        )
    )

    # ---- Levels ----
    story.append(PageBreak())
    story.append(Paragraph("Test Levels - What Goes Where and Why", h2))
    story.append(
        Paragraph(
            "<b>Unit</b> (test_note, test_validation, test_privacy): one "
            "component, no I/O wiring. Validation rules and Fernet "
            "round-trips are pure logic - provable in milliseconds without "
            "a filesystem. These are the bulk of the suite because they are "
            "the cheapest place to catch a regression.",
            body,
        )
    )
    story.append(
        Paragraph(
            "<b>Integration</b> (test_repository, test_note_manager): two or "
            "more tiers wired through the real dependency-injection seam, "
            "writing to a <i>tmp_path</i> directory. 'Encrypted on disk' and "
            "'skip undecryptable note' only have meaning once the manager, "
            "privacy service, and file repository are connected, so they "
            "cannot be unit tests by definition.",
            body,
        )
    )
    story.append(
        Paragraph(
            "<b>Feature-level</b> (test_cli, and the GUI controller test as "
            "the presentation tier lands): drives the app through its "
            "user-facing entry point with scripted input and a captured "
            "output buffer. It does not re-test encryption internals - it "
            "asserts the user-visible outcome. Intentionally thin because "
            "the presentation tier is intentionally thin.",
            body,
        )
    )
    story.append(
        Paragraph(
            "I deliberately do <b>not</b> mock the filesystem in the "
            "integration tests. <i>tmp_path</i> gives a real directory "
            "destroyed after the test, faithful to production and still "
            "satisfying SPR-03 ('tests run without external dependencies'). "
            "A mocked filesystem would let a test pass while the real "
            "<i>json.dumps</i> / <i>Path.write_text</i> path is broken - "
            "exactly the false green this feature cannot afford.",
            body,
        )
    )

    # ---- Timing ----
    story.append(Paragraph("When These Tests Run During Development", h2))
    timing_rows = [
        [header_cell("Test level"), header_cell("When it runs"), header_cell("Why then")],
        [
            cell("Unit"),
            cell("On every save / before every commit (TDD inner loop)"),
            cell("Sub-second feedback; this is where you live while writing logic."),
        ],
        [
            cell("Integration"),
            cell("Before committing a slice, and in CI on every push"),
            cell("Slower (touches disk); run when a slice is done to prove the tiers still talk."),
        ],
        [
            cell("Feature-level"),
            cell("Before a user story is marked Done, and at each milestone gate"),
            cell("Slowest and broadest; the Definition-of-Done check, not the inner loop."),
        ],
    ]
    story.append(styled_table(timing_rows, [1.2 * inch, 2.4 * inch, page_w - 3.6 * inch]))
    story.append(
        Paragraph(
            "The shift-left point: the create-private security test is an "
            "<i>integration</i> test, but it runs in CI on every single "
            "push, not just at milestones. A security regression is the one "
            "thing I never want to discover late, so I move that specific "
            "test as far left as it will go.",
            body,
        )
    )

    story.append(Paragraph("What I Deliberately Did NOT Test First", h2))
    for line in [
        "<b>NFR-01 / NFR-03 (performance):</b> runtime assertions, not "
        "behavior. They belong in a Sprint 1 benchmark harness; testing "
        "them now would be guessing.",
        "<b>GUI widget rendering:</b> the presentation tier is thin by "
        "design and a broken button is loud and immediately visible. "
        "Pixel/widget tests are brittle and low-value this early; I test "
        "the controller seam instead.",
        "<b>Search (US-06):</b> not implemented yet. Writing tests for "
        "unwritten code is theater.",
        "<b>FR-08 sort beyond the created_at tiebreaker:</b> basic "
        "ordering is covered; exhaustive ordering edge cases are not "
        "first-week risk.",
    ]:
        story.append(Paragraph(f"&bull; {line}", body))

    # ---- AI Reflection ----
    story.append(PageBreak())
    story.append(Paragraph("AI Reflection", h2))
    story.append(
        Paragraph(
            "<b>How AI helped.</b> I used GitHub Copilot to brainstorm "
            "candidate cases for both features and to critique my draft set "
            "for gaps. Its most useful single suggestion was the negative "
            "security assertion - checking that the plaintext string is "
            "<i>absent</i> from the file, not just that some ciphertext is "
            "present. My first draft of "
            "<i>test_create_private_note_encrypts_body_on_disk</i> only "
            "asserted the body looked encrypted; the stronger 'plaintext "
            "must not appear anywhere in the file' assertion came from an AI "
            "critique and is now the most important line in the suite. It "
            "also flagged that I had no test for the no-key-configured path, "
            "which became "
            "<i>test_create_private_without_privacy_service_raises</i>.",
            body,
        )
    )
    story.append(
        Paragraph(
            "<b>What I kept.</b> The absent-plaintext assertion, the missing "
            "no-key case, and a suggestion to parametrize the "
            "whitespace-title inputs instead of writing three near-duplicate "
            "tests.",
            body,
        )
    )
    story.append(
        Paragraph(
            "<b>What I changed.</b> AI proposed one large end-to-end test "
            "that created a private note, listed it, edited it, and deleted "
            "it in a single function. I split it back into focused tests - a "
            "failure in a four-step test does not tell you which step broke, "
            "and edit/delete are different user stories (US-02, US-03) that "
            "should not be smuggled into the create/private first set.",
            body,
        )
    )
    story.append(
        Paragraph(
            "<b>What I rejected.</b> AI suggested a test asserting duplicate "
            "tags are rejected. CLAUDE.md explicitly records duplicate tags "
            "as an <i>accepted</i> known limitation (they preserve user "
            "intent), so that test would encode the wrong behavior and fail "
            "a correct implementation. I also rejected mocking "
            "<i>Path.write_text</i> in the repository tests - that would "
            "produce a false green if the real serialization path "
            "regressed, unacceptable for the persistence and privacy "
            "features specifically. Keeping <i>tmp_path</i> over a mock is "
            "my call and the single most consequential testing judgment "
            "here.",
            body,
        )
    )
    story.append(
        Paragraph(
            "The level assignments, the timing table, the out-of-scope "
            "list, and every keep/change/reject decision are my judgment. "
            "Copilot widened the candidate list; it did not decide what was "
            "worth testing.",
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

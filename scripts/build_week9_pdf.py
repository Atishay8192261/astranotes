"""Build the Week 9 Test Improvement Log PDF.

Run from the project root:
    python scripts/build_week9_pdf.py
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
    Spacer,
    Table,
    TableStyle,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = PROJECT_ROOT / "submissions" / "Week9_Test_Improvement_Log.pdf"


def cell(text: str, font_size: float = 9.0, color: str = "#111111") -> Paragraph:
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


def code_block(text: str) -> Preformatted:
    style = ParagraphStyle(
        "code",
        fontName="Courier",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#1a1a1a"),
        backColor=colors.HexColor("#f3f3f3"),
        borderColor=colors.HexColor("#dddddd"),
        borderWidth=0.5,
        borderPadding=6,
        leftIndent=2,
        rightIndent=2,
    )
    return Preformatted(text, style)


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
        title="Week 9 Test Improvement Log - AstraNotes",
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
    sub = ParagraphStyle("sub", parent=styles["Heading3"], fontSize=11, textColor=colors.grey, spaceAfter=10)
    info = ParagraphStyle("info", parent=styles["Normal"], fontSize=10, leading=14, spaceAfter=12)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=13, spaceBefore=10, spaceAfter=6)
    body = ParagraphStyle("body", parent=styles["Normal"], fontSize=10.5, leading=14, spaceAfter=8)

    page_w = page_size[0] - 1.3 * inch
    story = []

    # ---- Cover ----
    story.append(Paragraph("CSEN 296B-2 | Week 9 Lab Submission", h1))
    story.append(Paragraph("AstraNotes Test Improvement Log", sub))
    story.append(
        Paragraph(
            "<b>Student Name:</b> Atishay Jain &nbsp;|&nbsp; "
            "<b>Date:</b> May 30, 2026 &nbsp;|&nbsp; "
            "<b>Project:</b> AstraNotes &nbsp;|&nbsp; "
            "<b>Technical Path:</b> Python<br/>"
            "<b>Repository:</b> github.com/Atishay8192261/astranotes (private) &nbsp;|&nbsp; "
            "<b>Pull Request:</b> #2 (merged) &nbsp;|&nbsp; "
            "<b>Suite after this lab:</b> 70 passed, 5 skipped (legacy CLI quarantined)",
            info,
        )
    )

    # ---- Feature reviewed ----
    story.append(Paragraph("Feature / requirement reviewed", h2))
    story.append(
        Paragraph(
            "<b>SPR-01</b> (private note bodies encrypted with Fernet before "
            "any disk write) as enforced by "
            "<i>test_create_private_note_encrypts_body_on_disk</i> in "
            "<i>tests/test_note_manager.py</i>. This is the single "
            "load-bearing test for the project's most security-critical "
            "requirement: a note marked <i>is_private=True</i> never lands "
            "plaintext on disk. The test has existed since Sprint Zero and "
            "has shipped through every milestone.",
            body,
        )
    )
    story.append(
        Paragraph(
            "I picked it because SPR-01 is the requirement my grade and my "
            "user's privacy both ride on. If any test in the suite deserves "
            "to be strong, it is this one.",
            body,
        )
    )

    # ---- Weakness ----
    story.append(Paragraph("The weakness — a brittle assertion masquerading as a security check", h2))
    story.append(Paragraph("The original test was five lines:", body))
    story.append(code_block(
        'def test_create_private_note_encrypts_body_on_disk(manager, tmp_path):\n'
        '    manager.create_note(title="secret", body="meet at 5", is_private=True)\n'
        '    raw = list(tmp_path.glob("*.json"))[0].read_text()\n'
        '    assert "meet at 5" not in raw\n'
        '    assert \'"body_encoding": "base64"\' in raw'
    ))
    story.append(
        Paragraph(
            "Two assertions, both phrased as questions about the "
            "<i>implementation</i> rather than the <i>property</i>:",
            body,
        )
    )
    for line in [
        "<b>(1)</b> <i>assert \"meet at 5\" not in raw</i> is the right idea, "
        "but pinning a single short phrase gives false confidence. <i>\"5\"</i> "
        "could appear in an ISO timestamp; <i>\"meet\"</i> could be a tag. "
        "The test would also miss a regression that leaks a <i>different</i> "
        "substring of the plaintext while suppressing the exact phrase. The "
        "assertion fits the literal SPR-01 sentence but does not probe its spirit.",
        "<b>(2)</b> <i>assert '\"body_encoding\": \"base64\"' in raw</i> is "
        "the bigger problem: it pins a <i>private serialization detail</i>. "
        "If we evolved the storage format - added a <i>\"v\": 2</i> envelope, "
        "switched encoding to hex, wrapped the ciphertext in a per-note salt - "
        "this assertion would break <b>even though SPR-01 still held</b>. "
        "Conversely, if a regression switched private bodies to a "
        "plaintext-with-<i>body_encoding=base64</i>-wrapper (base64-encoded "
        "the cleartext), the assertion would still pass. It is testing the "
        "<i>shape</i> of the right answer, not the <i>answer</i>.",
    ]:
        story.append(Paragraph(f"&bull; {line}", body))
    story.append(
        Paragraph(
            "This is the canonical 'misleading coverage confidence' failure "
            "mode from the rubric.",
            body,
        )
    )

    # ---- Improvement ----
    story.append(PageBreak())
    story.append(Paragraph("The improvement", h2))
    story.append(Paragraph("Rewritten to assert the property directly:", body))
    story.append(code_block(
        'def test_create_private_note_encrypts_body_on_disk(manager, tmp_path):\n'
        '    """Gap #4 fix: assert the SPR-01 property, not the format."""\n'
        '    import json\n'
        '    plaintext = "meet rendezvous coordinates xyz123"\n'
        '    manager.create_note(title="secret", body=plaintext, is_private=True)\n'
        '    payload = json.loads(list(tmp_path.glob("*.json"))[0].read_text())\n'
        '\n'
        '    # 1) Plaintext never appears in the on-disk body field, AND no\n'
        '    #    token of the plaintext appears either - so a leak of any\n'
        '    #    substring longer than a single word is caught.\n'
        '    assert plaintext not in payload["body"]\n'
        '    for word in plaintext.split():\n'
        '        assert word not in payload["body"], (\n'
        '            f"plaintext token \'{word}\' leaked to disk")\n'
        '\n'
        '    # 2) The body still decrypts back to the original under the\n'
        '    #    same key. If a regression "encrypts" by base64-ing\n'
        '    #    cleartext, step 1 catches it; if it scrambles into\n'
        '    #    something undecryptable, step 2 catches it.\n'
        '    notes = manager.list_notes()\n'
        '    assert [n.body for n in notes] == [plaintext]'
    ))
    story.append(
        Paragraph(
            "Three things change. <b>First</b>, the assertion targets the "
            "JSON <i>body</i> field specifically (<i>payload[\"body\"]</i>) "
            "instead of the whole file text - this is what lets the per-word "
            "check work without false positives from <i>created_at</i> "
            "containing the substring <i>\"at\"</i> (a real failure I hit "
            "while writing the test, see AI section below). <b>Second</b>, "
            "the per-word loop makes the leak detection robust to any "
            "substring leak longer than a single token. <b>Third</b>, the "
            "test asserts the <i>round-trip</i> - that the ciphertext "
            "decrypts back to the original - which is the only assertion "
            "that catches a regression that encodes cleartext rather than "
            "encrypting it.",
            body,
        )
    )
    story.append(
        Paragraph(
            "The new test is decoupled from the storage envelope format: "
            "changing <i>body_encoding</i> from <i>base64</i> to <i>hex</i>, "
            "or wrapping the payload in a versioned envelope, would not "
            "break this test. A real SPR-01 regression would.",
            body,
        )
    )

    # ---- Mocking ----
    story.append(Paragraph("Mocking — helping or hiding risk?", h2))
    story.append(
        Paragraph(
            "This codebase's discipline around mocking is one of the things "
            "I deliberately did not change. The fixture for this test uses "
            "a <b>real</b> <i>JsonFileRepository</i>, a <b>real</b> "
            "<i>PrivacyService</i> (with <i>PrivacyService.generate_key()</i> "
            "for the test key), and a <i>tmp_path</i> from pytest. There "
            "are no mocks anywhere in the privacy or persistence layers, "
            "by convention since Week 7.2.",
            body,
        )
    )
    story.append(
        Paragraph(
            "The pattern is right. SPR-01 is a property about what hits the "
            "disk; a test of it that mocks the disk is testing the wrong "
            "thing. The one place I had to be careful was the temptation - "
            "when I added a 'decryption fails during toggle' test in this "
            "same PR - to monkeypatch <i>PrivacyService.decrypt</i> to "
            "raise. I resisted that and used two distinct "
            "<i>PrivacyService</i> instances with different keys, "
            "mirroring the existing pattern. A <i>decrypt</i> that raises "
            "because the wrong key was used is a different code path than "
            "a <i>decrypt</i> that raises because I told it to. The "
            "real-key approach exercises Fernet's actual <i>InvalidToken</i> "
            "flow.",
            body,
        )
    )
    story.append(
        Paragraph(
            "The single place mocking <i>did</i> help this PR was in the "
            "new repository tests for filesystem failures. There I "
            "monkeypatched <i>pathlib.Path.write_text</i> to raise "
            "<i>OSError(\"disk full\")</i>. This is mocking at the "
            "<b>boundary</b> where the real failure surfaces a real branch "
            "in the code under test (the <i>except OSError:</i> clause that "
            "translates to <i>PersistenceError</i>). That branch was 100% "
            "uncovered before; nothing short of mocking would have reached "
            "it without an actually-failing disk. Mocking at the <b>OS "
            "boundary</b> to exercise an internal error-translation branch "
            "is helping; mocking the <b>service under test</b> to make it "
            "raise on cue would have been hiding.",
            body,
        )
    )

    # ---- Coverage gap ----
    story.append(PageBreak())
    story.append(Paragraph("A meaningful coverage gap that still matters", h2))
    story.append(
        Paragraph(
            "The improved test proves that the <i>first</i> write of a "
            "private note never leaks plaintext, and that a fresh "
            "<i>list_notes()</i> round-trips. What it does <b>not</b> prove "
            "is that the <i>whole lifecycle</i> of a private note preserves "
            "the property - specifically, that an <b>edit</b> to a private "
            "note also re-encrypts on every save, that a "
            "<i>set_private(False)</i> toggle correctly <i>replaces</i> the "
            "ciphertext with plaintext (not appends), and that a second "
            "update doesn't accidentally double-encrypt the body.",
            body,
        )
    )
    story.append(
        Paragraph(
            "I added partial coverage for the edit and toggle paths in the "
            "same PR (<i>test_update_preserves_encryption_for_private_note</i>, "
            "<i>test_set_private_true_encrypts_body_on_disk</i>, "
            "<i>test_set_private_false_decrypts_and_writes_plaintext</i>), "
            "but none of those check the <i>file content after multiple "
            "edits</i>. A user who creates a private note, edits it once, "
            "then edits it again is exercising a path the suite still "
            "asserts only at the in-memory API level. The next test I would "
            "add - and the reason I am calling this out instead of slipping "
            "it in silently - is "
            "<i>test_repeated_edits_keep_private_body_encrypted_on_disk</i> "
            "that creates, updates, updates again, and re-reads the raw "
            "JSON each time to confirm the body field is never plaintext.",
            body,
        )
    )
    story.append(
        Paragraph(
            "The coverage gap that does <i>not</i> matter and that I am "
            "deliberately not chasing: testing for plaintext leakage in "
            "OS-level metadata (swap files, journaled filesystems, FUSE "
            "caches). That is an OS-layer threat model that ADR-005's "
            "threat model explicitly excludes, and writing tests for it "
            "would be theater.",
            body,
        )
    )

    # ---- AI ----
    story.append(Paragraph("How AI helped, and what I accepted / changed / rejected", h2))
    story.append(
        Paragraph(
            "<b>Accepted.</b> Claude proposed the per-word loop "
            "(<i>for word in plaintext.split()</i>) as the way to broaden "
            "the leak check beyond a single-phrase substring. That is the "
            "structural improvement that makes the new test stronger than "
            "the old one, and I would not have written it on the first try.",
            body,
        )
    )
    story.append(
        Paragraph(
            "<b>Changed.</b> Claude's first draft tried to assert against "
            "the entire raw file text - exactly the trap I was trying to "
            "escape. The test failed when the plaintext token <i>\"at\"</i> "
            "matched the substring <i>\"created_at\"</i> in the timestamp "
            "field. The fix - <i>json.loads</i> the payload and assert "
            "against <i>payload[\"body\"]</i> instead of the whole string - "
            "is mine; the failure made the bug obvious in a way reading "
            "the code didn't. The AI's draft had the right idea but the "
            "wrong target.",
            body,
        )
    )
    story.append(
        Paragraph(
            "<b>Rejected.</b> Claude also suggested adding a <i>fuzz</i> "
            "test that generated 100 random plaintexts and asserted the "
            "property holds across all of them. I declined. The property "
            "is structural - Fernet either encrypts or it doesn't - so 100 "
            "random inputs prove nothing that 1 well-chosen input doesn't, "
            "and the slower test would just add CI time. The same "
            "suggestion would be appropriate for a <i>parsing</i> function "
            "where input variety matters; here it is overkill for show, "
            "not for signal.",
            body,
        )
    )
    story.append(
        Paragraph(
            "<b>On framing the rubric pieces.</b> I drafted the "
            "'mocking helping vs hiding' paragraph myself, then asked "
            "Claude to push back on it. It correctly pointed out that I "
            "had not justified <i>why</i> mocking "
            "<i>pathlib.Path.write_text</i> was OK while mocking "
            "<i>PrivacyService.decrypt</i> would not be. I tightened the "
            "distinction - boundary-mocking the OS to exercise an internal "
            "error branch vs. service-mocking the code under test to fake "
            "an outcome - and that is the version that ended up in the "
            "doc. The framing decision is mine; the request to make it "
            "explicit is what AI added.",
            body,
        )
    )
    story.append(
        Paragraph(
            "<b>The honest limit.</b> AI is good at proposing the "
            "structural move and at catching the lazy phrasing. It is not "
            "good at deciding what to test, what coverage is theater, or "
            "which gap is actually load-bearing for a given threat model. "
            "Those calls - the ones the rubric is actually asking about - "
            "have to be mine.",
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

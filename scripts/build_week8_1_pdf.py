"""Build the Week 8.1 Collaborative Git Workflow PDF.

Run from the project root:
    python scripts/build_week8_1_pdf.py
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
OUT_PATH = PROJECT_ROOT / "submissions" / "Week8_1_Collaborative_Git_Workflow.pdf"


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
        title="Week 8.1 Collaborative Git Workflow - AstraNotes",
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
    h3 = ParagraphStyle("h3", parent=styles["Heading3"], fontSize=11.5, spaceBefore=8, spaceAfter=4)
    body = ParagraphStyle("body", parent=styles["Normal"], fontSize=10.5, leading=14, spaceAfter=8)
    quote = ParagraphStyle(
        "quote",
        parent=styles["Normal"],
        fontSize=10,
        leading=13.5,
        leftIndent=14,
        rightIndent=10,
        spaceAfter=8,
        textColor=colors.HexColor("#333333"),
    )

    page_w = page_size[0] - 1.3 * inch
    story = []

    # ---- Cover ----
    story.append(Paragraph("CSEN 296B-2 | Week 8.1 Lab Submission", h1))
    story.append(Paragraph("AstraNotes Collaborative Git Workflow", sub))
    story.append(
        Paragraph(
            "<b>Student Name:</b> Atishay Jain &nbsp;|&nbsp; "
            "<b>Date:</b> May 19, 2026 &nbsp;|&nbsp; "
            "<b>Project:</b> AstraNotes &nbsp;|&nbsp; "
            "<b>Technical Path:</b> Python<br/>"
            "<b>Repository:</b> github.com/Atishay8192261/astranotes (private) &nbsp;|&nbsp; "
            "<b>Pull Request:</b> #1 (merged)",
            info,
        )
    )

    # ---- Collaboration log ----
    story.append(Paragraph("Collaboration Log", h2))
    story.append(
        Paragraph(
            "AstraNotes is a solo build, so I ran the rubric as a <i>two-hat</i> "
            "simulation: author hat on the feature branch, reviewer hat on the "
            "PR. The point was not to perform the motions but to make the "
            "change actually reviewable - branch, commit, PR, critique, merge - "
            "and to write the kind of review I would want from a teammate, "
            "not the kind that just clicks approve.",
            body,
        )
    )
    story.append(
        Paragraph(
            "I picked the change before opening the branch. Candidates were "
            "search improvement, settings/UI polish, and test cleanup. I "
            "chose <b>search</b> because it is the largest unimplemented "
            "behavior in the committed scope (US-06 / FR-07), it has real "
            "edge cases worth reviewing (case folding, decrypt-before-match, "
            "undecryptable notes, empty corpus), and it gives me something "
            "honest to flag in the review instead of rubber-stamping a "
            "trivial diff. Test cleanup would have been too thin to write a "
            "useful PR summary about; UI polish would not have been visually "
            "verifiable without Tk in this environment.",
            body,
        )
    )

    # ---- Workflow ----
    story.append(Paragraph("Branch and PR Workflow Summary", h2))
    wf_rows = [
        [header_cell("Step"), header_cell("What I did"), header_cell("Why")],
        [cell("1"), mono("git checkout main &amp;&amp; git pull"),
         cell("Start from a known-clean baseline; never branch from stale main.")],
        [cell("2"), mono("git checkout -b feature/search-notes"),
         cell("One branch, one idea. Branch name encodes intent (US-06).")],
        [cell("3"), cell("Two focused commits on the branch"),
         cell("Service tier first, then controller/GUI wiring. Each commit small enough that a revert peels one off without taking the other.")],
        [cell("4"), mono("pytest -q"),
         cell("46 pass locally before push. Pushing red wastes a reviewer's time.")],
        [cell("5"), mono("git push -u origin feature/search-notes"),
         cell("Remote-tracked from the start; no orphaned branch later.")],
        [cell("6"), mono("gh pr create"),
         cell("Structured body: summary, traceability, test inventory, deliberate out-of-scope. The PR body is what survives in history.")],
        [cell("7"), mono("gh pr review --comment"),
         cell("Reviewer hat. Did not approve until I had named at least one thing worth changing.")],
        [cell("8"), mono("gh pr merge --squash --delete-branch"),
         cell("Squash keeps main history linear; delete branch keeps the remote tidy.")],
    ]
    story.append(styled_table(wf_rows, [0.5 * inch, 2.5 * inch, page_w - 3.0 * inch]))

    story.append(Paragraph("Branch Purpose", h3))
    story.append(
        Paragraph(
            "<i>feature/search-notes</i> exists to realize the US-06 "
            "keyword-search slice end-to-end, from <i>NoteManager</i> through "
            "the controller seam to a live search entry above the sidebar, "
            "with no other scope.",
            body,
        )
    )

    story.append(Paragraph("Commit Messages (as they appear in the branch)", h3))
    story.append(mono(
        "Add NoteManager.search_notes (FR-07/US-06)<br/><br/>"
        "&nbsp;&nbsp;Case-insensitive substring match across titles and bodies. Private<br/>"
        "&nbsp;&nbsp;notes decrypt before matching; undecryptable notes are skipped with<br/>"
        "&nbsp;&nbsp;an error logged (SPR-01/SPR-02). Empty keyword returns empty list.<br/><br/>"
        "Wire search into controller and GUI sidebar (US-06)<br/><br/>"
        "&nbsp;&nbsp;Adds NotesController.search_notes() passthrough and a search entry<br/>"
        "&nbsp;&nbsp;above the sidebar; live key-release filtering. Empty keyword falls<br/>"
        "&nbsp;&nbsp;back to list_notes (FR-08 ordering preserved). +1 controller test."
    ))
    story.append(
        Paragraph(
            "Both messages name what changed and which requirement it traces "
            "to. Neither rambles. The squash commit on main carries the PR "
            "number (#1) for trace-back.",
            body,
        )
    )

    # ---- PR Summary ----
    story.append(PageBreak())
    story.append(Paragraph("PR Summary (the one I wrote on PR #1)", h2))
    story.append(Paragraph("<b>Title:</b> Add keyword search (US-06 / FR-07)", body))
    story.append(Paragraph("<b>Summary</b>", body))
    for line in [
        "Adds <i>NoteManager.search_notes(keyword)</i> - case-insensitive "
        "substring match across titles and bodies (FR-07).",
        "Private notes are decrypted before matching; undecryptable notes "
        "are skipped with an error logged, preserving SPR-01 (no plaintext "
        "leak) and SPR-02 (no traceback / no path exposure).",
        "Wires the behavior up through <i>NotesController.search_notes()</i> "
        "and a live search entry above the GUI sidebar. Empty keyword falls "
        "back to <i>list_notes()</i> so FR-08 ordering is preserved.",
    ]:
        story.append(Paragraph(f"&bull; {line}", body))

    story.append(Paragraph("<b>Traceability</b>", body))
    trace_rows = [
        [header_cell("ID"), header_cell("How this PR closes / honors it")],
        [cell("US-06"), cell("First realization slice for Search Notes by Keyword.")],
        [cell("FR-07"),
         cell("Case-insensitive, plain substring, decrypted private notes included, failed decryptions excluded, empty collection returns empty list.")],
        [cell("FR-08"),
         cell("Search reuses <i>list_notes()</i> so the existing modified_at-desc ordering test still proves the property.")],
        [cell("SPR-01 / SPR-02"),
         cell("Decryption-failure path exercised by <i>test_search_notes_skips_undecryptable_private_note</i>; no plaintext leak; no path/traceback exposed.")],
    ]
    story.append(styled_table(trace_rows, [1.2 * inch, page_w - 1.2 * inch]))

    story.append(
        Paragraph(
            "<b>Tests:</b> 40 -> 46. Five new service-tier tests + one new "
            "controller test. Full suite green (<i>46 passed in 0.10s</i>), "
            "no Tk required.",
            body,
        )
    )
    story.append(
        Paragraph(
            "<b>Out of scope (deliberate):</b> NFR-01 benchmark, "
            "regex/boolean operators, persisted recent-search history.",
            body,
        )
    )

    # ---- Review ----
    story.append(Paragraph("Example of Review Feedback (the review I wrote on PR #1)", h2))
    story.append(
        Paragraph(
            "I approved with two follow-ups instead of stamping a blind LGTM. "
            "The most useful thing a review can do is say <i>what the diff is "
            "silent about</i>. Excerpt of the review body:",
            body,
        )
    )
    story.append(
        Paragraph(
            "<b>1. Silent skip on decryption failure is logged but not "
            "surfaced to the user (medium severity).</b> <i>search_notes()</i> "
            "delegates to <i>list_notes()</i>, which already drops "
            "un-decryptable private notes with a <i>logger.error</i>. That "
            "preserves SPR-01 (no plaintext leak), but a user searching for "
            "a term that <i>would have</i> matched an un-decryptable note "
            "sees an empty result with no indication that something was "
            "skipped. Consistent with current <i>list_notes()</i> behavior, "
            "so not a regression - but when key-rotation lands (ADR-005 "
            "still Pending), search should surface a 'N notes could not be "
            "searched' hint via the status bar. Refactor candidate, not a "
            "merge blocker.",
            quote,
        )
    )
    story.append(
        Paragraph(
            "<b>2. GUI search rebuilds the entire sidebar on every "
            "KeyRelease (low severity).</b> For the 500-note NFR-01 target "
            "this is borderline - a full <i>list_notes()</i> scan with N "
            "Fernet decryptions happens per keystroke. Not blocking because "
            "(a) NFR-01 is out of scope for this PR, (b) the substring "
            "match itself is microsecond-cheap, (c) decryption dominates "
            "only when many private notes exist. A ~150 ms debounce or an "
            "in-memory plaintext cache would fix it if it becomes a UX "
            "problem.",
            quote,
        )
    )
    story.append(
        Paragraph(
            "Both findings are tracked as refactor notes. Neither blocks the "
            "merge because the merged behavior satisfies FR-07 as written. "
            "That distinction - <i>consistent-with-spec but worth a "
            "follow-up</i> vs. <i>blocks merge</i> - is the call a reviewer "
            "has to make every time, and I tried to make it explicitly.",
            body,
        )
    )
    story.append(
        Paragraph(
            "The non-feedback half of the review matters too: I called out "
            "what was already done well so the next change doesn't "
            "accidentally undo it. The decryption-failure test uses two "
            "real <i>PrivacyService</i> instances with different keys "
            "instead of a mock; that matches the project's 'no mocked "
            "storage' convention from Week 7.2 and would be easy to "
            "regress to a mock under time pressure.",
            body,
        )
    )

    # ---- Merge note ----
    story.append(PageBreak())
    story.append(Paragraph("Merge Decision and Merge-Readiness Note", h2))
    story.append(
        Paragraph(
            "<b>Decision:</b> merged via squash-merge into <i>main</i> on "
            "2026-05-19.",
            body,
        )
    )
    story.append(Paragraph("<b>Why it was safe to merge:</b>", body))
    for line in [
        "Behavior matches FR-07 exactly; no committed acceptance criterion "
        "was bent.",
        "Full test suite green (40 -> 46), including the high-risk SPR-01 "
        "decryption-failure path. The five new service tests use "
        "<i>tmp_path</i> + a real <i>JsonFileRepository</i> + two real "
        "<i>PrivacyService</i> instances - not mocked.",
        "The change is additive. <i>search_notes()</i> is a new public "
        "method; the GUI search entry is a new widget. No existing call "
        "path changed signature or semantics. <i>list_notes()</i> and "
        "FR-08 ordering are untouched.",
        "SPR-01 is provably preserved: the only place private bodies "
        "appear in plaintext is in-memory inside <i>list_notes()</i>, "
        "which is exactly how the codebase already handles list. No new "
        "disk write path was introduced.",
    ]:
        story.append(Paragraph(f"&bull; {line}", body))

    story.append(
        Paragraph(
            "<b>Why a thoughtful reviewer might still hold the merge "
            "(and I chose not to):</b> the keystroke-rate sidebar rebuild "
            "is a latent NFR-01 concern, accepted because NFR-01 is "
            "explicitly out of scope and was not enforced anywhere else "
            "either; the silent-skip behavior is a real UX gap, held "
            "because closing it requires a controller-level result type "
            "that does not belong inside this scoped slice.",
            body,
        )
    )

    # ---- Refactor note ----
    story.append(Paragraph("Refactor Note (post-merge follow-up)", h2))
    story.append(
        Paragraph(
            "Two refactor candidates surfaced during review. Both are "
            "intentionally deferred, with the reason explicit so they "
            "don't decay into 'we'll get to it':",
            body,
        )
    )
    story.append(
        Paragraph(
            "<b>1. Surface skipped-during-search count.</b> Change "
            "<i>NoteManager.search_notes()</i> (and the controller "
            "passthrough) to return <i>(matches, skipped_count)</i>, so the "
            "GUI status bar can show 'N notes could not be searched' when "
            "a decryption failure silently dropped a candidate. Right "
            "<i>after</i> ADR-005 (Pending) is resolved and key-rotation "
            "becomes a real path; doing it now would be designing for a "
            "code path that doesn't yet exist.",
            body,
        )
    )
    story.append(
        Paragraph(
            "<b>2. Debounce the keystroke search.</b> Bind the search "
            "entry to a ~150 ms debounce timer instead of <i>&lt;KeyRelease&gt;</i> "
            "direct. Trivial change, deferred until either a real "
            "performance complaint shows up or the NFR-01 benchmark lands "
            "- whichever is first.",
            body,
        )
    )
    story.append(
        Paragraph(
            "<b>What I will not refactor:</b> the search algorithm itself. "
            "Plain lowercased substring match is exactly what FR-07 "
            "specifies, and the temptation to 'improve' it to regex / "
            "fuzzy / weighted ranking would be scope creep against an "
            "accepted requirement - that goes through the backlog, not "
            "through a code change.",
            body,
        )
    )

    # ---- AI ----
    story.append(PageBreak())
    story.append(Paragraph("How AI Helped, and What I Accepted / Changed / Rejected", h2))
    story.append(
        Paragraph(
            "<b>Accepted.</b> Copilot suggested the explicit "
            "<i>keyword.strip()</i> empty-guard and the test pair "
            "covering both <i>''</i> and <i>'   '</i>. Obvious in "
            "retrospect but easy to miss; I kept them because they are "
            "cheap and they make the FR-07 'empty collection returns "
            "empty list' promise hold for the <i>empty keyword</i> edge "
            "too. Copilot also suggested using two distinct "
            "<i>PrivacyService</i> instances for the undecryptable-search "
            "test rather than monkeypatching <i>decrypt</i> to raise - "
            "matches the convention from Week 7.2, so I took it as-is.",
            body,
        )
    )
    story.append(
        Paragraph(
            "<b>Changed.</b> Copilot's first draft of <i>search_notes</i> "
            "ran a separate decrypt loop inside the search method, "
            "duplicating the <i>list_notes()</i> decrypt-and-skip logic. "
            "I rewrote it to delegate to <i>list_notes()</i> instead. The "
            "rewrite is shorter, but the real reason is that it keeps the "
            "FR-07 / FR-08 contract defined in exactly one place. Two "
            "copies of decrypt-and-skip is two places to leak plaintext "
            "when the next change goes in.",
            body,
        )
    )
    story.append(
        Paragraph(
            "<b>Rejected.</b> Copilot proposed a 'search by tag' "
            "extension and a regex-mode toggle. Both are out of scope per "
            "FR-07 ('plain string matching, not regex') and would violate "
            "the Working Agreement's no-scope-creep rule. I also rejected "
            "its suggestion to add a self-review comment on the PR that "
            "just listed the changes - reviews exist to surface what the "
            "diff is silent about, and a recap of what the diff already "
            "shows is review theater.",
            body,
        )
    )
    story.append(
        Paragraph(
            "<b>On the review itself.</b> I drafted the review note "
            "manually first, then asked Copilot to critique it for "
            "hand-wavy claims. It correctly flagged that my original "
            "phrasing on the keystroke-rebuild concern said 'this might "
            "be slow' without quantifying <i>when</i> it would be slow. I "
            "tightened that paragraph to name the NFR-01 target and the "
            "dominating cost (Fernet decryption), which is what makes it "
            "actionable instead of a vague worry. The keep/change/reject "
            "decisions and the merge call are mine.",
            body,
        )
    )
    story.append(
        Paragraph(
            "<b>The honest limit.</b> AI helped me widen the candidate "
            "list and tighten my review prose. It did not decide what to "
            "merge, what to defer, or what risk profile to accept. Those "
            "are exactly the judgments the rubric asks for, and they have "
            "to be mine.",
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

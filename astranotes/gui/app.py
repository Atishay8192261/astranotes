"""AstraNotes GUI — warm-white glassmorphism redesign (2025 aesthetic).

Design language:
  • Warm off-white background (#F8F7F5) — not harsh pure-white
  • Violet (#7856FF) accent — stands out vs default CTk blue every other student uses
  • Card-based glass panels — subtle borders + inner shadow simulation
  • Body preview in sidebar — much more useful than title-only lists
  • Tag pills — inline coloured chips
  • Dynamic button states — Delete/Duplicate disabled until selection

Strict tier separation maintained: zero business logic or file I/O in this file.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import customtkinter as ctk
from PIL import Image

from astranotes.config import passphrase_store, resolve_data_dir
from astranotes.gui.controller import NotesController, build_default_controller
from astranotes.gui.passphrase_dialog import prompt_setup, prompt_unlock
from astranotes.models.exceptions import PersistenceError, ValidationError
from astranotes.models.note import Note
from astranotes.services.event_logger import EventLogger

# ── default to light mode (warm-white palette) ────────────────────────────────
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# ── colour palette ─────────────────────────────────────────────────────────────
# Tuples: (light, dark)
_BG        = ("#F8F7F5", "#13131F")   # main window
_HEADER    = ("#FFFFFF", "#1A1A2E")   # header bar
_PANEL     = ("#FFFFFF", "#1E1E30")   # sidebar + editor cards
_SIDEBAR   = ("#F2F0EC", "#16162A")   # sidebar chrome
_BORDER    = ("#E8E4DD", "#2A2A42")   # card borders
_SELECTED  = ("#EDE8FF", "#2D2550")   # selected note card
_LOCKED_BG = ("#FFF8EE", "#2A1F0F")   # locked-note card tint
_LOCKED_BD = ("#F5D88C", "#4A3010")   # locked-note border

_TXT1  = ("#1C1C1E", "#F5F5F7")      # primary text
_TXT2  = ("#6E6E73", "#98989F")      # secondary text
_TXT3  = ("#AEAEB2", "#48484A")      # muted text

_ACCENT     = "#7856FF"              # violet brand colour
_ACCENT_H   = "#6244E0"              # hover
_ACCENT_LT  = ("#EDE8FF", "#2D2550") # very-light accent tint

_SUCCESS = "#34C759"
_DANGER  = "#FF3B30"
_WARN    = "#FF9F0A"
_PRIVATE_STRIP = "#FF9F0A"           # amber strip for private notes


# ── helpers ────────────────────────────────────────────────────────────────────

def _load_ctk_image(path: Path, size: tuple[int, int]) -> ctk.CTkImage | None:
    try:
        img = Image.open(path)
        return ctk.CTkImage(light_image=img, dark_image=img, size=size)
    except Exception:
        return None


def _truncate(text: str, n: int) -> str:
    return text if len(text) <= n else text[:n] + "…"


# ── main application window ────────────────────────────────────────────────────

class AstraNotesApp(ctk.CTk):
    def __init__(self, controller: NotesController, key_source: str) -> None:
        super().__init__()
        self._controller = controller
        self._key_source = key_source
        self._selected: Note | None = None
        self._selected_is_locked: bool = False
        self._event_log = EventLogger()

        self.title("AstraNotes")
        self.geometry("1200x740")
        self.minsize(960, 600)
        self.configure(fg_color=_BG)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Window icon
        _assets = Path(__file__).parent.parent / "assets"
        icon_img = _load_ctk_image(_assets / "icon_256.png", (256, 256))
        if icon_img:
            try:
                self.wm_iconphoto(True, icon_img._light_image)
            except Exception:
                pass

        self._build_header()
        self._build_sidebar()
        self._build_editor()
        self._build_statusbar()
        self.refresh_notes_list()
        self._event_log.log("app_started", "AstraNotes launched")

    # ── HEADER ─────────────────────────────────────────────────────────────────

    def _build_header(self) -> None:
        header = ctk.CTkFrame(
            self, height=68, corner_radius=0,
            fg_color=_HEADER, border_width=0,
        )
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        header.grid_columnconfigure(1, weight=1)
        header.grid_propagate(False)

        # ── left: brand ──────────────────────────────────────────────────
        brand = ctk.CTkFrame(header, fg_color="transparent")
        brand.grid(row=0, column=0, padx=(20, 0), pady=12, sticky="w")

        # violet accent pill before logo text
        ctk.CTkFrame(
            brand, width=4, height=32, corner_radius=2, fg_color=_ACCENT
        ).pack(side="left", padx=(0, 12))

        text_stack = ctk.CTkFrame(brand, fg_color="transparent")
        text_stack.pack(side="left")
        ctk.CTkLabel(
            text_stack,
            text="AstraNotes",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=_TXT1,
        ).pack(anchor="w")
        ctk.CTkLabel(
            text_stack,
            text="local-first · private by design",
            font=ctk.CTkFont(size=11),
            text_color=_TXT2,
        ).pack(anchor="w")

        # ── right: action buttons ─────────────────────────────────────────
        btn_row = ctk.CTkFrame(header, fg_color="transparent")
        btn_row.grid(row=0, column=2, padx=20, pady=14, sticky="e")

        for label, cmd, is_accent in (
            ("System",   self._open_admin,    False),
            ("Settings", self._open_settings, False),
            ("About",    self._open_about,    False),
            ("Theme",    self._toggle_theme,  False),
        ):
            bg = (_ACCENT, _ACCENT_H) if is_accent else (("#F2F0EC", "#252535"))
            tc = ("#FFFFFF", "#FFFFFF") if is_accent else _TXT1
            ctk.CTkButton(
                btn_row,
                text=label,
                width=86,
                height=34,
                corner_radius=17,
                fg_color=bg,
                hover_color=("#E8E4DD", "#2E2E48"),
                text_color=tc,
                font=ctk.CTkFont(size=12),
                command=cmd,
            ).pack(side="left", padx=4)

    # ── SIDEBAR ─────────────────────────────────────────────────────────────────

    def _build_sidebar(self) -> None:
        sidebar_wrap = ctk.CTkFrame(self, width=320, fg_color=_SIDEBAR, corner_radius=0)
        sidebar_wrap.grid(row=1, column=0, sticky="nsew")
        sidebar_wrap.grid_propagate(False)
        sidebar_wrap.grid_rowconfigure(2, weight=1)

        # Search bar
        search_frame = ctk.CTkFrame(sidebar_wrap, fg_color="transparent")
        search_frame.grid(row=0, column=0, sticky="ew", padx=14, pady=(14, 6))
        search_frame.grid_columnconfigure(0, weight=1)

        self._search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍  Search notes…",
            height=40,
            corner_radius=12,
            border_width=1,
            border_color=_BORDER,
            fg_color=_PANEL,
            text_color=_TXT1,
            placeholder_text_color=_TXT3,
            font=ctk.CTkFont(size=13),
        )
        self._search_entry.grid(row=0, column=0, sticky="ew")
        self._search_entry.bind("<KeyRelease>", lambda _e: self._on_search())

        # Section label + count badge
        label_row = ctk.CTkFrame(sidebar_wrap, fg_color="transparent")
        label_row.grid(row=1, column=0, sticky="ew", padx=16, pady=(6, 4))
        label_row.grid_columnconfigure(0, weight=1)

        self._sidebar_header = ctk.CTkLabel(
            label_row,
            text="NOTES",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=_TXT3,
            anchor="w",
        )
        self._sidebar_header.grid(row=0, column=0, sticky="w")

        self._note_count_badge = ctk.CTkLabel(
            label_row,
            text="",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=("#FFFFFF", "#FFFFFF"),
            fg_color=(_ACCENT, _ACCENT),
            corner_radius=8,
            width=1,
            padx=6,
            pady=1,
        )
        self._note_count_badge.grid(row=0, column=1, sticky="e")

        # Scrollable note list
        self._sidebar = ctk.CTkScrollableFrame(
            sidebar_wrap,
            fg_color="transparent",
            scrollbar_button_color=_BORDER,
            scrollbar_button_hover_color=_TXT3,
        )
        self._sidebar.grid(row=2, column=0, sticky="nsew", padx=8, pady=(0, 8))

    # ── EDITOR ──────────────────────────────────────────────────────────────────

    def _build_editor(self) -> None:
        outer = ctk.CTkFrame(self, fg_color=_BG)
        outer.grid(row=1, column=1, sticky="nsew", padx=(0, 16), pady=16)
        outer.grid_columnconfigure(0, weight=1)
        outer.grid_rowconfigure(0, weight=1)

        editor = ctk.CTkFrame(
            outer,
            fg_color=_PANEL,
            corner_radius=16,
            border_width=1,
            border_color=_BORDER,
        )
        editor.grid(row=0, column=0, sticky="nsew")
        editor.grid_columnconfigure(0, weight=1)
        editor.grid_rowconfigure(4, weight=1)

        # ── Title ─────────────────────────────────────────────────────────
        ctk.CTkLabel(
            editor,
            text="TITLE",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=_TXT3,
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=24, pady=(20, 3))

        self._title_entry = ctk.CTkEntry(
            editor,
            placeholder_text="Give this note a clear title…",
            height=44,
            corner_radius=10,
            border_width=1,
            border_color=_BORDER,
            fg_color=("#FAFAF8", "#1A1A2A"),
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=_TXT1,
        )
        self._title_entry.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 10))

        # ── Tags + Private switch row ─────────────────────────────────────
        meta_row = ctk.CTkFrame(editor, fg_color="transparent")
        meta_row.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 10))
        meta_row.grid_columnconfigure(0, weight=1)

        self._tags_entry = ctk.CTkEntry(
            meta_row,
            placeholder_text="🏷  Tags  (comma separated)",
            height=36,
            corner_radius=10,
            border_width=1,
            border_color=_BORDER,
            fg_color=("#FAFAF8", "#1A1A2A"),
            font=ctk.CTkFont(size=12),
            text_color=_TXT1,
        )
        self._tags_entry.grid(row=0, column=0, sticky="ew", padx=(0, 12))

        self._private_switch = ctk.CTkSwitch(
            meta_row,
            text="Private",
            font=ctk.CTkFont(size=12),
            text_color=_TXT2,
            button_color=_ACCENT,
            button_hover_color=_ACCENT_H,
            progress_color=_ACCENT_LT,
        )
        self._private_switch.grid(row=0, column=1, sticky="e")

        # ── Body ──────────────────────────────────────────────────────────
        ctk.CTkLabel(
            editor,
            text="BODY",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=_TXT3,
            anchor="w",
        ).grid(row=3, column=0, sticky="w", padx=24, pady=(6, 3))

        self._body_box = ctk.CTkTextbox(
            editor,
            wrap="word",
            corner_radius=10,
            border_width=1,
            border_color=_BORDER,
            fg_color=("#FAFAF8", "#1A1A2A"),
            font=ctk.CTkFont(size=13),
            text_color=_TXT1,
        )
        self._body_box.grid(row=4, column=0, sticky="nsew", padx=24, pady=(0, 10))

        # ── Action buttons ────────────────────────────────────────────────
        btn_row = ctk.CTkFrame(editor, fg_color="transparent")
        btn_row.grid(row=5, column=0, sticky="ew", padx=24, pady=(0, 20))

        # New — ghost style
        self._btn_new = ctk.CTkButton(
            btn_row,
            text="+ New",
            width=90,
            height=38,
            corner_radius=19,
            fg_color="transparent",
            hover_color=_ACCENT_LT,
            border_width=1,
            border_color=_BORDER,
            text_color=_TXT1,
            font=ctk.CTkFont(size=13),
            command=self._new_note,
        )
        self._btn_new.pack(side="left", padx=(0, 8))

        # Save — filled accent
        self._btn_save = ctk.CTkButton(
            btn_row,
            text="Save",
            width=110,
            height=38,
            corner_radius=19,
            fg_color=(_ACCENT, _ACCENT),
            hover_color=(_ACCENT_H, _ACCENT_H),
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._save_note,
        )
        self._btn_save.pack(side="left", padx=(0, 8))

        # Duplicate — ghost / disabled
        self._btn_duplicate = ctk.CTkButton(
            btn_row,
            text="Duplicate",
            width=100,
            height=38,
            corner_radius=19,
            fg_color="transparent",
            hover_color=_ACCENT_LT,
            border_width=1,
            border_color=_BORDER,
            text_color=_TXT2,
            font=ctk.CTkFont(size=13),
            state="disabled",
            command=self._duplicate_note,
        )
        self._btn_duplicate.pack(side="left", padx=(0, 8))

        # Delete — danger / right-aligned
        self._btn_delete = ctk.CTkButton(
            btn_row,
            text="Delete",
            width=90,
            height=38,
            corner_radius=19,
            fg_color="transparent",
            hover_color=("#FFE5E5", "#3A1010"),
            border_width=1,
            border_color=("#FFBDBD", "#6B2020"),
            text_color=(_DANGER, _DANGER),
            font=ctk.CTkFont(size=13),
            state="disabled",
            command=self._delete_note,
        )
        self._btn_delete.pack(side="right")

    # ── STATUS BAR ──────────────────────────────────────────────────────────────

    def _build_statusbar(self) -> None:
        bar = ctk.CTkFrame(
            self,
            fg_color=_HEADER,
            corner_radius=0,
            height=30,
            border_width=0,
        )
        bar.grid(row=2, column=0, columnspan=2, sticky="ew")
        bar.grid_columnconfigure(0, weight=1)
        bar.grid_propagate(False)

        # thin top border
        ctk.CTkFrame(bar, height=1, corner_radius=0, fg_color=_BORDER).place(
            relx=0, rely=0, relwidth=1
        )

        self._status = ctk.CTkLabel(
            bar,
            text="Ready",
            anchor="w",
            font=ctk.CTkFont(size=11),
            text_color=_TXT2,
        )
        self._status.grid(row=0, column=0, sticky="w", padx=16, pady=4)

        self._key_indicator = ctk.CTkLabel(
            bar,
            text=self._key_label(),
            anchor="e",
            font=ctk.CTkFont(size=11),
            text_color=_TXT3,
        )
        self._key_indicator.grid(row=0, column=1, sticky="e", padx=16, pady=4)

    # ── BUTTON STATE MANAGEMENT ────────────────────────────────────────────────

    def _update_button_states(self) -> None:
        editable = self._selected is not None and not self._selected_is_locked
        if editable:
            self._btn_delete.configure(
                state="normal",
                border_color=("#FFBDBD", "#6B2020"),
                text_color=(_DANGER, _DANGER),
            )
            self._btn_duplicate.configure(
                state="normal",
                border_color=(_ACCENT, _ACCENT),
                text_color=(_ACCENT, _ACCENT_H),
            )
        else:
            self._btn_delete.configure(
                state="disabled",
                border_color=_BORDER,
                text_color=_TXT3,
            )
            self._btn_duplicate.configure(
                state="disabled",
                border_color=_BORDER,
                text_color=_TXT3,
            )

    # ── SIDEBAR RENDERING ──────────────────────────────────────────────────────

    def _on_search(self) -> None:
        kw = self._search_entry.get().strip()
        if kw:
            self._event_log.log("search", f"keyword={kw!r}")
        self.refresh_notes_list()

    def refresh_notes_list(self) -> None:
        for child in self._sidebar.winfo_children():
            child.destroy()

        kw = self._search_entry.get().strip() if hasattr(self, "_search_entry") else ""
        notes = (
            self._controller.search_notes(kw)
            if kw
            else self._controller.list_all_for_display()
        )

        # Update header label + badge
        count = len(notes)
        if hasattr(self, "_sidebar_header"):
            label = "MATCHES" if kw else "NOTES"
            self._sidebar_header.configure(text=label)
        if hasattr(self, "_note_count_badge"):
            self._note_count_badge.configure(text=str(count))

        if not notes:
            placeholder = "No matches." if kw else "No notes yet.\nCreate one on the right →"
            ctk.CTkLabel(
                self._sidebar,
                text=placeholder,
                text_color=_TXT3,
                font=ctk.CTkFont(size=13),
                justify="center",
            ).pack(pady=40, padx=14)
            return

        for note in notes:
            self._render_sidebar_item(note)

    def _render_sidebar_item(self, note: Note) -> None:
        """Notion-style compact single-row list item."""
        is_locked   = note.is_private and not self._controller.has_privacy_key
        is_selected = self._selected is not None and self._selected.id == note.id

        # Row background — selected gets a soft violet tint, otherwise transparent
        if is_selected:
            row_bg = ("#EEEAFF", "#2D2550")
        elif is_locked:
            row_bg = ("#FFF8EE", "#2A1F0F")
        else:
            row_bg = "transparent"

        row = ctk.CTkFrame(
            self._sidebar,
            fg_color=row_bg,
            corner_radius=6,
            cursor="hand2",
        )
        row.pack(fill="x", padx=2, pady=1)
        row.grid_columnconfigure(1, weight=1)

        # Left accent dot (2 px wide, full height)
        dot_color = (
            _WARN if is_locked
            else (_ACCENT if note.is_private else "transparent")
        )
        ctk.CTkFrame(row, width=2, corner_radius=1, fg_color=dot_color).grid(
            row=0, column=0, sticky="ns", padx=(4, 0), pady=5
        )

        # Title — single line, truncated
        icon = "🔒 " if is_locked else ("🔐 " if note.is_private else "")
        title_text  = icon + (note.title or "(untitled)")
        title_color = (_WARN, "#C9A84C") if is_locked else _TXT1
        title_font  = ctk.CTkFont(size=13, weight="bold" if is_selected else "normal")

        title_lbl = ctk.CTkLabel(
            row,
            text=_truncate(title_text, 32),
            font=title_font,
            text_color=title_color,
            anchor="w",
        )
        title_lbl.grid(row=0, column=1, sticky="w", padx=(8, 4), pady=(6, 6))

        # Date — right-aligned, muted
        date_lbl = ctk.CTkLabel(
            row,
            text=f"{note.modified_at:%b %d}",
            font=ctk.CTkFont(size=10),
            text_color=_TXT3,
            anchor="e",
            width=42,
        )
        date_lbl.grid(row=0, column=2, sticky="e", padx=(0, 8), pady=6)

        # Click binding
        for widget in (row, title_lbl, date_lbl):
            widget.bind(
                "<Button-1>",
                lambda _e, n=note, lk=is_locked: self._select_note(n, lk),
            )

    # ── NOTE SELECTION ─────────────────────────────────────────────────────────

    def _select_note(self, note: Note, is_locked: bool = False) -> None:
        self._event_log.log("note_selected", f"id={note.id} locked={is_locked}")
        self._selected = note
        self._selected_is_locked = is_locked

        self._title_entry.delete(0, "end")
        self._title_entry.insert(0, note.title)
        self._tags_entry.delete(0, "end")
        self._tags_entry.insert(0, ", ".join(note.tags))
        self._body_box.delete("1.0", "end")

        if is_locked:
            self._body_box.insert(
                "1.0",
                "🔒  This note is encrypted.\n\nEnter your passphrase to unlock and edit it.",
            )
            self._private_switch.select()
            self._update_button_states()
            self._set_status("Locked — enter passphrase to read this note")

            if self._ensure_passphrase():
                refreshed = self._controller.get_note(note.id)
                if refreshed is not None:
                    self._selected_is_locked = False
                    self._select_note(refreshed, False)
            return

        self._body_box.insert("1.0", note.body)
        (self._private_switch.select if note.is_private else self._private_switch.deselect)()
        self._update_button_states()
        self._set_status(f"Editing  '{note.title}'")
        self.refresh_notes_list()

    # ── CRUD ACTIONS ───────────────────────────────────────────────────────────

    def _new_note(self) -> None:
        self._event_log.log("new_note_clicked", "")
        self._selected = None
        self._selected_is_locked = False
        self._title_entry.delete(0, "end")
        self._tags_entry.delete(0, "end")
        self._body_box.delete("1.0", "end")
        self._private_switch.deselect()
        self._update_button_states()
        self._set_status("New note — fill in the fields and click Save")
        self.refresh_notes_list()

    def _save_note(self) -> None:
        title     = self._title_entry.get()
        body      = self._body_box.get("1.0", "end").rstrip("\n")
        tags_csv  = self._tags_entry.get()
        is_priv   = bool(self._private_switch.get())

        if is_priv and not self._controller.has_privacy_key:
            if not self._ensure_passphrase():
                self._set_status("⚠  Passphrase required for private notes")
                return

        if self._selected is None or self._selected_is_locked:
            result = self._controller.create_note(title=title, body=body, is_private=is_priv, tags_csv=tags_csv)
            self._event_log.log("note_created", f"title={title!r} private={is_priv}")
        else:
            result = self._controller.update_note(self._selected.id, title=title, body=body, tags_csv=tags_csv)
            if result.ok and is_priv != self._selected.is_private:
                toggle = self._controller.set_private(self._selected.id, is_priv)
                if not toggle.ok:
                    result = toggle
            self._event_log.log("note_updated", f"id={self._selected.id}")

        self._set_status(("✓  " if result.ok else "✗  ") + result.message)
        if result.ok:
            self._new_note()

    def _delete_note(self) -> None:
        if not self._selected:
            return
        self._event_log.log("note_deleted", f"id={self._selected.id}")
        result = self._controller.delete_note(self._selected.id)
        self._set_status(("✓  " if result.ok else "✗  ") + result.message)
        if result.ok:
            self._new_note()

    def _duplicate_note(self) -> None:
        if not self._selected or self._selected_is_locked:
            return
        self._event_log.log("note_duplicated", f"id={self._selected.id}")
        result = self._controller.duplicate_note(self._selected.id)
        self._set_status(("✓  " if result.ok else "✗  ") + result.message)
        if result.ok:
            self.refresh_notes_list()

    # ── ADMIN / TELEMETRY PANEL ────────────────────────────────────────────────

    def _open_admin(self) -> None:
        self._event_log.log("admin_panel_opened", "")
        stats = self._controller.get_stats()

        win = ctk.CTkToplevel(self)
        win.title("System Health — AstraNotes")
        win.geometry("560x500")
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()
        win.configure(fg_color=_BG)

        ctk.CTkLabel(
            win,
            text="System Health",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=_TXT1,
        ).pack(anchor="w", padx=24, pady=(22, 4))
        ctk.CTkLabel(
            win,
            text="Real-time application & database statistics",
            font=ctk.CTkFont(size=12),
            text_color=_TXT2,
        ).pack(anchor="w", padx=24, pady=(0, 14))

        # Service status card
        sf = ctk.CTkFrame(win, fg_color=_PANEL, corner_radius=12, border_width=1, border_color=_BORDER)
        sf.pack(fill="x", padx=24, pady=(0, 10))
        ctk.CTkLabel(sf, text="SERVICE STATUS", font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=_TXT3, anchor="w").grid(row=0, column=0, columnspan=2, sticky="w", padx=16, pady=(14, 6))

        enc_ok = self._controller.has_privacy_key
        for row_i, (lbl, val, col) in enumerate([
            ("Application",    "● Running",                                  _SUCCESS),
            ("JSON Storage",   "● Accessible",                               _SUCCESS),
            ("Encryption",
             "● Fernet/PBKDF2 — unlocked" if enc_ok
             else "○ Not unlocked (set on first private note)",
             _SUCCESS if enc_ok else _WARN),
        ], start=1):
            ctk.CTkLabel(sf, text=lbl, font=ctk.CTkFont(size=13), text_color=_TXT2, anchor="w").grid(
                row=row_i, column=0, sticky="w", padx=16, pady=4)
            ctk.CTkLabel(sf, text=val, font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=col, anchor="w").grid(row=row_i, column=1, sticky="w", padx=8, pady=4)
        ctk.CTkFrame(sf, height=10, fg_color="transparent").grid(row=99, column=0)

        # DB stats card
        df = ctk.CTkFrame(win, fg_color=_PANEL, corner_radius=12, border_width=1, border_color=_BORDER)
        df.pack(fill="x", padx=24, pady=(0, 10))
        ctk.CTkLabel(df, text="DATABASE STATISTICS", font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=_TXT3, anchor="w").grid(row=0, column=0, columnspan=2, sticky="w", padx=16, pady=(14, 6))

        for row_i, (lbl, val) in enumerate([
            ("Total Notes",               str(stats["total_notes"])),
            ("Public Notes",              str(stats["public_notes"])),
            ("Private (encrypted) Notes", str(stats["private_notes"])),
            ("Storage Used",              f"{stats['storage_bytes']:,} bytes"),
            ("Avg. Content Length",       f"{stats['avg_body_length']:.0f} chars"),
            ("Data Directory",            stats["data_dir"]),
        ], start=1):
            ctk.CTkLabel(df, text=lbl, font=ctk.CTkFont(size=13), text_color=_TXT2, anchor="w").grid(
                row=row_i, column=0, sticky="w", padx=16, pady=4)
            ctk.CTkLabel(df, text=val, font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=_TXT1, anchor="w").grid(row=row_i, column=1, sticky="w", padx=10, pady=4)
        ctk.CTkFrame(df, height=10, fg_color="transparent").grid(row=99, column=0)

        ctk.CTkButton(
            win, text="Close", width=100, height=36, corner_radius=18,
            fg_color=(_ACCENT, _ACCENT), hover_color=(_ACCENT_H, _ACCENT_H),
            text_color="#FFFFFF", font=ctk.CTkFont(size=13),
            command=win.destroy,
        ).pack(pady=(4, 20))

    # ── SETTINGS / ABOUT ──────────────────────────────────────────────────────

    def _open_settings(self) -> None:
        self._event_log.log("settings_opened", "")
        win = ctk.CTkToplevel(self)
        win.title("Settings — AstraNotes")
        win.geometry("500x300")
        win.resizable(False, False)
        win.transient(self)
        win.configure(fg_color=_BG)

        ctk.CTkLabel(win, text="Settings", font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=_TXT1).pack(anchor="w", padx=24, pady=(22, 12))

        card = ctk.CTkFrame(win, fg_color=_PANEL, corner_radius=12, border_width=1, border_color=_BORDER)
        card.pack(fill="x", padx=24, pady=(0, 12))
        for lbl, val in [
            ("Data directory", str(resolve_data_dir())),
            ("Privacy key",    self._key_source),
            ("Event log",      str(self._event_log.log_path)),
        ]:
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=5)
            ctk.CTkLabel(row, text=lbl, font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=_TXT2, width=130, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=val, font=ctk.CTkFont(size=12),
                         text_color=_TXT1, anchor="w", wraplength=280).pack(side="left")

        ctk.CTkButton(win, text="Close", width=100, height=36, corner_radius=18,
                      fg_color=(_ACCENT, _ACCENT), hover_color=(_ACCENT_H, _ACCENT_H),
                      text_color="#FFFFFF", command=win.destroy).pack(pady=(0, 20))

    def _open_about(self) -> None:
        self._event_log.log("about_opened", "")
        win = ctk.CTkToplevel(self)
        win.title("About AstraNotes")
        win.geometry("500x420")
        win.resizable(False, False)
        win.transient(self)
        win.configure(fg_color=_BG)

        # Purple accent strip at top
        ctk.CTkFrame(win, height=4, corner_radius=0, fg_color=_ACCENT).pack(fill="x")

        ctk.CTkLabel(win, text="AstraNotes  v0.3.0",
                     font=ctk.CTkFont(size=18, weight="bold"), text_color=_TXT1).pack(
            anchor="w", padx=24, pady=(18, 4))
        ctk.CTkLabel(win, text="Local-first, single-user, privacy-first note-taking",
                     font=ctk.CTkFont(size=13), text_color=_TXT2).pack(anchor="w", padx=24, pady=(0, 14))

        card = ctk.CTkFrame(win, fg_color=_PANEL, corner_radius=12, border_width=1, border_color=_BORDER)
        card.pack(fill="x", padx=24, pady=(0, 16))
        specs = [
            ("Architecture",  "3-tier MVC  ·  View → Controller → Model"),
            ("Encryption",    "Fernet (AES-128-CBC + HMAC-SHA256)"),
            ("Key derivation","PBKDF2-HMAC-SHA256  ·  600 000 iterations"),
            ("Tests",         "92 passing  ·  14 BDD Gherkin scenarios"),
            ("Course",        "CSEN 296B-2  ·  Spring 2026  ·  SCU"),
        ]
        for lbl, val in specs:
            r = ctk.CTkFrame(card, fg_color="transparent")
            r.pack(fill="x", padx=16, pady=5)
            ctk.CTkLabel(r, text=lbl, font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=_TXT2, width=130, anchor="w").pack(side="left")
            ctk.CTkLabel(r, text=val, font=ctk.CTkFont(size=12),
                         text_color=_TXT1, anchor="w").pack(side="left")

        ctk.CTkFrame(card, height=8, fg_color="transparent").pack()

        ctk.CTkButton(win, text="Close", width=120, height=38, corner_radius=19,
                      fg_color=(_ACCENT, _ACCENT), hover_color=(_ACCENT_H, _ACCENT_H),
                      text_color="#FFFFFF", font=ctk.CTkFont(size=13),
                      command=win.destroy).pack(pady=(0, 24))

    def _toggle_theme(self) -> None:
        mode = "light" if ctk.get_appearance_mode() == "Dark" else "dark"
        ctk.set_appearance_mode(mode)
        self._event_log.log("theme_toggled", mode)

    # ── STATUS BAR HELPERS ────────────────────────────────────────────────────

    def _key_label(self) -> str:
        return "🔓 unlocked" if self._controller.has_privacy_key else "🔒 no passphrase set"

    def _set_status(self, text: str) -> None:
        self._status.configure(text=text)
        if hasattr(self, "_key_indicator"):
            self._key_indicator.configure(text=self._key_label())

    # ── LAZY PASSPHRASE HANDLING ──────────────────────────────────────────────

    def _ensure_passphrase(self) -> bool:
        store = passphrase_store()
        if store.exists():
            for _ in range(3):
                value = prompt_unlock(self)
                if value is None:
                    return False
                try:
                    self._controller.set_privacy_service(store.unlock(value))
                    self._key_source = "passphrase (PBKDF2)"
                    self._event_log.log("passphrase_unlocked", "success")
                    self.refresh_notes_list()
                    return True
                except PersistenceError:
                    continue
            self._event_log.log("passphrase_failed", "too many attempts")
            return False

        value = prompt_setup(self)
        if value is None:
            return False
        try:
            self._controller.set_privacy_service(store.initialize(value))
            self._key_source = "passphrase (PBKDF2)"
            self._event_log.log("passphrase_setup", "new passphrase configured")
            return True
        except (PersistenceError, ValidationError) as exc:
            self._set_status(str(exc))
            return False


# ── entry point ────────────────────────────────────────────────────────────────

def main() -> None:
    if os.environ.get("ASTRANOTES_KEY"):
        controller, key_source = build_default_controller()
        AstraNotesApp(controller, key_source).mainloop()
        return

    store = passphrase_store()
    if store.exists():
        bootstrap = ctk.CTk()
        bootstrap.withdraw()
        privacy = None
        for _ in range(3):
            value = prompt_unlock(bootstrap)
            if value is None:
                bootstrap.destroy()
                print("Unlock cancelled.", file=sys.stderr)
                return
            try:
                privacy = store.unlock(value)
                break
            except PersistenceError:
                continue
        bootstrap.destroy()
        if privacy is None:
            print("Too many failed attempts.", file=sys.stderr)
            return
        controller, key_source = build_default_controller(
            privacy=privacy, key_source="passphrase (PBKDF2)"
        )
        AstraNotesApp(controller, key_source).mainloop()
        return

    controller, key_source = build_default_controller(
        privacy=None, key_source="no passphrase (set on first private note)"
    )
    AstraNotesApp(controller, key_source).mainloop()


if __name__ == "__main__":
    main()

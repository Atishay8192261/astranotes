"""CustomTkinter view — AstraNotes presentation tier (3-tier MVC).

All user actions delegate to NotesController. No business logic, no
encryption, and no file I/O lives in this file — strict tier separation
enforces NFR-02. The controller is headlessly unit-testable as a result.
"""

from __future__ import annotations

import os
import sys

import customtkinter as ctk

from astranotes.config import passphrase_store, resolve_data_dir
from astranotes.gui.controller import NotesController, build_default_controller
from astranotes.gui.passphrase_dialog import prompt_setup, prompt_unlock
from astranotes.models.exceptions import PersistenceError, ValidationError
from astranotes.models.note import Note
from astranotes.services.event_logger import EventLogger

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class AstraNotesApp(ctk.CTk):
    def __init__(self, controller: NotesController, key_source: str) -> None:
        super().__init__()
        self._controller = controller
        self._key_source = key_source
        self._selected: Note | None = None
        self._selected_is_locked: bool = False
        self._event_log = EventLogger()

        self.title("AstraNotes")
        self.geometry("1140x720")
        self.minsize(900, 580)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.configure(fg_color=("#f4f5f7", "#1a1c20"))

        self._build_header()
        self._build_sidebar()
        self._build_editor()
        self._build_statusbar()
        self.refresh_notes_list()
        self._event_log.log("app_started", "AstraNotes launched")

    # ── layout ────────────────────────────────────────────────────────────

    def _build_header(self) -> None:
        header = ctk.CTkFrame(
            self, height=64, corner_radius=0, fg_color=("#ffffff", "#23262d")
        )
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.grid(row=0, column=0, padx=(18, 0), pady=10, sticky="w")
        ctk.CTkLabel(
            title_box,
            text="AstraNotes",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(anchor="w")
        self._subtitle = ctk.CTkLabel(
            title_box,
            text="local-first · private by design",
            font=ctk.CTkFont(size=11),
            text_color=("#6c757d", "#94a3b8"),
        )
        self._subtitle.pack(anchor="w")

        actions = ctk.CTkFrame(header, fg_color="transparent")
        actions.grid(row=0, column=2, padx=16, pady=12, sticky="e")
        for label, cmd in (
            ("System", self._open_admin),
            ("Settings", self._open_settings),
            ("About", self._open_about),
            ("Theme", self._toggle_theme),
        ):
            ctk.CTkButton(
                actions, text=label, width=90, height=32, corner_radius=8, command=cmd
            ).pack(side="left", padx=4)

    def _build_sidebar(self) -> None:
        wrapper = ctk.CTkFrame(self, width=300, fg_color="transparent")
        wrapper.grid(row=1, column=0, sticky="nsw", padx=(14, 8), pady=14)
        wrapper.grid_rowconfigure(2, weight=1)

        self._search_entry = ctk.CTkEntry(
            wrapper,
            placeholder_text="Search title or body…",
            height=36,
            corner_radius=10,
        )
        self._search_entry.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self._search_entry.bind("<KeyRelease>", lambda _e: self._on_search())

        self._sidebar_header = ctk.CTkLabel(
            wrapper,
            text="Notes",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#6c757d", "#94a3b8"),
            anchor="w",
        )
        self._sidebar_header.grid(row=1, column=0, sticky="ew", pady=(0, 4), padx=4)

        self._sidebar = ctk.CTkScrollableFrame(
            wrapper, width=290, fg_color=("#ffffff", "#23262d"), corner_radius=12
        )
        self._sidebar.grid(row=2, column=0, sticky="nsew")

    def _build_editor(self) -> None:
        editor = ctk.CTkFrame(
            self, fg_color=("#ffffff", "#23262d"), corner_radius=12
        )
        editor.grid(row=1, column=1, sticky="nsew", padx=(8, 14), pady=14)
        editor.grid_columnconfigure(0, weight=1)
        editor.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(
            editor,
            text="Title",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=("#6c757d", "#94a3b8"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(16, 2))
        self._title_entry = ctk.CTkEntry(
            editor,
            placeholder_text="Give your note a title…",
            height=38,
            corner_radius=10,
            font=ctk.CTkFont(size=14),
        )
        self._title_entry.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 8))

        row2 = ctk.CTkFrame(editor, fg_color="transparent")
        row2.grid(row=2, column=0, sticky="ew", padx=18, pady=6)
        row2.grid_columnconfigure(0, weight=1)
        self._tags_entry = ctk.CTkEntry(
            row2,
            placeholder_text="Tags (comma separated)",
            height=34,
            corner_radius=10,
        )
        self._tags_entry.grid(row=0, column=0, sticky="ew")
        self._private_switch = ctk.CTkSwitch(
            row2, text="Private (encrypted)", height=34
        )
        self._private_switch.grid(row=0, column=1, padx=(12, 0))

        ctk.CTkLabel(
            editor,
            text="Body",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=("#6c757d", "#94a3b8"),
            anchor="w",
        ).grid(row=3, column=0, sticky="w", padx=18, pady=(10, 2))
        self._body_box = ctk.CTkTextbox(
            editor,
            wrap="word",
            corner_radius=10,
            font=ctk.CTkFont(size=13),
            fg_color=("#fafbfc", "#1d2026"),
        )
        self._body_box.grid(row=5, column=0, sticky="nsew", padx=18, pady=(0, 8))

        btn_row = ctk.CTkFrame(editor, fg_color="transparent")
        btn_row.grid(row=6, column=0, sticky="ew", padx=18, pady=(0, 16))

        self._btn_new = ctk.CTkButton(
            btn_row, text="+ New", width=90, height=36, corner_radius=10,
            command=self._new_note,
        )
        self._btn_new.pack(side="left", padx=(0, 6))

        self._btn_save = ctk.CTkButton(
            btn_row, text="Save", width=120, height=36, corner_radius=10,
            command=self._save_note,
        )
        self._btn_save.pack(side="left", padx=6)

        self._btn_duplicate = ctk.CTkButton(
            btn_row,
            text="Duplicate",
            width=110,
            height=36,
            corner_radius=10,
            state="disabled",
            fg_color=("#adb5bd", "#4a5568"),
            hover_color=("#868e96", "#3d4655"),
            command=self._duplicate_note,
        )
        self._btn_duplicate.pack(side="left", padx=6)

        self._btn_delete = ctk.CTkButton(
            btn_row,
            text="Delete",
            width=100,
            height=36,
            corner_radius=10,
            state="disabled",
            fg_color=("#b91c1c", "#7f1d1d"),
            hover_color=("#dc2626", "#991b1b"),
            command=self._delete_note,
        )
        self._btn_delete.pack(side="right", padx=(6, 0))

    def _build_statusbar(self) -> None:
        bar = ctk.CTkFrame(
            self, fg_color=("#ffffff", "#23262d"), corner_radius=0, height=32
        )
        bar.grid(row=2, column=0, columnspan=2, sticky="ew")
        bar.grid_columnconfigure(0, weight=1)

        self._status = ctk.CTkLabel(
            bar, text="Ready", anchor="w", font=ctk.CTkFont(size=11)
        )
        self._status.grid(row=0, column=0, sticky="w", padx=14, pady=6)

        key_label = (
            "[ unlocked ]"
            if self._controller.has_privacy_key
            else "[ no passphrase set ]"
        )
        self._key_indicator = ctk.CTkLabel(
            bar,
            text=key_label,
            anchor="e",
            font=ctk.CTkFont(size=11),
            text_color=("#6c757d", "#94a3b8"),
        )
        self._key_indicator.grid(row=0, column=1, sticky="e", padx=14, pady=6)

    # ── button-state management ────────────────────────────────────────────

    def _update_button_states(self) -> None:
        """Enable Delete / Duplicate only when a non-locked note is selected."""
        editable = self._selected is not None and not self._selected_is_locked
        if editable:
            self._btn_delete.configure(state="normal", fg_color=("#b91c1c", "#7f1d1d"))
            self._btn_duplicate.configure(state="normal", fg_color=("#1f6aa5", "#1f538d"))
        else:
            self._btn_delete.configure(state="disabled", fg_color=("#b91c1c", "#7f1d1d"))
            self._btn_duplicate.configure(state="disabled", fg_color=("#adb5bd", "#4a5568"))

    # ── behaviour — delegates to controller ───────────────────────────────

    def _on_search(self) -> None:
        keyword = self._search_entry.get().strip()
        if keyword:
            self._event_log.log("search", f"keyword={keyword!r}")
        self.refresh_notes_list()

    def refresh_notes_list(self) -> None:
        for child in self._sidebar.winfo_children():
            child.destroy()

        keyword = (
            self._search_entry.get().strip()
            if hasattr(self, "_search_entry")
            else ""
        )
        if keyword:
            notes = self._controller.search_notes(keyword)
        else:
            notes = self._controller.list_all_for_display()

        if hasattr(self, "_sidebar_header"):
            count = len(notes)
            if keyword:
                label = f"  Notes  ·  {count} match{'es' if count != 1 else ''}"
            else:
                label = f"  Notes  ·  {count} note{'s' if count != 1 else ''}"
            self._sidebar_header.configure(text=label)

        if not notes:
            placeholder = (
                "No matches for that search."
                if keyword
                else "No notes yet — create one on the right."
            )
            ctk.CTkLabel(
                self._sidebar,
                text=placeholder,
                text_color=("#9aa0a6", "#6c757d"),
                font=ctk.CTkFont(size=12),
            ).pack(pady=24, padx=14)
            return

        for note in notes:
            self._render_sidebar_item(note)

    def _render_sidebar_item(self, note: Note) -> None:
        is_locked = note.is_private and not self._controller.has_privacy_key
        is_selected = self._selected is not None and self._selected.id == note.id

        if is_selected:
            bg = ("#e9efff", "#2d3140")
        elif is_locked:
            bg = ("#fff8e1", "#2a2318")
        else:
            bg = "transparent"

        item = ctk.CTkFrame(
            self._sidebar, fg_color=bg, corner_radius=10, cursor="hand2"
        )
        item.pack(fill="x", padx=6, pady=3)

        title_text = f"🔒 {note.title or '(untitled)'}" if is_locked else (note.title or "(untitled)")
        title_color = ("#92610a", "#c9a84c") if is_locked else ("white" if is_selected else ("#1a1c20", "#f8f9fa"))
        top = ctk.CTkLabel(
            item,
            text=title_text,
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
            justify="left",
            text_color=title_color,
        )
        top.pack(fill="x", padx=12, pady=(8, 0))

        meta_parts = [f"{note.modified_at:%b %d  ·  %H:%M}"]
        if is_locked:
            meta_parts.append("encrypted — click to unlock")
        elif note.is_private:
            meta_parts.append("private")
        if note.tags and not is_locked:
            meta_parts.append(" · ".join(note.tags[:3]))

        meta = ctk.CTkLabel(
            item,
            text="  ·  ".join(meta_parts),
            font=ctk.CTkFont(size=10),
            text_color=("#6c757d", "#94a3b8"),
            anchor="w",
        )
        meta.pack(fill="x", padx=12, pady=(0, 8))

        for widget in (item, top, meta):
            widget.bind(
                "<Button-1>",
                lambda _e, n=note, locked=is_locked: self._select_note(n, locked),
            )

    def _select_note(self, note: Note, is_locked: bool = False) -> None:
        self._event_log.log(
            "note_selected",
            f"id={note.id} title={note.title!r} locked={is_locked}",
        )

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
                "🔒  This note is encrypted.\n\nClick [Unlock] below, or save a new note above.",
            )
            self._private_switch.select()
            self._update_button_states()
            self._set_status("Locked note — enter your passphrase to edit")

            if self._ensure_passphrase():
                refreshed = self._controller.get_note(note.id)
                if refreshed is not None:
                    self._selected_is_locked = False
                    self._select_note(refreshed, False)
            return

        self._body_box.insert("1.0", note.body)
        if note.is_private:
            self._private_switch.select()
        else:
            self._private_switch.deselect()
        self._update_button_states()
        self._set_status(f"Editing '{note.title}'  (Save updates this note)")

    def _new_note(self) -> None:
        self._event_log.log("new_note_clicked", "")
        self._selected = None
        self._selected_is_locked = False
        self._title_entry.delete(0, "end")
        self._tags_entry.delete(0, "end")
        self._body_box.delete("1.0", "end")
        self._private_switch.deselect()
        self._update_button_states()
        self._set_status("New note")

    def _save_note(self) -> None:
        title = self._title_entry.get()
        body = self._body_box.get("1.0", "end").rstrip("\n")
        tags_csv = self._tags_entry.get()
        switch_private = bool(self._private_switch.get())

        if switch_private and not self._controller.has_privacy_key:
            if not self._ensure_passphrase():
                self._set_status("Passphrase required for private notes")
                return

        if self._selected is None or self._selected_is_locked:
            result = self._controller.create_note(
                title=title, body=body, is_private=switch_private, tags_csv=tags_csv
            )
            self._event_log.log(
                "note_created", f"title={title!r} private={switch_private}"
            )
        else:
            result = self._controller.update_note(
                self._selected.id, title=title, body=body, tags_csv=tags_csv
            )
            if result.ok and switch_private != self._selected.is_private:
                toggle = self._controller.set_private(self._selected.id, switch_private)
                if not toggle.ok:
                    result = toggle
            self._event_log.log(
                "note_updated", f"id={self._selected.id} title={title!r}"
            )

        self._set_status(result.message)
        if result.ok:
            self._new_note()
            self.refresh_notes_list()

    def _delete_note(self) -> None:
        if self._selected is None:
            self._set_status("Select a note to delete")
            return
        self._event_log.log(
            "note_deleted",
            f"id={self._selected.id} title={self._selected.title!r}",
        )
        result = self._controller.delete_note(self._selected.id)
        self._set_status(result.message)
        if result.ok:
            self._new_note()
            self.refresh_notes_list()

    def _duplicate_note(self) -> None:
        if self._selected is None or self._selected_is_locked:
            return
        self._event_log.log("note_duplicated", f"id={self._selected.id}")
        result = self._controller.duplicate_note(self._selected.id)
        self._set_status(result.message)
        if result.ok:
            self.refresh_notes_list()

    # ── admin / telemetry panel ────────────────────────────────────────────

    def _open_admin(self) -> None:
        self._event_log.log("admin_panel_opened", "")
        stats = self._controller.get_stats()

        win = ctk.CTkToplevel(self)
        win.title("System Health — AstraNotes")
        win.geometry("560x460")
        win.transient(self)
        win.grab_set()

        ctk.CTkLabel(
            win,
            text="System Health Dashboard",
            font=ctk.CTkFont(size=17, weight="bold"),
        ).pack(anchor="w", padx=22, pady=(20, 6))

        # ── service status ──────────────────────────────────────────────
        sf = ctk.CTkFrame(win, corner_radius=10)
        sf.pack(fill="x", padx=22, pady=8)
        ctk.CTkLabel(
            sf, text="Service Status",
            font=ctk.CTkFont(size=12, weight="bold"), anchor="w",
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=14, pady=(10, 6))

        enc_ok = self._controller.has_privacy_key
        status_rows = [
            ("Application",   "● Running",                          "#22c55e"),
            ("JSON Storage",  "● Accessible",                       "#22c55e"),
            ("Encryption",
             "● Fernet/PBKDF2 — unlocked" if enc_ok else "○ Not unlocked (set on first private note)",
             "#22c55e" if enc_ok else "#f59e0b"),
        ]
        for row_i, (lbl, val, col) in enumerate(status_rows, start=1):
            ctk.CTkLabel(sf, text=lbl, anchor="w").grid(
                row=row_i, column=0, sticky="w", padx=14, pady=3
            )
            ctk.CTkLabel(sf, text=val, anchor="w", text_color=col).grid(
                row=row_i, column=1, sticky="w", padx=8, pady=3
            )
        ctk.CTkFrame(sf, height=8, fg_color="transparent").grid(row=99, column=0)

        # ── database statistics ─────────────────────────────────────────
        df = ctk.CTkFrame(win, corner_radius=10)
        df.pack(fill="x", padx=22, pady=8)
        ctk.CTkLabel(
            df, text="Database Statistics",
            font=ctk.CTkFont(size=12, weight="bold"), anchor="w",
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=14, pady=(10, 6))

        db_rows = [
            ("Total Notes",                str(stats["total_notes"])),
            ("Public Notes",               str(stats["public_notes"])),
            ("Private (encrypted) Notes",  str(stats["private_notes"])),
            ("Storage Used",               f"{stats['storage_bytes']:,} bytes"),
            ("Avg. Content Length",        f"{stats['avg_body_length']:.0f} chars"),
            ("Data Directory",             stats["data_dir"]),
        ]
        for row_i, (lbl, val) in enumerate(db_rows, start=1):
            ctk.CTkLabel(df, text=lbl, anchor="w").grid(
                row=row_i, column=0, sticky="w", padx=14, pady=3
            )
            ctk.CTkLabel(
                df, text=val, anchor="w",
                text_color=("#374151", "#94a3b8"),
            ).grid(row=row_i, column=1, sticky="w", padx=10, pady=3)
        ctk.CTkFrame(df, height=8, fg_color="transparent").grid(row=99, column=0)

        ctk.CTkButton(win, text="Close", width=100, command=win.destroy).pack(
            pady=(10, 20)
        )

    # ── settings / about ──────────────────────────────────────────────────

    def _open_settings(self) -> None:
        self._event_log.log("settings_opened", "")
        win = ctk.CTkToplevel(self)
        win.title("Settings")
        win.geometry("480x280")
        win.transient(self)
        ctk.CTkLabel(
            win, text="Settings", font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=16, pady=(16, 8))
        ctk.CTkLabel(win, text=f"Data directory:   {resolve_data_dir()}").pack(
            anchor="w", padx=16, pady=4
        )
        ctk.CTkLabel(win, text=f"Privacy key:   {self._key_source}").pack(
            anchor="w", padx=16, pady=4
        )
        ctk.CTkLabel(
            win, text=f"Event log:   {self._event_log.log_path}"
        ).pack(anchor="w", padx=16, pady=4)
        ctk.CTkLabel(
            win,
            text="AstraNotes is single-user; no account management required.",
            text_color="gray",
            justify="left",
        ).pack(anchor="w", padx=16, pady=8)
        ctk.CTkButton(win, text="Close", width=80, command=win.destroy).pack(pady=(0, 16))

    def _open_about(self) -> None:
        self._event_log.log("about_opened", "")
        win = ctk.CTkToplevel(self)
        win.title("About AstraNotes")
        win.geometry("460x260")
        win.transient(self)
        ctk.CTkLabel(
            win, text="AstraNotes  v0.3.0", font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=16, pady=(16, 8))
        ctk.CTkLabel(
            win,
            text=(
                "Local-first, single-user secure note-taking application.\n\n"
                "Architecture: 3-tier MVC\n"
                "  View     →  CustomTkinter (this window)\n"
                "  Controller → NotesController (widget-free)\n"
                "  Model    →  NoteManager + JsonFileRepository\n\n"
                "Encryption: Fernet (AES-128-CBC + HMAC-SHA256)\n"
                "Key derivation: PBKDF2-HMAC-SHA256 · 600 000 iterations\n\n"
                "Course: CSEN 296B-2 · Spring 2026 · Santa Clara University"
            ),
            justify="left",
        ).pack(anchor="w", padx=16, pady=4)
        ctk.CTkButton(win, text="Close", width=80, command=win.destroy).pack(pady=(0, 16))

    def _toggle_theme(self) -> None:
        mode = "light" if ctk.get_appearance_mode() == "Dark" else "dark"
        ctk.set_appearance_mode(mode)
        self._event_log.log("theme_toggled", mode)

    # ── status bar helper ─────────────────────────────────────────────────

    def _set_status(self, text: str) -> None:
        self._status.configure(text=text)
        if hasattr(self, "_key_indicator"):
            self._key_indicator.configure(
                text=(
                    "[ unlocked ]"
                    if self._controller.has_privacy_key
                    else "[ no passphrase set ]"
                )
            )

    # ── lazy passphrase handling ──────────────────────────────────────────

    def _ensure_passphrase(self) -> bool:
        """Prompt for passphrase unlock/setup; returns True on success."""
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
    """Launch the GUI — passphrase precedence: env-var → stored → none (ADR-005)."""
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
                print("Unlock cancelled. Exiting.", file=sys.stderr)
                return
            try:
                privacy = store.unlock(value)
                break
            except PersistenceError:
                continue
        bootstrap.destroy()
        if privacy is None:
            print("Too many failed unlock attempts. Exiting.", file=sys.stderr)
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

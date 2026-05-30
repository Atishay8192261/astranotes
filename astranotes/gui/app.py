"""CustomTkinter view - the AstraNotes presentation tier (3-tier frontend).

This is a thin shell. Every user action delegates to NotesController, which
holds the only reference to the logic tier. No business rule, no encryption,
no file path lives in this file - that is what keeps the tiers separate
(NFR-02) and the controller headlessly testable.
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

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class AstraNotesApp(ctk.CTk):
    def __init__(self, controller: NotesController, key_source: str) -> None:
        super().__init__()
        self._controller = controller
        self._key_source = key_source
        self._selected: Note | None = None

        self.title("AstraNotes — local-first notes")
        self.geometry("1100x700")
        self.minsize(880, 560)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.configure(fg_color=("#f4f5f7", "#1a1c20"))

        self._build_header()
        self._build_sidebar()
        self._build_editor()
        self._build_statusbar()
        self.refresh_notes_list()

    # ---- layout ----------------------------------------------------------
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
        self._search_entry.bind("<KeyRelease>", lambda _e: self.refresh_notes_list())

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
        editor = ctk.CTkFrame(self, fg_color=("#ffffff", "#23262d"), corner_radius=12)
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
            row2, text="Private (encrypt at rest)", height=34
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

        buttons = ctk.CTkFrame(editor, fg_color="transparent")
        buttons.grid(row=6, column=0, sticky="ew", padx=18, pady=(0, 16))
        ctk.CTkButton(
            buttons, text="New", width=90, height=36, corner_radius=10, command=self._new_note
        ).pack(side="left", padx=(0, 6))
        ctk.CTkButton(
            buttons, text="Save", width=120, height=36, corner_radius=10, command=self._save_note
        ).pack(side="left", padx=6)
        ctk.CTkButton(
            buttons,
            text="Delete",
            width=100,
            height=36,
            corner_radius=10,
            fg_color="#b91c1c",
            hover_color="#dc2626",
            command=self._delete_note,
        ).pack(side="right", padx=(6, 0))

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

        key_label = "[ unlocked ]" if self._controller.has_privacy_key else "[ no passphrase set ]"
        self._key_indicator = ctk.CTkLabel(
            bar,
            text=key_label,
            anchor="e",
            font=ctk.CTkFont(size=11),
            text_color=("#6c757d", "#94a3b8"),
        )
        self._key_indicator.grid(row=0, column=1, sticky="e", padx=14, pady=6)

    # ---- behavior (delegates to the controller) --------------------------
    def refresh_notes_list(self) -> None:
        for child in self._sidebar.winfo_children():
            child.destroy()
        keyword = self._search_entry.get().strip() if hasattr(self, "_search_entry") else ""
        notes = self._controller.search_notes(keyword) if keyword else self._controller.list_notes()
        if hasattr(self, "_sidebar_header"):
            count = len(notes)
            suffix = "" if count == 1 else "s"
            label = f"  Notes  ·  {count} match{'es' if count != 1 else ''}" if keyword else f"  Notes  ·  {count} note{suffix}"
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
        is_selected = self._selected is not None and self._selected.id == note.id
        item = ctk.CTkFrame(
            self._sidebar,
            fg_color=("#e9efff", "#2d3140") if is_selected else "transparent",
            corner_radius=10,
            cursor="hand2",
        )
        item.pack(fill="x", padx=6, pady=3)
        item.bind("<Button-1>", lambda _e, n=note: self._select_note(n))

        top = ctk.CTkLabel(
            item,
            text=note.title or "(untitled)",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
            justify="left",
        )
        top.pack(fill="x", padx=12, pady=(8, 0))
        top.bind("<Button-1>", lambda _e, n=note: self._select_note(n))

        meta_parts = [f"{note.modified_at:%b %d  ·  %H:%M}"]
        if note.is_private:
            meta_parts.append("private")
        if note.tags:
            meta_parts.append(" · ".join(note.tags[:3]))
        meta = ctk.CTkLabel(
            item,
            text="  ·  ".join(meta_parts),
            font=ctk.CTkFont(size=10),
            text_color=("#6c757d", "#94a3b8"),
            anchor="w",
        )
        meta.pack(fill="x", padx=12, pady=(0, 8))
        meta.bind("<Button-1>", lambda _e, n=note: self._select_note(n))

    def _select_note(self, note: Note) -> None:
        self._selected = note
        self._title_entry.delete(0, "end")
        self._title_entry.insert(0, note.title)
        self._tags_entry.delete(0, "end")
        self._tags_entry.insert(0, ", ".join(note.tags))
        self._body_box.delete("1.0", "end")
        self._body_box.insert("1.0", note.body)
        if note.is_private:
            self._private_switch.select()
        else:
            self._private_switch.deselect()
        self._set_status(f"Editing '{note.title}' (Save updates this note)")

    def _new_note(self) -> None:
        self._selected = None
        self._title_entry.delete(0, "end")
        self._tags_entry.delete(0, "end")
        self._body_box.delete("1.0", "end")
        self._private_switch.deselect()
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

        if self._selected is None:
            result = self._controller.create_note(
                title=title, body=body, is_private=switch_private, tags_csv=tags_csv
            )
        else:
            result = self._controller.update_note(
                self._selected.id, title=title, body=body, tags_csv=tags_csv
            )
            if result.ok and switch_private != self._selected.is_private:
                toggle = self._controller.set_private(self._selected.id, switch_private)
                if not toggle.ok:
                    result = toggle
        self._set_status(result.message)
        if result.ok:
            self._new_note()
            self.refresh_notes_list()

    def _delete_note(self) -> None:
        if self._selected is None:
            self._set_status("Select a note to delete")
            return
        result = self._controller.delete_note(self._selected.id)
        self._set_status(result.message)
        if result.ok:
            self._new_note()
            self.refresh_notes_list()

    def _set_status(self, text: str) -> None:
        self._status.configure(text=text)
        if hasattr(self, "_key_indicator"):
            self._key_indicator.configure(
                text="[ unlocked ]" if self._controller.has_privacy_key else "[ no passphrase set ]"
            )

    def _ensure_passphrase(self) -> bool:
        """Lazy passphrase setup the first time a private note is saved."""
        store = passphrase_store()
        if store.exists():
            for _ in range(3):
                value = prompt_unlock(self)
                if value is None:
                    return False
                try:
                    self._controller.set_privacy_service(store.unlock(value))
                    self._key_source = "passphrase (PBKDF2)"
                    return True
                except PersistenceError:
                    continue
            return False
        value = prompt_setup(self)
        if value is None:
            return False
        try:
            self._controller.set_privacy_service(store.initialize(value))
            self._key_source = "passphrase (PBKDF2)"
            return True
        except (PersistenceError, ValidationError) as exc:
            self._set_status(str(exc))
            return False

    # ---- dialogs ---------------------------------------------------------
    def _open_settings(self) -> None:
        win = ctk.CTkToplevel(self)
        win.title("Settings")
        win.geometry("460x230")
        win.transient(self)
        from astranotes.config import resolve_data_dir

        ctk.CTkLabel(
            win, text="Settings", font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=16, pady=(16, 8))
        ctk.CTkLabel(win, text=f"Data directory: {resolve_data_dir()}").pack(
            anchor="w", padx=16, pady=4
        )
        ctk.CTkLabel(win, text=f"Privacy key: {self._key_source}").pack(
            anchor="w", padx=16, pady=4
        )
        ctk.CTkLabel(
            win,
            text="Profile screen intentionally omitted - AstraNotes is\n"
            "single-user; no accounts are part of the requirements.",
            text_color="gray",
            justify="left",
        ).pack(anchor="w", padx=16, pady=8)

    def _open_about(self) -> None:
        win = ctk.CTkToplevel(self)
        win.title("About")
        win.geometry("420x210")
        win.transient(self)
        ctk.CTkLabel(
            win, text="AstraNotes 0.3.0", font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=16, pady=(16, 8))
        ctk.CTkLabel(
            win,
            text="Local-first, single-user secure note app.\n"
            "3-tier: CustomTkinter view -> NoteManager -> JSON store.\n"
            "Course: CSEN 296B-2 (Spring 2026).\n"
            "Private notes use Fernet encryption (SPR-01).",
            justify="left",
        ).pack(anchor="w", padx=16, pady=4)

    def _toggle_theme(self) -> None:
        ctk.set_appearance_mode(
            "light" if ctk.get_appearance_mode() == "Dark" else "dark"
        )


def main() -> None:
    """Launch the GUI with the right key-source story (ADR-005).

    Precedence:
      1. ASTRANOTES_KEY env var (legacy / CI / tests) - no prompt.
      2. Existing passphrase.json - prompt for unlock at launch.
      3. Neither - launch unlocked; first private note triggers setup.
    """
    if os.environ.get("ASTRANOTES_KEY"):
        controller, key_source = build_default_controller()
        AstraNotesApp(controller, key_source).mainloop()
        return

    store = passphrase_store()
    if store.exists():
        # Create a hidden root just for the dialog, then build the real window.
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

    # No env var, no passphrase set yet - launch unlocked.
    controller, key_source = build_default_controller(
        privacy=None, key_source="no passphrase (set on first private note)"
    )
    AstraNotesApp(controller, key_source).mainloop()


if __name__ == "__main__":
    main()

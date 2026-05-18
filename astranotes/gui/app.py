"""CustomTkinter view - the AstraNotes presentation tier (3-tier frontend).

This is a thin shell. Every user action delegates to NotesController, which
holds the only reference to the logic tier. No business rule, no encryption,
no file path lives in this file - that is what keeps the tiers separate
(NFR-02) and the controller headlessly testable.
"""

from __future__ import annotations

import customtkinter as ctk

from astranotes.gui.controller import NotesController, build_default_controller
from astranotes.models.note import Note

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class AstraNotesApp(ctk.CTk):
    def __init__(self, controller: NotesController, key_source: str) -> None:
        super().__init__()
        self._controller = controller
        self._key_source = key_source
        self._selected: Note | None = None

        self.title("AstraNotes")
        self.geometry("1000x640")
        self.minsize(820, 520)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_sidebar()
        self._build_editor()
        self._build_statusbar()
        self.refresh_notes_list()

    # ---- layout ----------------------------------------------------------
    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, height=52, corner_radius=0)
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header,
            text="  AstraNotes",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).grid(row=0, column=0, padx=(12, 0), pady=10, sticky="w")

        actions = ctk.CTkFrame(header, fg_color="transparent")
        actions.grid(row=0, column=2, padx=12, pady=8, sticky="e")
        ctk.CTkButton(actions, text="Settings", width=90, command=self._open_settings).pack(
            side="left", padx=4
        )
        ctk.CTkButton(actions, text="About", width=80, command=self._open_about).pack(
            side="left", padx=4
        )
        ctk.CTkButton(
            actions, text="Toggle Theme", width=110, command=self._toggle_theme
        ).pack(side="left", padx=4)

    def _build_sidebar(self) -> None:
        self._sidebar = ctk.CTkScrollableFrame(self, width=270, label_text="Notes")
        self._sidebar.grid(row=1, column=0, sticky="nsw", padx=(10, 6), pady=10)

    def _build_editor(self) -> None:
        editor = ctk.CTkFrame(self)
        editor.grid(row=1, column=1, sticky="nsew", padx=(6, 10), pady=10)
        editor.grid_columnconfigure(0, weight=1)
        editor.grid_rowconfigure(4, weight=1)

        self._title_entry = ctk.CTkEntry(editor, placeholder_text="Title")
        self._title_entry.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 6))

        self._tags_entry = ctk.CTkEntry(
            editor, placeholder_text="Tags (comma separated, optional)"
        )
        self._tags_entry.grid(row=1, column=0, sticky="ew", padx=12, pady=6)

        self._private_switch = ctk.CTkSwitch(editor, text="Private (encrypt body at rest)")
        self._private_switch.grid(row=2, column=0, sticky="w", padx=12, pady=6)

        ctk.CTkLabel(editor, text="Body").grid(row=3, column=0, sticky="w", padx=12)
        self._body_box = ctk.CTkTextbox(editor, wrap="word")
        self._body_box.grid(row=4, column=0, sticky="nsew", padx=12, pady=6)

        buttons = ctk.CTkFrame(editor, fg_color="transparent")
        buttons.grid(row=5, column=0, sticky="ew", padx=12, pady=(6, 12))
        ctk.CTkButton(buttons, text="New", width=90, command=self._new_note).pack(
            side="left", padx=(0, 6)
        )
        ctk.CTkButton(buttons, text="Save", width=110, command=self._save_note).pack(
            side="left", padx=6
        )
        ctk.CTkButton(
            buttons,
            text="Delete",
            width=100,
            fg_color="#9a0007",
            hover_color="#c1121f",
            command=self._delete_note,
        ).pack(side="left", padx=6)

    def _build_statusbar(self) -> None:
        self._status = ctk.CTkLabel(self, text="Ready", anchor="w", height=24)
        self._status.grid(row=2, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 8))

    # ---- behavior (delegates to the controller) --------------------------
    def refresh_notes_list(self) -> None:
        for child in self._sidebar.winfo_children():
            child.destroy()
        notes = self._controller.list_notes()
        if not notes:
            ctk.CTkLabel(self._sidebar, text="No notes yet.", text_color="gray").pack(
                pady=12
            )
            return
        for note in notes:
            flag = "[private] " if note.is_private else ""
            label = f"{flag}{note.title}\n{note.modified_at:%Y-%m-%d %H:%M}"
            ctk.CTkButton(
                self._sidebar,
                text=label,
                anchor="w",
                height=46,
                fg_color="transparent",
                hover_color=("#d9d9d9", "#3a3a3a"),
                command=lambda n=note: self._select_note(n),
            ).pack(fill="x", pady=2)

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
        self._set_status(f"Viewing '{note.title}' (Save creates a new note)")

    def _new_note(self) -> None:
        self._selected = None
        self._title_entry.delete(0, "end")
        self._tags_entry.delete(0, "end")
        self._body_box.delete("1.0", "end")
        self._private_switch.deselect()
        self._set_status("New note")

    def _save_note(self) -> None:
        result = self._controller.create_note(
            title=self._title_entry.get(),
            body=self._body_box.get("1.0", "end").rstrip("\n"),
            is_private=bool(self._private_switch.get()),
            tags_csv=self._tags_entry.get(),
        )
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
    controller, key_source = build_default_controller()
    AstraNotesApp(controller, key_source).mainloop()


if __name__ == "__main__":
    main()

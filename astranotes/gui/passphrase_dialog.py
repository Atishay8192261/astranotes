"""CustomTkinter passphrase dialogs for setup and unlock (ADR-005)."""

from __future__ import annotations

from typing import Optional

import customtkinter as ctk


class _PassphraseDialog(ctk.CTkToplevel):
    def __init__(
        self,
        parent: ctk.CTk,
        title: str,
        prompt: str,
        confirm_label: Optional[str] = None,
    ) -> None:
        super().__init__(parent)
        self.title(title)
        self.geometry("420x230")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self._result: Optional[str] = None

        ctk.CTkLabel(
            self, text=prompt, justify="left", wraplength=380
        ).pack(anchor="w", padx=18, pady=(18, 8))

        self._entry = ctk.CTkEntry(self, show="*", width=380, placeholder_text="Passphrase")
        self._entry.pack(padx=18, pady=4)
        self._entry.focus_set()

        self._confirm_entry: Optional[ctk.CTkEntry] = None
        if confirm_label:
            self._confirm_entry = ctk.CTkEntry(
                self, show="*", width=380, placeholder_text=confirm_label
            )
            self._confirm_entry.pack(padx=18, pady=4)

        self._error_label = ctk.CTkLabel(self, text="", text_color="#ff6b6b")
        self._error_label.pack(padx=18, pady=(4, 2))

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(pady=(6, 14))
        ctk.CTkButton(row, text="Cancel", width=120, command=self._cancel).pack(
            side="left", padx=6
        )
        ctk.CTkButton(row, text="OK", width=120, command=self._submit).pack(
            side="left", padx=6
        )
        self.bind("<Return>", lambda _e: self._submit())
        self.bind("<Escape>", lambda _e: self._cancel())
        self.protocol("WM_DELETE_WINDOW", self._cancel)

    def _submit(self) -> None:
        value = self._entry.get()
        if not value:
            self._error_label.configure(text="Passphrase cannot be empty")
            return
        if self._confirm_entry is not None:
            if value != self._confirm_entry.get():
                self._error_label.configure(text="Passphrases do not match")
                return
            if len(value) < 8:
                self._error_label.configure(text="At least 8 characters required")
                return
        self._result = value
        self.destroy()

    def _cancel(self) -> None:
        self._result = None
        self.destroy()

    def ask(self) -> Optional[str]:
        self.wait_window()
        return self._result


def prompt_unlock(parent: ctk.CTk) -> Optional[str]:
    """Ask the user to type their existing passphrase."""
    return _PassphraseDialog(
        parent,
        title="Unlock AstraNotes",
        prompt=(
            "Enter your passphrase to unlock your private notes.\n"
            "This passphrase derives the encryption key in memory only;\n"
            "it is never stored on disk."
        ),
    ).ask()


def prompt_setup(parent: ctk.CTk) -> Optional[str]:
    """Ask the user to set a new passphrase (with confirm)."""
    return _PassphraseDialog(
        parent,
        title="Set passphrase",
        prompt=(
            "Choose a passphrase for your private notes. The encryption key\n"
            "is derived from this passphrase via PBKDF2 (600k iterations) and\n"
            "kept only in memory. If you forget it, your private notes\n"
            "cannot be recovered (no backdoor, by design)."
        ),
        confirm_label="Confirm passphrase",
    ).ask()

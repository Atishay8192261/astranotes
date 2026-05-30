"""Passphrase-derived Fernet key store (ADR-005 resolution).

Resolves SPR-01's "key NEVER in source code or data directory" by deriving
the Fernet key from a user-supplied passphrase via PBKDF2-HMAC-SHA256. Only
a random salt and a small Fernet verifier blob are persisted; the key itself
lives in memory and dies with the process.

Why not the env var alone: ASTRANOTES_KEY is still supported as an override
for tests and CI, but it requires the user to manage a 32-byte base64 string.
A passphrase is the standard UX (Obsidian, Bitwarden, Standard Notes).
"""

from __future__ import annotations

import base64
import json
import os
import secrets
from dataclasses import dataclass
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from astranotes.models.exceptions import PersistenceError, ValidationError
from astranotes.services.privacy import PrivacyService

PBKDF2_ITERATIONS = 600_000
SALT_BYTES = 16
VERIFIER_PLAINTEXT = "astranotes-passphrase-verifier-v1"
MIN_PASSPHRASE_LEN = 8


@dataclass
class PassphraseRecord:
    salt_b64: str
    verifier_b64: str


class PassphraseStore:
    """Manages the salt + verifier file used to derive the Fernet key.

    File layout (one path): {"salt": "<b64>", "verifier": "<fernet-token-b64>"}.
    Salt is non-secret. Verifier is a Fernet-encrypted known plaintext; it
    proves that a typed passphrase derives the same key as the original.
    """

    def __init__(self, path: Path) -> None:
        self._path = Path(path)

    @property
    def path(self) -> Path:
        return self._path

    def exists(self) -> bool:
        return self._path.exists()

    def initialize(self, passphrase: str) -> PrivacyService:
        """Create the salt/verifier file for a brand-new passphrase."""
        self._validate_passphrase(passphrase)
        if self.exists():
            raise PersistenceError("Passphrase already initialized")
        salt = secrets.token_bytes(SALT_BYTES)
        key = _derive_key(passphrase, salt)
        verifier = Fernet(key).encrypt(VERIFIER_PLAINTEXT.encode("utf-8"))
        self._write(
            PassphraseRecord(
                salt_b64=base64.b64encode(salt).decode("ascii"),
                verifier_b64=verifier.decode("ascii"),
            )
        )
        return PrivacyService(key)

    def unlock(self, passphrase: str) -> PrivacyService:
        """Verify the passphrase against the stored verifier; return the service."""
        if not self.exists():
            raise PersistenceError("No passphrase has been set yet")
        rec = self._read()
        salt = base64.b64decode(rec.salt_b64.encode("ascii"))
        key = _derive_key(passphrase, salt)
        try:
            plaintext = Fernet(key).decrypt(rec.verifier_b64.encode("ascii"))
        except InvalidToken as exc:
            raise PersistenceError("Incorrect passphrase") from exc
        if plaintext.decode("utf-8") != VERIFIER_PLAINTEXT:
            raise PersistenceError("Verifier mismatch")
        return PrivacyService(key)

    @staticmethod
    def _validate_passphrase(passphrase: str) -> None:
        if not isinstance(passphrase, str) or len(passphrase) < MIN_PASSPHRASE_LEN:
            raise ValidationError(
                f"Passphrase must be at least {MIN_PASSPHRASE_LEN} characters"
            )

    def _read(self) -> PassphraseRecord:
        try:
            payload = json.loads(self._path.read_text(encoding="utf-8"))
            return PassphraseRecord(
                salt_b64=payload["salt"], verifier_b64=payload["verifier"]
            )
        except (OSError, json.JSONDecodeError, KeyError) as exc:
            raise PersistenceError("Could not read passphrase store") from exc

    def _write(self, record: PassphraseRecord) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self._path.write_text(
                json.dumps({"salt": record.salt_b64, "verifier": record.verifier_b64}),
                encoding="utf-8",
            )
            os.chmod(self._path, 0o600)
        except OSError as exc:
            raise PersistenceError("Could not write passphrase store") from exc


def _derive_key(passphrase: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    raw = kdf.derive(passphrase.encode("utf-8"))
    return base64.urlsafe_b64encode(raw)

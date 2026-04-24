"""PrivacyService: Fernet symmetric encryption for private note bodies (SPR-01, FR-04)."""

from __future__ import annotations

from cryptography.fernet import Fernet, InvalidToken

from astranotes.models.exceptions import PersistenceError


class PrivacyService:
    def __init__(self, key: bytes) -> None:
        self._fernet = Fernet(key)

    @staticmethod
    def generate_key() -> bytes:
        return Fernet.generate_key()

    def encrypt(self, body: str) -> bytes:
        return self._fernet.encrypt(body.encode("utf-8"))

    def decrypt(self, data: bytes) -> str:
        try:
            return self._fernet.decrypt(data).decode("utf-8")
        except InvalidToken as exc:
            raise PersistenceError("Could not decrypt note body") from exc

"""Tests for PrivacyService (SPR-01, FR-04)."""

import pytest
from cryptography.fernet import Fernet

from astranotes.models.exceptions import PersistenceError
from astranotes.services.privacy import PrivacyService

TEST_KEY = b"zmYf3sQ2DRzU7m6gQH3tH4Y9xZc-pHO_8XlPdOe-iIs="  # test-only key


def test_encrypt_decrypt_round_trip():
    service = PrivacyService(TEST_KEY)
    plaintext = "secret diary entry"

    ciphertext = service.encrypt(plaintext)

    assert isinstance(ciphertext, bytes)
    assert ciphertext != plaintext.encode("utf-8")
    assert service.decrypt(ciphertext) == plaintext


def test_decrypt_with_wrong_key_raises_persistence_error():
    encrypted = PrivacyService(TEST_KEY).encrypt("hello")
    other = PrivacyService(Fernet.generate_key())

    with pytest.raises(PersistenceError):
        other.decrypt(encrypted)


def test_generate_key_returns_fernet_compatible_key():
    key = PrivacyService.generate_key()
    service = PrivacyService(key)
    assert service.decrypt(service.encrypt("ok")) == "ok"

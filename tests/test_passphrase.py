"""Tests for the PassphraseStore (ADR-005, SPR-01)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from astranotes.models.exceptions import PersistenceError, ValidationError
from astranotes.services.passphrase import PassphraseStore


@pytest.fixture
def store(tmp_path: Path) -> PassphraseStore:
    return PassphraseStore(tmp_path / "passphrase.json")


def test_initialize_then_unlock_round_trip(store: PassphraseStore) -> None:
    privacy = store.initialize("correct horse battery staple")
    ciphertext = privacy.encrypt("hello")
    again = store.unlock("correct horse battery staple")
    assert again.decrypt(ciphertext) == "hello"


def test_prepare_returns_matching_privacy_and_record(store: PassphraseStore) -> None:
    privacy, record = store.prepare("correct horse battery staple")
    assert privacy.decrypt(privacy.encrypt("hello")) == "hello"
    assert record.salt_b64
    assert record.verifier_b64


def test_unlock_with_wrong_passphrase_raises(store: PassphraseStore) -> None:
    store.initialize("correct horse battery staple")
    with pytest.raises(PersistenceError):
        store.unlock("wrong passphrase here")


def test_initialize_rejects_short_passphrase(store: PassphraseStore) -> None:
    with pytest.raises(ValidationError):
        store.initialize("short")


def test_initialize_twice_raises(store: PassphraseStore) -> None:
    store.initialize("first passphrase here")
    with pytest.raises(PersistenceError):
        store.initialize("second passphrase here")


def test_unlock_before_initialize_raises(store: PassphraseStore) -> None:
    with pytest.raises(PersistenceError):
        store.unlock("anything reasonable")


def test_persisted_file_contains_only_salt_and_verifier(
    store: PassphraseStore, tmp_path: Path
) -> None:
    """SPR-01: nothing key-material-bearing should be in the on-disk file."""
    store.initialize("correct horse battery staple")
    payload = json.loads((tmp_path / "passphrase.json").read_text())
    assert set(payload.keys()) == {"salt", "verifier"}
    # Neither field should equal anything resembling the passphrase plaintext.
    assert "correct" not in payload["salt"]
    assert "correct" not in payload["verifier"]


def test_two_separate_stores_with_same_passphrase_get_different_keys(tmp_path: Path) -> None:
    """Salt randomness: two installs with the same passphrase encrypt differently."""
    a = PassphraseStore(tmp_path / "a.json")
    b = PassphraseStore(tmp_path / "b.json")
    pa = a.initialize("correct horse battery staple")
    pb = b.initialize("correct horse battery staple")
    # Same plaintext, different keys -> ciphertexts must not match.
    assert pa.encrypt("hello") != pb.encrypt("hello")
    # And A's ciphertext should not decrypt under B's key.
    with pytest.raises(PersistenceError):
        pb.decrypt(pa.encrypt("hello"))


def test_tampered_verifier_raises_on_unlock(
    store: PassphraseStore, tmp_path: Path
) -> None:
    store.initialize("correct horse battery staple")
    path = tmp_path / "passphrase.json"
    payload = json.loads(path.read_text())
    payload["verifier"] = payload["verifier"][:-4] + "AAAA"
    path.write_text(json.dumps(payload))
    with pytest.raises(PersistenceError):
        store.unlock("correct horse battery staple")

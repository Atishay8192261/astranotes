"""Runtime configuration shared by every presentation tier (SPR-01).

Resolves the data directory and the Fernet key from the environment so the
GUI, the CLI dev harness, and the tests all agree on where notes live and
which key protects them. The persistent-key strategy is the open SPR-01 ADR;
until then a missing key yields a session-only key.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import NamedTuple

from astranotes.services.privacy import PrivacyService

DEFAULT_DATA_DIR = Path.home() / ".astranotes" / "notes"


class KeyResolution(NamedTuple):
    privacy: PrivacyService
    source: str
    is_session_only: bool


def resolve_data_dir() -> Path:
    raw = os.environ.get("ASTRANOTES_DATA_DIR")
    return Path(raw).expanduser() if raw else DEFAULT_DATA_DIR


def resolve_privacy() -> KeyResolution:
    raw = os.environ.get("ASTRANOTES_KEY")
    if raw:
        return KeyResolution(PrivacyService(raw.encode("utf-8")), "ASTRANOTES_KEY", False)
    return KeyResolution(
        PrivacyService(PrivacyService.generate_key()),
        "dev key (session only)",
        True,
    )

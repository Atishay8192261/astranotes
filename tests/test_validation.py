"""Tests for ValidationLayer (FR-01)."""

import pytest

from astranotes.models.exceptions import ValidationError
from astranotes.models.note import Note
from astranotes.services.validation import ValidationLayer


@pytest.fixture
def validator():
    return ValidationLayer()


def test_valid_title_passes(validator):
    validator.validate(Note(title="Hello"))


def test_empty_title_raises(validator):
    with pytest.raises(ValidationError):
        validator.validate(Note(title=""))


def test_whitespace_only_title_raises(validator):
    with pytest.raises(ValidationError):
        validator.validate(Note(title="   \t\n "))


def test_non_string_title_raises(validator):
    with pytest.raises(ValidationError):
        validator.validate(Note(title=None))  # type: ignore[arg-type]

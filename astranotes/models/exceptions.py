"""Domain-level exceptions (SPR-02)."""


class AstraNotesError(Exception):
    """Base class for all AstraNotes domain errors."""


class NoteNotFoundError(AstraNotesError):
    """Raised when a note cannot be located by id."""


class PersistenceError(AstraNotesError):
    """Raised when a storage operation fails."""


class ValidationError(AstraNotesError):
    """Raised when a note fails validation rules."""

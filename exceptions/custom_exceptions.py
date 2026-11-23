"""Custom exceptions for the Public School Library Management System.

All exceptions derive from PSLMSError so the CLI can catch every
domain-level problem with one handler while still letting programming
errors (TypeError, etc.) surface during development.
"""


class PSLMSError(Exception):
    """Base class for every expected, recoverable PSLMS error."""


class ItemUnavailableError(PSLMSError):
    """Raised when no copy of an item is available to lend."""


class BorrowLimitExceededError(PSLMSError):
    """Raised when a member already holds the maximum number of loans."""


class NonCirculatingItemError(PSLMSError):
    """Raised when someone tries to borrow an in-library-use-only item."""


class BorrowingSuspendedError(PSLMSError):
    """Raised when a suspended member tries to borrow."""


class InvalidReturnStateError(PSLMSError):
    """Raised when a return/close operation is illegal for the current state
    (e.g. returning a loan twice, or returning more copies than are owned)."""


class RecordNotFoundError(PSLMSError):
    """Raised when a member, item or loan ID does not exist."""


class DuplicateRecordError(PSLMSError):
    """Raised when adding a record whose ID already exists."""


class ItemInUseError(PSLMSError):
    """Raised when retiring an item that still has active loans."""


class DataCorruptionError(PSLMSError):
    """Raised when a data file is unreadable or inconsistent."""

"""Domain-specific exceptions for PSLMS."""
from .custom_exceptions import (
    PSLMSError, ItemUnavailableError, BorrowLimitExceededError,
    NonCirculatingItemError, BorrowingSuspendedError, InvalidReturnStateError,
    RecordNotFoundError, DuplicateRecordError, ItemInUseError, DataCorruptionError,
)

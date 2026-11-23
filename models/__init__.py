"""Domain model package."""
from .library_item import LibraryItem, Storybook, Textbook, ReferenceMaterial, VALID_CONDITIONS
from .member import Member, Learner, Teacher
from .loan_record import LoanRecord, LoanStatus
from .library import Library

ITEM_TYPES = {cls.__name__: cls for cls in (Storybook, Textbook, ReferenceMaterial)}
MEMBER_TYPES = {cls.__name__: cls for cls in (Learner, Teacher)}


def item_from_dict(data):
    """Rebuild the right LibraryItem subclass from a saved dict."""
    return ITEM_TYPES[data["type"]].from_dict(data)


def member_from_dict(data):
    """Rebuild the right Member subclass from a saved dict."""
    return MEMBER_TYPES[data["type"]].from_dict(data)

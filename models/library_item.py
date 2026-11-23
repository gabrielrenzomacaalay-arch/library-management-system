"""Library items: an abstract base class and three concrete item types."""
from abc import ABC, abstractmethod

from exceptions import ItemUnavailableError, InvalidReturnStateError
from models.validation import require_text, require_int

VALID_CONDITIONS = ("New", "Good", "Fair", "Poor")


class LibraryItem(ABC):
    """Abstract catalog entry (one title, possibly with several copies).

    Encapsulation: stock counts are private and can only change through
    checkout_copy / return_copy / write_off_copy, which keep the invariant
    ``0 <= copies_available <= copies_owned``.
    """

    item_type = "Item"

    def __init__(self, item_id, title, author, copies_owned,
                 condition="Good", copies_available=None):
        self._item_id = require_text(item_id, "Item ID")
        self.title = title
        self.author = author
        self.condition = condition
        self._copies_owned = require_int(copies_owned, "Copies owned", minimum=0)
        if copies_available is None:
            copies_available = copies_owned
        self._copies_available = require_int(
            copies_available, "Copies available", minimum=0, maximum=copies_owned)

    # ---- properties (validated) -------------------------------------
    @property
    def item_id(self):
        return self._item_id

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = require_text(value, "Title")

    @property
    def author(self):
        return self._author

    @author.setter
    def author(self, value):
        self._author = require_text(value, "Author")

    @property
    def condition(self):
        return self._condition

    @condition.setter
    def condition(self, value):
        text = require_text(value, "Condition").title()
        if text not in VALID_CONDITIONS:
            raise ValueError(f"Condition must be one of: {', '.join(VALID_CONDITIONS)}.")
        self._condition = text

    @property
    def copies_owned(self):
        return self._copies_owned

    @property
    def copies_available(self):
        return self._copies_available

    # ---- polymorphic behaviour --------------------------------------
    @abstractmethod
    def is_circulating(self):
        """True if the item may leave the library."""

    @abstractmethod
    def _extra_fields(self):
        """Subclass-specific attributes for serialisation."""

    # ---- stock operations -------------------------------------------
    def is_available(self):
        return self._copies_available > 0

    def checkout_copy(self):
        if self._copies_available == 0:
            raise ItemUnavailableError(f"No copies of '{self.title}' are available.")
        self._copies_available -= 1

    def return_copy(self):
        if self._copies_available >= self._copies_owned:
            raise InvalidReturnStateError(
                f"All copies of '{self.title}' are already in the library.")
        self._copies_available += 1

    def write_off_copy(self):
        """Permanently remove a copy that is out on loan (lost book)."""
        if self._copies_owned - self._copies_available < 1:
            raise InvalidReturnStateError(f"No copy of '{self.title}' is out on loan.")
        self._copies_owned -= 1
        assert 0 <= self._copies_available <= self._copies_owned

    # ---- persistence ------------------------------------------------
    def to_dict(self):
        data = {
            "type": type(self).__name__,
            "item_id": self._item_id,
            "title": self._title,
            "author": self._author,
            "copies_owned": self._copies_owned,
            "copies_available": self._copies_available,
            "condition": self._condition,
        }
        data.update(self._extra_fields())
        return data

    def __str__(self):
        return f"{self.item_id} {self.title} by {self.author} ({self.item_type})"


class Storybook(LibraryItem):
    item_type = "Storybook"

    def __init__(self, item_id, title, author, copies_owned, reading_level,
                 condition="Good", copies_available=None):
        super().__init__(item_id, title, author, copies_owned, condition, copies_available)
        self.reading_level = reading_level

    @property
    def reading_level(self):
        return self._reading_level

    @reading_level.setter
    def reading_level(self, value):
        self._reading_level = require_text(value, "Reading level")

    def is_circulating(self):
        return True

    def _extra_fields(self):
        return {"reading_level": self._reading_level}

    @classmethod
    def from_dict(cls, d):
        return cls(d["item_id"], d["title"], d["author"], d["copies_owned"],
                   d["reading_level"], d["condition"], d["copies_available"])


class Textbook(LibraryItem):
    item_type = "Textbook"

    def __init__(self, item_id, title, author, copies_owned, subject, grade_level,
                 condition="Good", copies_available=None):
        super().__init__(item_id, title, author, copies_owned, condition, copies_available)
        self.subject = subject
        self.grade_level = grade_level

    @property
    def subject(self):
        return self._subject

    @subject.setter
    def subject(self, value):
        self._subject = require_text(value, "Subject")

    @property
    def grade_level(self):
        return self._grade_level

    @grade_level.setter
    def grade_level(self, value):
        self._grade_level = require_int(value, "Grade level", 1, 12)

    def is_circulating(self):
        return True

    def _extra_fields(self):
        return {"subject": self._subject, "grade_level": self._grade_level}

    @classmethod
    def from_dict(cls, d):
        return cls(d["item_id"], d["title"], d["author"], d["copies_owned"],
                   d["subject"], d["grade_level"], d["condition"], d["copies_available"])


class ReferenceMaterial(LibraryItem):
    """Encyclopedias, dictionaries, atlases: in-library use only."""
    item_type = "Reference"

    def __init__(self, item_id, title, author, copies_owned, edition,
                 condition="Good", copies_available=None):
        super().__init__(item_id, title, author, copies_owned, condition, copies_available)
        self.edition = edition

    @property
    def edition(self):
        return self._edition

    @edition.setter
    def edition(self, value):
        self._edition = require_text(value, "Edition")

    def is_circulating(self):
        return False

    def _extra_fields(self):
        return {"edition": self._edition}

    @classmethod
    def from_dict(cls, d):
        return cls(d["item_id"], d["title"], d["author"], d["copies_owned"],
                   d["edition"], d["condition"], d["copies_available"])

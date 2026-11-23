"""LoanRecord: one borrowing transaction linking a Member and a LibraryItem."""
from datetime import date
from enum import Enum

from exceptions import InvalidReturnStateError
from models.validation import require_text, require_date


class LoanStatus(Enum):
    ACTIVE = "active"
    RETURNED = "returned"
    LOST = "lost"
    DAMAGED = "damaged"


class LoanRecord:
    def __init__(self, loan_id, member, item, issue_date, due_date,
                 return_date=None, status=LoanStatus.ACTIVE, note=""):
        self._loan_id = require_text(loan_id, "Loan ID")
        if member is None or item is None:
            raise ValueError("A loan needs both a member and an item.")
        self._member = member
        self._item = item
        self._issue_date = require_date(issue_date, "Issue date")
        self._due_date = require_date(due_date, "Due date")
        if self._due_date < self._issue_date:
            raise ValueError("Due date cannot be before the issue date.")
        if return_date is not None:
            require_date(return_date, "Return date")
            if return_date < issue_date:
                raise ValueError("Return date cannot be before the issue date.")
        self._return_date = return_date
        self._status = LoanStatus(status)
        self._note = note or ""
        if (self._status is LoanStatus.ACTIVE) != (return_date is None):
            raise ValueError("Only active loans may lack a return date.")

    @property
    def loan_id(self): return self._loan_id
    @property
    def member(self): return self._member
    @property
    def item(self): return self._item
    @property
    def issue_date(self): return self._issue_date
    @property
    def due_date(self): return self._due_date
    @property
    def return_date(self): return self._return_date
    @property
    def status(self): return self._status
    @property
    def note(self): return self._note

    @property
    def is_active(self):
        return self._status is LoanStatus.ACTIVE

    def is_overdue(self, today=None):
        today = today or date.today()
        return self.is_active and today > self._due_date

    def days_overdue(self, as_of=None):
        """Days past due: measured to the return date if closed, else ``as_of``."""
        reference = self._return_date or as_of or date.today()
        return max(0, (reference - self._due_date).days)

    def close_loan(self, return_date, status=LoanStatus.RETURNED, note=""):
        if not self.is_active:
            raise InvalidReturnStateError(f"Loan {self._loan_id} is already closed.")
        if status is LoanStatus.ACTIVE:
            raise ValueError("Cannot close a loan with ACTIVE status.")
        if return_date < self._issue_date:
            raise ValueError("Return date cannot be before the issue date.")
        self._return_date = return_date
        self._status = status
        self._note = note or ""

    def to_dict(self):
        return {
            "loan_id": self._loan_id,
            "member_id": self._member.member_id,
            "item_id": self._item.item_id,
            "issue_date": self._issue_date.isoformat(),
            "due_date": self._due_date.isoformat(),
            "return_date": self._return_date.isoformat() if self._return_date else None,
            "status": self._status.value,
            "note": self._note,
        }

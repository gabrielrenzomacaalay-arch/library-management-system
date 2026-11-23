"""Library members: abstract Member with Learner and Teacher subclasses."""
from abc import ABC, abstractmethod
from datetime import date, timedelta

from exceptions import BorrowLimitExceededError
from models.validation import require_text, require_int


class Member(ABC):
    """Abstract library member.

    The borrowing *rules* (limit, loan period, overdue penalty) are abstract,
    so each subclass decides them and LoanService never checks member types.
    """

    member_type = "Member"

    def __init__(self, member_id, name, demerit_points=0, suspended_until=None):
        self._member_id = require_text(member_id, "Member ID")
        self.name = name
        self._demerit_points = require_int(demerit_points, "Demerit points", minimum=0)
        if suspended_until is not None and not isinstance(suspended_until, date):
            raise ValueError("Suspension end must be a date.")
        self._suspended_until = suspended_until
        self._active_loans = []          # loan IDs; rebuilt from loans on load

    # ---- properties -------------------------------------------------
    @property
    def member_id(self):
        return self._member_id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = require_text(value, "Name")

    @property
    def demerit_points(self):
        return self._demerit_points

    @property
    def suspended_until(self):
        return self._suspended_until

    @property
    def active_loan_ids(self):
        return tuple(self._active_loans)

    @property
    def active_loan_count(self):
        return len(self._active_loans)

    @property
    @abstractmethod
    def grade_or_dept(self):
        """Human-readable affiliation (grade/section or department)."""

    # ---- polymorphic rules ------------------------------------------
    @abstractmethod
    def get_max_loans(self):
        """Maximum simultaneous loans."""

    @abstractmethod
    def get_loan_period_days(self):
        """Number of days before a loan is due."""

    @abstractmethod
    def apply_overdue_penalty(self, days_overdue, today=None):
        """Apply a non-monetary penalty; return a message ('' if none)."""

    # ---- shared behaviour -------------------------------------------
    def is_suspended(self, today=None):
        today = today or date.today()
        return self._suspended_until is not None and today < self._suspended_until

    def can_borrow_more(self):
        return self.active_loan_count < self.get_max_loans()

    def add_loan(self, loan_id):
        if loan_id in self._active_loans:
            raise ValueError(f"Loan {loan_id} is already recorded for {self.name}.")
        if not self.can_borrow_more():
            raise BorrowLimitExceededError(
                f"{self.name} already has {self.get_max_loans()} active loan(s).")
        self._active_loans.append(loan_id)

    def remove_loan(self, loan_id):
        if loan_id not in self._active_loans:
            raise ValueError(f"Loan {loan_id} is not active for {self.name}.")
        self._active_loans.remove(loan_id)

    def to_dict(self):
        data = {
            "type": type(self).__name__,
            "member_id": self._member_id,
            "name": self._name,
            "demerit_points": self._demerit_points,
            "suspended_until": self._suspended_until.isoformat()
            if self._suspended_until else None,
        }
        data.update(self._extra_fields())
        return data

    @abstractmethod
    def _extra_fields(self):
        """Subclass-specific attributes for serialisation."""

    def __str__(self):
        return f"{self.member_id} {self.name} ({self.member_type}, {self.grade_or_dept})"


class Learner(Member):
    """Student: 2 loans, 7 days, demerit points then temporary suspension."""

    member_type = "Learner"
    MAX_LOANS = 2
    LOAN_DAYS = 7
    DEMERIT_THRESHOLD = 5
    SUSPENSION_DAYS = 7

    def __init__(self, member_id, name, grade_level, section,
                 demerit_points=0, suspended_until=None):
        super().__init__(member_id, name, demerit_points, suspended_until)
        self._grade_level = require_int(grade_level, "Grade level", 1, 12)
        self._section = require_text(section, "Section")

    @property
    def grade_level(self):
        return self._grade_level

    @property
    def section(self):
        return self._section

    @property
    def grade_or_dept(self):
        return f"Grade {self._grade_level} - {self._section}"

    def get_max_loans(self):
        return self.MAX_LOANS

    def get_loan_period_days(self):
        return self.LOAN_DAYS

    def apply_overdue_penalty(self, days_overdue, today=None):
        assert days_overdue >= 0, "days_overdue must never be negative"
        if days_overdue == 0:
            return ""
        today = today or date.today()
        self._demerit_points += days_overdue          # 1 point per overdue day
        message = f"{days_overdue} demerit point(s) added."
        if self._demerit_points >= self.DEMERIT_THRESHOLD:
            self._suspended_until = today + timedelta(days=self.SUSPENSION_DAYS)
            self._demerit_points = 0                  # fresh start after serving
            message += (f" Borrowing suspended until "
                        f"{self._suspended_until.isoformat()}.")
        return message

    def _extra_fields(self):
        return {"grade_level": self._grade_level, "section": self._section}

    @classmethod
    def from_dict(cls, d):
        until = date.fromisoformat(d["suspended_until"]) if d.get("suspended_until") else None
        return cls(d["member_id"], d["name"], d["grade_level"], d["section"],
                   d["demerit_points"], until)


class Teacher(Member):
    """Teacher: 5 loans, 14 days, reminder flags instead of penalties."""

    member_type = "Teacher"
    MAX_LOANS = 5
    LOAN_DAYS = 14

    def __init__(self, member_id, name, department,
                 demerit_points=0, suspended_until=None, reminder_flags=0):
        super().__init__(member_id, name, demerit_points, suspended_until)
        self._department = require_text(department, "Department")
        self._reminder_flags = require_int(reminder_flags, "Reminder flags", minimum=0)

    @property
    def department(self):
        return self._department

    @property
    def reminder_flags(self):
        return self._reminder_flags

    @property
    def grade_or_dept(self):
        return self._department

    def get_max_loans(self):
        return self.MAX_LOANS

    def get_loan_period_days(self):
        return self.LOAN_DAYS

    def apply_overdue_penalty(self, days_overdue, today=None):
        assert days_overdue >= 0, "days_overdue must never be negative"
        if days_overdue == 0:
            return ""
        self._reminder_flags += 1
        return "Reminder flag recorded (no borrowing restriction)."

    def _extra_fields(self):
        return {"department": self._department, "reminder_flags": self._reminder_flags}

    @classmethod
    def from_dict(cls, d):
        until = date.fromisoformat(d["suspended_until"]) if d.get("suspended_until") else None
        return cls(d["member_id"], d["name"], d["department"],
                   d["demerit_points"], until, d.get("reminder_flags", 0))

"""LoanService: the borrowing and return workflow.

The service never asks "is this a Learner or a Teacher?". It relies on the
polymorphic methods of Member and LibraryItem, so adding a new member or
item type requires no change here.
"""
from dataclasses import dataclass
from datetime import date, timedelta

from exceptions import (BorrowLimitExceededError, BorrowingSuspendedError,
                        InvalidReturnStateError, NonCirculatingItemError)
from models import LoanRecord, LoanStatus


@dataclass(frozen=True)
class ReturnResult:
    loan: LoanRecord
    days_overdue: int
    penalty_message: str


class LoanService:
    def __init__(self, library, today_provider=date.today):
        self._library = library
        self._today = today_provider

    # ---- borrowing --------------------------------------------------
    def borrow_item(self, member_id, item_id, on_date=None):
        """Issue an item. All rules are checked *before* any state changes."""
        on_date = on_date or self._today()
        member = self._library.get_member(member_id)
        item = self._library.get_item(item_id)

        if not item.is_circulating():
            raise NonCirculatingItemError(
                f"'{item.title}' is reference material for in-library use only.")
        if member.is_suspended(on_date):
            raise BorrowingSuspendedError(
                f"{member.name} cannot borrow until {member.suspended_until.isoformat()}.")
        if not member.can_borrow_more():
            raise BorrowLimitExceededError(
                f"{member.name} already has {member.get_max_loans()} active loan(s).")

        item.checkout_copy()                      # raises ItemUnavailableError
        try:
            due = on_date + timedelta(days=member.get_loan_period_days())
            loan = LoanRecord(self._library.generate_loan_id(), member, item, on_date, due)
            self._library.add_loan(loan)
        except Exception:
            item.return_copy()                    # roll back stock on any failure
            raise
        return loan

    # ---- returning --------------------------------------------------
    def return_item(self, loan_id, on_date=None, note=""):
        return self._close(loan_id, on_date, LoanStatus.RETURNED, note)

    def report_damaged(self, loan_id, note="", on_date=None):
        return self._close(loan_id, on_date, LoanStatus.DAMAGED, note)

    def report_lost(self, loan_id, note="", on_date=None):
        return self._close(loan_id, on_date, LoanStatus.LOST, note)

    def _close(self, loan_id, on_date, status, note):
        on_date = on_date or self._today()
        loan = self._library.get_loan(loan_id)
        if not loan.is_active:
            raise InvalidReturnStateError(f"Loan {loan_id} was already closed.")

        if status is LoanStatus.LOST:
            loan.item.write_off_copy()            # the copy never comes back
        else:
            loan.item.return_copy()
            if status is LoanStatus.DAMAGED:
                loan.item.condition = "Poor"

        loan.close_loan(on_date, status, note)
        loan.member.remove_loan(loan_id)

        days = loan.days_overdue()
        penalty = ""
        if days > 0 and status is not LoanStatus.LOST:
            penalty = loan.member.apply_overdue_penalty(days, on_date)
        return ReturnResult(loan, days, penalty)

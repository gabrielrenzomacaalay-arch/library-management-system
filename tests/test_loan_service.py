import unittest
from datetime import timedelta

from exceptions import (BorrowLimitExceededError, BorrowingSuspendedError,
                        InvalidReturnStateError, ItemInUseError, ItemUnavailableError,
                        NonCirculatingItemError, RecordNotFoundError, DuplicateRecordError)
from models import LoanStatus, Learner
from tests.helpers import TODAY, make_library, make_service


class TestBorrowing(unittest.TestCase):
    def setUp(self):
        self.lib, self.svc = make_service()

    def test_learner_loan_is_due_in_seven_days(self):
        loan = self.svc.borrow_item("M001", "B001")
        self.assertEqual(loan.due_date, TODAY + timedelta(days=7))
        self.assertEqual(self.lib.get_item("B001").copies_available, 1)
        self.assertEqual(self.lib.get_member("M001").active_loan_count, 1)

    def test_teacher_loan_is_due_in_fourteen_days(self):
        self.assertEqual(self.svc.borrow_item("M002", "B001").due_date,
                         TODAY + timedelta(days=14))

    def test_learner_cannot_exceed_two_loans(self):
        self.svc.borrow_item("M001", "B001")
        self.svc.borrow_item("M001", "B004")
        with self.assertRaises(BorrowLimitExceededError):
            self.svc.borrow_item("M001", "B002")

    def test_teacher_can_hold_five_loans(self):
        for _ in range(5):
            self.svc.borrow_item("M002", "B004")
        with self.assertRaises(BorrowLimitExceededError):
            self.svc.borrow_item("M002", "B001")

    def test_reference_material_is_non_circulating(self):
        with self.assertRaises(NonCirculatingItemError):
            self.svc.borrow_item("M001", "B003")

    def test_unavailable_item_raises(self):
        self.svc.borrow_item("M002", "B002")
        with self.assertRaises(ItemUnavailableError):
            self.svc.borrow_item("M001", "B002")

    def test_suspended_member_cannot_borrow(self):
        self.lib.get_member("M001").apply_overdue_penalty(5, TODAY)
        with self.assertRaises(BorrowingSuspendedError):
            self.svc.borrow_item("M001", "B001")

    def test_unknown_ids_raise_not_found(self):
        with self.assertRaises(RecordNotFoundError):
            self.svc.borrow_item("NOPE", "B001")
        with self.assertRaises(RecordNotFoundError):
            self.svc.borrow_item("M001", "NOPE")

    def test_failed_borrow_leaves_stock_unchanged(self):
        self.svc.borrow_item("M001", "B001")
        self.svc.borrow_item("M001", "B004")
        before = self.lib.get_item("B002").copies_available
        with self.assertRaises(BorrowLimitExceededError):
            self.svc.borrow_item("M001", "B002")
        self.assertEqual(self.lib.get_item("B002").copies_available, before)


class TestReturning(unittest.TestCase):
    def setUp(self):
        self.lib, self.svc = make_service()
        self.loan = self.svc.borrow_item("M001", "B001")

    def test_on_time_return_has_no_penalty(self):
        result = self.svc.return_item(self.loan.loan_id, TODAY + timedelta(days=7))
        self.assertEqual((result.days_overdue, result.penalty_message), (0, ""))
        self.assertEqual(self.lib.get_item("B001").copies_available, 2)
        self.assertEqual(self.lib.get_member("M001").active_loan_count, 0)

    def test_late_return_applies_demerits(self):
        result = self.svc.return_item(self.loan.loan_id, TODAY + timedelta(days=10))
        self.assertEqual(result.days_overdue, 3)
        self.assertEqual(self.lib.get_member("M001").demerit_points, 3)

    def test_late_return_can_trigger_suspension(self):
        self.svc.return_item(self.loan.loan_id, TODAY + timedelta(days=12))
        self.assertTrue(self.lib.get_member("M001").is_suspended(TODAY + timedelta(days=12)))

    def test_returning_twice_raises_invalid_state(self):
        self.svc.return_item(self.loan.loan_id)
        with self.assertRaises(InvalidReturnStateError):
            self.svc.return_item(self.loan.loan_id)

    def test_lost_book_reduces_owned_copies_and_no_penalty(self):
        result = self.svc.report_lost(self.loan.loan_id, "Family will replace",
                                      TODAY + timedelta(days=20))
        self.assertEqual(result.loan.status, LoanStatus.LOST)
        self.assertEqual(self.lib.get_item("B001").copies_owned, 1)
        self.assertEqual(self.lib.get_member("M001").demerit_points, 0)

    def test_damaged_book_is_restocked_as_poor_condition(self):
        self.svc.report_damaged(self.loan.loan_id, "Torn cover")
        item = self.lib.get_item("B001")
        self.assertEqual((item.copies_available, item.condition), (2, "Poor"))

    def test_can_borrow_again_after_return(self):
        self.svc.return_item(self.loan.loan_id)
        self.assertTrue(self.svc.borrow_item("M001", "B001").is_active)


class TestLibraryRegistry(unittest.TestCase):
    def test_duplicate_ids_rejected(self):
        lib = make_library()
        with self.assertRaises(DuplicateRecordError):
            lib.add_member(Learner("M001", "Other", 4, "Z"))

    def test_item_with_active_loan_cannot_be_retired(self):
        lib, svc = make_service()
        svc.borrow_item("M001", "B001")
        with self.assertRaises(ItemInUseError):
            lib.retire_item("B001")

    def test_generated_ids_continue_the_sequence(self):
        lib = make_library()
        self.assertEqual((lib.generate_item_id(), lib.generate_member_id(),
                          lib.generate_loan_id()), ("B005", "M003", "L0001"))


if __name__ == "__main__":
    unittest.main()

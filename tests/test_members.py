import unittest
from datetime import date, timedelta

from exceptions import BorrowLimitExceededError
from models import Member, Learner, Teacher, member_from_dict

TODAY = date(2026, 11, 20)


class TestMembers(unittest.TestCase):
    def test_abstract_member_cannot_be_instantiated(self):
        with self.assertRaises(TypeError):
            Member("M1", "Name")

    def test_polymorphic_borrowing_rules(self):
        learner, teacher = Learner("M1", "A", 5, "X"), Teacher("M2", "B", "Math")
        self.assertEqual((learner.get_max_loans(), learner.get_loan_period_days()), (2, 7))
        self.assertEqual((teacher.get_max_loans(), teacher.get_loan_period_days()), (5, 14))

    def test_invalid_grade_level_rejected(self):
        with self.assertRaises(ValueError):
            Learner("M1", "A", 0, "X")

    def test_empty_name_rejected(self):
        with self.assertRaises(ValueError):
            Teacher("M1", " ", "Math")

    def test_add_loan_enforces_limit_inside_the_class(self):
        learner = Learner("M1", "A", 5, "X")
        learner.add_loan("L1")
        learner.add_loan("L2")
        with self.assertRaises(BorrowLimitExceededError):
            learner.add_loan("L3")

    def test_learner_overdue_adds_one_demerit_per_day(self):
        learner = Learner("M1", "A", 5, "X")
        learner.apply_overdue_penalty(3, TODAY)
        self.assertEqual(learner.demerit_points, 3)
        self.assertFalse(learner.is_suspended(TODAY))

    def test_learner_reaching_threshold_is_suspended_and_points_reset(self):
        learner = Learner("M1", "A", 5, "X")
        message = learner.apply_overdue_penalty(5, TODAY)
        self.assertTrue(learner.is_suspended(TODAY))
        self.assertEqual(learner.demerit_points, 0)
        self.assertIn("suspended", message)

    def test_suspension_expires_after_seven_days(self):
        learner = Learner("M1", "A", 5, "X")
        learner.apply_overdue_penalty(5, TODAY)
        self.assertTrue(learner.is_suspended(TODAY + timedelta(days=6)))
        self.assertFalse(learner.is_suspended(TODAY + timedelta(days=7)))

    def test_teacher_gets_reminder_flag_never_suspension(self):
        teacher = Teacher("M2", "B", "Math")
        teacher.apply_overdue_penalty(30, TODAY)
        self.assertEqual(teacher.reminder_flags, 1)
        self.assertFalse(teacher.is_suspended(TODAY))

    def test_round_trip_preserves_suspension(self):
        learner = Learner("M1", "A", 5, "X")
        learner.apply_overdue_penalty(6, TODAY)
        clone = member_from_dict(learner.to_dict())
        self.assertIsInstance(clone, Learner)
        self.assertEqual(clone.suspended_until, learner.suspended_until)


if __name__ == "__main__":
    unittest.main()

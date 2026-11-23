import json
import os
import tempfile
import unittest
from datetime import timedelta

from exceptions import DataCorruptionError
from services import ReportService
from storage import JsonRepository
from tests.helpers import TODAY, make_library, make_service


class TestJsonRepository(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = self._tmp.name
        self.repo = JsonRepository(self.dir)

    def test_missing_files_give_empty_library(self):
        lib = self.repo.load_all()
        self.assertEqual((lib.items(), lib.members(), lib.loans()), ([], [], []))

    def test_data_survives_save_and_reload(self):
        lib, svc = make_service()
        svc.borrow_item("M001", "B001")
        self.repo.save_all(lib)
        reloaded = JsonRepository(self.dir).load_all()
        self.assertEqual(len(reloaded.items()), 4)
        self.assertEqual(reloaded.get_item("B001").copies_available, 1)

    def test_reload_relinks_active_loans_to_members(self):
        lib, svc = make_service()
        loan = svc.borrow_item("M001", "B001")
        self.repo.save_all(lib)
        reloaded = self.repo.load_all()
        self.assertEqual(reloaded.get_member("M001").active_loan_ids, (loan.loan_id,))
        self.assertIs(reloaded.get_loan(loan.loan_id).member, reloaded.get_member("M001"))

    def test_subclasses_are_restored(self):
        self.repo.save_all(make_library())
        names = {type(i).__name__ for i in self.repo.load_all().items()}
        self.assertEqual(names, {"Storybook", "Textbook", "ReferenceMaterial"})

    def test_corrupted_json_raises_custom_error(self):
        with open(os.path.join(self.dir, "books.json"), "w") as f:
            f.write("{ not valid json")
        with self.assertRaises(DataCorruptionError):
            self.repo.load_all()

    def test_loan_pointing_to_missing_member_is_corruption(self):
        lib, svc = make_service()
        svc.borrow_item("M001", "B001")
        self.repo.save_all(lib)
        path = os.path.join(self.dir, "members.json")
        with open(path, "w") as f:
            json.dump({"version": 1, "records": []}, f)
        with self.assertRaises(DataCorruptionError):
            self.repo.load_all()

    def test_second_save_creates_backup_of_previous_data(self):
        lib = make_library()
        self.repo.save_all(lib)
        self.assertEqual(self.repo.list_backups(), [])      # nothing to back up yet
        self.repo.save_all(lib)
        self.assertEqual(len(self.repo.list_backups()), 1)

    def test_restore_backup_recovers_earlier_state(self):
        lib = make_library()
        self.repo.save_all(lib)
        lib.add_item(type(lib.get_item("B001"))("B099", "New", "X", 1, "Grades 1-3"))
        self.repo.save_all(lib)                              # backup holds 4 items
        self.repo.restore_backup()
        self.assertEqual(len(self.repo.load_all().items()), 4)

    def test_no_temp_files_left_after_save(self):
        self.repo.save_all(make_library())
        self.assertFalse([f for f in os.listdir(self.dir) if f.endswith(".tmp")])


class TestReports(unittest.TestCase):
    def test_overdue_report_sorted_most_overdue_first(self):
        lib, svc = make_service()
        svc.borrow_item("M002", "B001", TODAY - timedelta(days=20))   # due 6 days ago
        svc.borrow_item("M001", "B004", TODAY - timedelta(days=10))   # due 3 days ago
        svc.borrow_item("M001", "B002", TODAY)                        # not overdue
        report = ReportService(lib, lambda: TODAY).overdue_report()
        self.assertEqual([e.days_overdue for e in report], [6, 3])

    def test_inventory_summary_counts_copies(self):
        lib, svc = make_service()
        svc.borrow_item("M001", "B001")
        summary = ReportService(lib, lambda: TODAY).inventory_summary()
        self.assertEqual(summary["copies_owned"], 9)
        self.assertEqual(summary["copies_on_loan"], 1)
        self.assertEqual(summary["titles_by_type"]["Storybook"], 2)


if __name__ == "__main__":
    unittest.main()

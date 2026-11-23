"""Menu-driven CLI. It only talks to services and the Library, never to files."""
from datetime import date

from exceptions import PSLMSError
from models import (Learner, Teacher, Storybook, Textbook, ReferenceMaterial,
                    VALID_CONDITIONS)
from services import LoanService, ReportService
from ui.formatting import format_table
from ui.prompts import ask_text, ask_int, ask_choice, ask_date, confirm


class LibraryApp:
    def __init__(self, library, repository, today_provider=date.today):
        self._library = library
        self._repo = repository
        self._today_provider = today_provider
        self._working_date = None              # demo override (System menu)
        self._loans = LoanService(library, self.today)
        self._reports = ReportService(library, self.today)

    def today(self):
        return self._working_date or self._today_provider()

    # ---- main loop --------------------------------------------------
    def run(self):
        print("=" * 56)
        print("  Public School Library Management System (PSLMS)")
        print("=" * 56)
        self._menu("MAIN MENU", [
            ("Catalog", self._catalog_menu),
            ("Members", self._members_menu),
            ("Borrow / Return", self._loans_menu),
            ("Reports", self._reports_menu),
            ("System (save, backups, date)", self._system_menu),
        ], back_label="Save and exit")
        self._save()
        print("Goodbye! Data saved.")

    def _menu(self, title, options, back_label="Back"):
        while True:
            print(f"\n=== {title} ===  (working date: {self.today().isoformat()})")
            for number, (label, _) in enumerate(options, 1):
                print(f" {number}. {label}")
            print(f" 0. {back_label}")
            choice = ask_int("Choose an option: ", 0, len(options))
            if choice == 0:
                return
            self._run(options[choice - 1][1])

    def _run(self, action):
        """Run one menu action; expected errors become friendly messages."""
        try:
            action()
        except PSLMSError as exc:
            print(f"  [!] {exc}")
        except ValueError as exc:
            print(f"  [!] Invalid data: {exc}")
        except OSError as exc:
            print(f"  [!] File problem: {exc}")

    def _save(self):
        self._repo.save_all(self._library)

    # ---- catalog ----------------------------------------------------
    def _catalog_menu(self):
        self._menu("CATALOG", [
            ("Add item", self._add_item),
            ("List all items", self._list_items),
            ("Search items", self._search_items),
            ("Retire item", self._retire_item),
        ])

    def _add_item(self):
        kind = ask_choice("Item type:", ["Storybook", "Textbook", "Reference Material"])
        item_id = self._library.generate_item_id()
        title = ask_text("Title: ")
        author = ask_text("Author: ")
        copies = ask_int("Copies owned: ", 1)
        condition = ask_choice("Condition:", list(VALID_CONDITIONS))
        if kind == "Storybook":
            item = Storybook(item_id, title, author, copies,
                             ask_text("Reading level (e.g. Grades 1-3): "), condition)
        elif kind == "Textbook":
            subject = ask_text("Subject: ")
            item = Textbook(item_id, title, author, copies, subject,
                            ask_int("Grade level (1-12): ", 1, 12), condition)
        else:
            item = ReferenceMaterial(item_id, title, author, copies,
                                     ask_text("Edition: "), condition)
        self._library.add_item(item)
        self._save()
        print(f"  Added {item}")

    def _print_items(self, items):
        rows = [(i.item_id, i.item_type, i.title, i.author,
                 i.copies_owned, i.copies_available, i.condition,
                 "Yes" if i.is_circulating() else "In-library only") for i in items]
        print(format_table(["ID", "Type", "Title", "Author", "Owned", "Avail",
                            "Condition", "Circulates"], rows))

    def _list_items(self):
        self._print_items(self._library.items())

    def _search_items(self):
        self._print_items(self._library.search_items(ask_text("Search title/author/ID: ")))

    def _retire_item(self):
        item = self._library.get_item(ask_text("Item ID to retire: ").upper())
        if confirm(f"Retire '{item.title}'?"):
            self._library.retire_item(item.item_id)
            self._save()
            print("  Item retired.")

    # ---- members ----------------------------------------------------
    def _members_menu(self):
        self._menu("MEMBERS", [
            ("Register member", self._register_member),
            ("List members", self._list_members),
            ("Member status and loans", self._member_status),
        ])

    def _register_member(self):
        kind = ask_choice("Member type:", ["Learner", "Teacher"])
        member_id = self._library.generate_member_id()
        name = ask_text("Full name: ")
        if kind == "Learner":
            grade = ask_int("Grade level (1-12): ", 1, 12)
            member = Learner(member_id, name, grade, ask_text("Section: "))
        else:
            member = Teacher(member_id, name, ask_text("Department: "))
        self._library.add_member(member)
        self._save()
        print(f"  Registered {member}")

    def _list_members(self):
        today = self.today()
        rows = [(m.member_id, m.member_type, m.name, m.grade_or_dept,
                 f"{m.active_loan_count}/{m.get_max_loans()}", m.demerit_points,
                 "Suspended" if m.is_suspended(today) else "OK")
                for m in self._library.members()]
        print(format_table(["ID", "Type", "Name", "Grade/Dept", "Loans", "Demerits", "Status"], rows))

    def _member_status(self):
        member = self._library.get_member(ask_text("Member ID: ").upper())
        print(f"  {member}")
        print(f"  Loan period: {member.get_loan_period_days()} days, "
              f"limit: {member.get_max_loans()} books")
        if member.is_suspended(self.today()):
            print(f"  SUSPENDED until {member.suspended_until.isoformat()}")
        self._print_loans(self._library.loans_for_member(member.member_id, active_only=True))

    # ---- loans ------------------------------------------------------
    def _loans_menu(self):
        self._menu("BORROW / RETURN", [
            ("Borrow an item", self._borrow),
            ("Return an item", self._return),
            ("Report lost item", self._lost),
            ("Report damaged item", self._damaged),
            ("View active loans", lambda: self._print_loans(self._library.active_loans())),
        ])

    def _print_loans(self, loans):
        today = self.today()
        rows = [(l.loan_id, l.member.name, l.item.title, l.issue_date, l.due_date,
                 f"OVERDUE {l.days_overdue(today)}d" if l.is_overdue(today) else l.status.value)
                for l in loans]
        print(format_table(["Loan", "Member", "Item", "Issued", "Due", "Status"], rows))

    def _borrow(self):
        loan = self._loans.borrow_item(ask_text("Member ID: ").upper(),
                                       ask_text("Item ID: ").upper())
        print(f"  Loan {loan.loan_id} created. '{loan.item.title}' is due "
              f"{loan.due_date.isoformat()}.")
        self._save()

    def _show_result(self, result, verb):
        print(f"  {verb}: '{result.loan.item.title}' from {result.loan.member.name}.")
        if result.days_overdue:
            print(f"  Returned {result.days_overdue} day(s) late. {result.penalty_message}")

    def _return(self):
        result = self._loans.return_item(ask_text("Loan ID: ").upper())
        self._show_result(result, "Returned")
        self._save()

    def _lost(self):
        loan_id = ask_text("Loan ID: ").upper()
        note = ask_text("Replacement note (optional): ", allow_empty=True)
        self._show_result(self._loans.report_lost(loan_id, note), "Recorded as lost")
        self._save()

    def _damaged(self):
        loan_id = ask_text("Loan ID: ").upper()
        note = ask_text("Damage note (optional): ", allow_empty=True)
        self._show_result(self._loans.report_damaged(loan_id, note), "Returned damaged")
        self._save()

    # ---- reports ----------------------------------------------------
    def _reports_menu(self):
        self._menu("REPORTS", [
            ("Overdue books", self._overdue_report),
            ("Inventory summary", self._inventory_report),
            ("Suspended members", self._suspended_report),
        ])

    def _overdue_report(self):
        rows = [(e.loan_id, e.borrower, e.item_title, e.due_date, e.days_overdue)
                for e in self._reports.overdue_report()]
        print(format_table(["Loan", "Borrower", "Item", "Due", "Days overdue"], rows))

    def _inventory_report(self):
        s = self._reports.inventory_summary()
        print(f"  Titles: {s['titles']}   Copies owned: {s['copies_owned']}   "
              f"Available: {s['copies_available']}   On loan: {s['copies_on_loan']}")
        for kind, count in sorted(s["titles_by_type"].items()):
            print(f"    {kind}: {count} title(s)")

    def _suspended_report(self):
        rows = [(m.member_id, m.name, m.suspended_until) for m in self._reports.suspended_members()]
        print(format_table(["ID", "Name", "Suspended until"], rows))

    # ---- system -----------------------------------------------------
    def _system_menu(self):
        self._menu("SYSTEM", [
            ("Save now", self._manual_save),
            ("List backups", lambda: print("\n".join(self._repo.list_backups()) or "  (no backups)")),
            ("Restore latest backup", self._restore),
            ("Set working date (for demos/testing)", self._set_date),
            ("Reset working date to today", self._reset_date),
        ])

    def _manual_save(self):
        self._save()
        print("  Saved (previous files backed up).")

    def _restore(self):
        if confirm("Replace current data with the latest backup? Unsaved changes are lost"):
            name = self._repo.restore_backup()
            self._library = self._repo.load_all()
            self._loans = LoanService(self._library, self.today)
            self._reports = ReportService(self._library, self.today)
            print(f"  Restored backup {name}.")

    def _set_date(self):
        self._working_date = ask_date("New working date (YYYY-MM-DD): ")

    def _reset_date(self):
        self._working_date = None
        print("  Working date reset.")

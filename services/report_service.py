"""ReportService: read-only reports over a Library."""
from collections import Counter
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class OverdueEntry:
    loan_id: str
    borrower: str
    item_title: str
    due_date: date
    days_overdue: int


class ReportService:
    def __init__(self, library, today_provider=date.today):
        self._library = library
        self._today = today_provider

    def overdue_report(self, on_date=None):
        """Overdue active loans, most overdue first."""
        on_date = on_date or self._today()
        entries = [
            OverdueEntry(l.loan_id, f"{l.member.name} ({l.member.member_id})",
                         l.item.title, l.due_date, l.days_overdue(on_date))
            for l in self._library.active_loans() if l.is_overdue(on_date)
        ]
        return sorted(entries, key=lambda e: (-e.days_overdue, e.loan_id))

    def inventory_summary(self):
        items = self._library.items()
        by_type = Counter(i.item_type for i in items)
        owned = sum(i.copies_owned for i in items)
        available = sum(i.copies_available for i in items)
        return {
            "titles": len(items),
            "copies_owned": owned,
            "copies_available": available,
            "copies_on_loan": owned - available,
            "titles_by_type": dict(by_type),
        }

    def suspended_members(self, on_date=None):
        on_date = on_date or self._today()
        return [m for m in self._library.members() if m.is_suspended(on_date)]

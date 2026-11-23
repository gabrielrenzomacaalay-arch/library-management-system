"""Library: the aggregate that owns the catalog, members and loan history."""
from exceptions import (RecordNotFoundError, DuplicateRecordError, ItemInUseError)


class Library:
    """Registry of items, members and loans.

    * Library *aggregates* LibraryItems and Members (they are independent
      concepts that the library merely keeps track of).
    * Library *composes* LoanRecords: a loan has no meaning outside the
      library that issued it, and loans are created and owned here.
    """

    def __init__(self):
        self._items = {}
        self._members = {}
        self._loans = {}

    # ---- items ------------------------------------------------------
    def add_item(self, item):
        if item.item_id in self._items:
            raise DuplicateRecordError(f"Item ID {item.item_id} already exists.")
        self._items[item.item_id] = item

    def get_item(self, item_id):
        try:
            return self._items[item_id]
        except KeyError:
            raise RecordNotFoundError(f"No item with ID {item_id}.") from None

    def items(self):
        return sorted(self._items.values(), key=lambda i: i.item_id)

    def search_items(self, keyword):
        key = keyword.strip().lower()
        return [i for i in self.items()
                if key in i.title.lower() or key in i.author.lower()
                or key == i.item_id.lower()]

    def retire_item(self, item_id):
        item = self.get_item(item_id)
        if any(l.is_active and l.item.item_id == item_id for l in self._loans.values()):
            raise ItemInUseError(f"'{item.title}' has active loans and cannot be retired.")
        del self._items[item_id]
        return item

    # ---- members ----------------------------------------------------
    def add_member(self, member):
        if member.member_id in self._members:
            raise DuplicateRecordError(f"Member ID {member.member_id} already exists.")
        self._members[member.member_id] = member

    def get_member(self, member_id):
        try:
            return self._members[member_id]
        except KeyError:
            raise RecordNotFoundError(f"No member with ID {member_id}.") from None

    def members(self):
        return sorted(self._members.values(), key=lambda m: m.member_id)

    # ---- loans ------------------------------------------------------
    def add_loan(self, loan):
        """Register a loan; active loans are linked to their member."""
        if loan.loan_id in self._loans:
            raise DuplicateRecordError(f"Loan ID {loan.loan_id} already exists.")
        self.get_member(loan.member.member_id)
        self.get_item(loan.item.item_id)
        if loan.is_active:
            loan.member.add_loan(loan.loan_id)     # may raise before we store
        self._loans[loan.loan_id] = loan

    def get_loan(self, loan_id):
        try:
            return self._loans[loan_id]
        except KeyError:
            raise RecordNotFoundError(f"No loan with ID {loan_id}.") from None

    def loans(self):
        return sorted(self._loans.values(), key=lambda l: l.loan_id)

    def active_loans(self):
        return [l for l in self.loans() if l.is_active]

    def loans_for_member(self, member_id, active_only=False):
        return [l for l in self.loans()
                if l.member.member_id == member_id and (l.is_active or not active_only)]

    # ---- ID generation ----------------------------------------------
    @staticmethod
    def _next_id(prefix, existing, width):
        numbers = [int(k[len(prefix):]) for k in existing
                   if k.startswith(prefix) and k[len(prefix):].isdigit()]
        return f"{prefix}{(max(numbers) + 1 if numbers else 1):0{width}d}"

    def generate_item_id(self):
        return self._next_id("B", self._items, 3)

    def generate_member_id(self):
        return self._next_id("M", self._members, 3)

    def generate_loan_id(self):
        return self._next_id("L", self._loans, 4)

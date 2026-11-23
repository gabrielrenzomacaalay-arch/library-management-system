# PSLMS Technical Documentation

## A. Project Overview
PSLMS is an offline Python CLI application that lets a public-school teacher-librarian catalog books,
register learners and teachers, lend and receive books, and follow up on overdue loans. It was created
because many public school libraries rely on handwritten logbooks and cannot trace missing books.

## B. Problem Definition
Paper logs are incomplete, holdings are not inventoried, cash fines are impractical, and the environment
has unreliable power, no internet, one shared computer and a part-time non-technical librarian.

## C. Users
Learners (borrowers), Teachers (borrowers with extended privileges) and the Teacher-Librarian (the only
person who operates the software).

## D. Functional Requirements
Catalog management · member registration · borrow / return / lost / damaged workflows · automatic
non-monetary penalties · overdue, inventory and suspension reports · automatic saving, backups and restore.
See `USER_STORIES_AND_BACKLOG.md` for stories and acceptance criteria.

## E. System Design
Layered architecture: `main.py → ui → services → models`, with `storage` serialising the models.

| Module | Responsibility |
|---|---|
| `models/library_item.py` | Item state, stock invariants, circulation rule |
| `models/member.py` | Member identity, borrowing rules, penalties |
| `models/loan_record.py` | One loan: dates, status, overdue calculation |
| `models/library.py` | Registry/aggregate of items, members, loans; ID generation |
| `services/loan_service.py` | Borrow/return workflows; checks all rules before changing state |
| `services/report_service.py` | Read-only reports |
| `storage/json_repository.py` | JSON read/write, atomic save, backups, restore |
| `ui/` | Menus, validated prompts, table output (no business rules) |

## F. OOP Design
- **Encapsulation** — stock counts (`_copies_available`, `_copies_owned`) change only through
  `checkout_copy/return_copy/write_off_copy`, which protect `0 ≤ available ≤ owned`. Titles, conditions,
  grade levels etc. use validated `@property` setters. `Member.add_loan` enforces the loan limit itself, so
  the rule holds even if a caller skips `LoanService`.
- **Inheritance** — `Storybook/Textbook/ReferenceMaterial → LibraryItem`; `Learner/Teacher → Member`.
- **Polymorphism** — `LoanService` calls `get_max_loans()`, `get_loan_period_days()`, `apply_overdue_penalty()`
  and `is_circulating()` without ever checking an object's type. Adding e.g. a `Volunteer` member requires no
  change to the service.
- **Abstraction** — `LibraryItem` and `Member` are ABCs with `@abstractmethod`; they cannot be instantiated
  (tested).
- **Composition / Aggregation / Association** — Library composes LoanRecords; aggregates Items and Members;
  LoanRecord associates with one Member and one Item (see `UML.md`).

## G. Persistence
Three files in `data/`: `books.json`, `members.json`, `loans.json`, each `{"version": 1, "records": [...]}`.
Loans store `member_id`/`item_id`; on load the repository resolves them back into objects and re-links
active loans to members (active-loan lists are *not* stored, so there is a single source of truth).
Saving: backup existing files → write temp file → `fsync` → `os.replace` (atomic). Last 20 backups kept.

## H. Exception Handling
| Exception | Raised when | Handled in |
|---|---|---|
| `ItemUnavailableError` | no copy available | `LibraryApp._run` |
| `BorrowLimitExceededError` | member at loan limit | `LibraryApp._run` |
| `NonCirculatingItemError` | borrowing reference material | `LibraryApp._run` |
| `BorrowingSuspendedError` | suspended member borrows | `LibraryApp._run` |
| `InvalidReturnStateError` | double return / impossible stock state | `LibraryApp._run` |
| `RecordNotFoundError`, `DuplicateRecordError`, `ItemInUseError` | bad/duplicate IDs, retiring borrowed item | `LibraryApp._run` |
| `DataCorruptionError` | unreadable/inconsistent files | `main.load_library` (offers restore) |

Validation layers: prompt helpers (type/range) → model setters (`ValueError`) → business rules
(`LoanService`, `Member`, `LibraryItem`). Assertions guard internal invariants only (`days_overdue >= 0`,
`0 <= available <= owned`), never user input.

## I. Testing
`python -m unittest discover -s tests -t . -v` → **57 tests**: item rules (13), member rules (9), borrowing
and returning (17), persistence/backups/reports (11), CLI behaviour (3), etc. Boundaries covered: limits of
2/5 loans, 5-demerit threshold, suspension expiry on day 7, grade 0/12/13, zero available copies, corrupted
JSON, dangling loan references. *Update this section with your own results and test explanations.*

## J. Refactoring
*Team to complete — see `DEBUGGING_LOG.md`.* Design points already present that you can discuss: validation
moved from the CLI into the model classes; `grade_or_dept` replaced by a derived property; borrow flow checks
all rules first and rolls back stock if loan creation fails.

## K. AI Usage
See `AI_USAGE_LOG.md`. AI-assisted code must be reviewed, tested and explainable by every member.

## L. Limitations
CLI only; single user; no renewals/holds/barcodes; members cannot be edited or deleted; no file locking if two
copies of the program run at once.

## M. Future Improvements
Renewals and reservations; member edit/deactivate; CSV import of existing catalog; printable overdue notices;
simple Tkinter front-end; year-end inventory audit report.

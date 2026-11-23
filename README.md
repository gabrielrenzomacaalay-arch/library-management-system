# Public School Library Management System (PSLMS)

## Project Description
PSLMS is an offline, menu-driven Python application for public elementary and high
school libraries that have no cataloging or lending system. It tracks the book
collection, registered learners and teachers, and every loan, so the school always
knows what it owns and who holds which book. Because many learners cannot pay money,
late returns are handled with **non-monetary** penalties (demerit points and temporary
suspension for learners, reminder flags for teachers).

Built for **IT121AL – Computer Programming 2 (Capstone Project)**.

## Features
- Catalog of **Storybooks, Textbooks and Reference Materials** (reference items are in-library use only)
- Member registration for **Learners** (max 2 loans, 7 days) and **Teachers** (max 5 loans, 14 days)
- Borrow, return, lost-book and damaged-book workflows with full rule validation
- Automatic non-monetary overdue penalties (5 demerits ⇒ 7-day suspension for learners)
- Reports: overdue books (most overdue first), inventory summary, suspended members
- Crash-safe JSON storage (atomic writes) with timestamped backups and one-step restore
- Friendly error messages through custom exceptions; the program does not crash on bad input

## Requirements
- Python 3.10 or newer
- No third-party packages (see `requirements.txt`); works fully offline

## Installation
```bash
git clone <your-repository-url>
cd pslms
```

## How to Run
```bash
python seed_data.py     # optional: load sample books, members and loans
python main.py          # start the application
```

## How to Use
1. Choose a menu number and press Enter. `0` goes back / saves and exits.
2. **Catalog → Add item** to register books; **Members → Register member** to add learners/teachers.
3. **Borrow / Return** to issue a book (`Member ID` like `M001`, `Item ID` like `B001`) and to return it (`Loan ID` like `L0001`).
4. **Reports → Overdue books** shows who to follow up with.
5. Data is saved automatically after every change and again on exit.
6. **System → Set working date** lets you simulate a later date to demonstrate overdue loans and penalties.

Sample data (after `python seed_data.py`): members `M001`–`M003` are learners, `M004` is a teacher;
loan `L0001` is overdue by 3 days. No login/credentials are used.

## Project Structure
```
pslms/
├── main.py                 # entry point (load data, start CLI)
├── seed_data.py            # creates sample data
├── models/                 # domain classes
│   ├── library_item.py     #   LibraryItem (ABC), Storybook, Textbook, ReferenceMaterial
│   ├── member.py           #   Member (ABC), Learner, Teacher
│   ├── loan_record.py      #   LoanRecord, LoanStatus
│   ├── library.py          #   Library (aggregate root)
│   └── validation.py       #   reusable validators
├── services/               # business workflows
│   ├── loan_service.py     #   borrow / return / lost / damaged
│   └── report_service.py   #   overdue, inventory, suspended reports
├── storage/json_repository.py   # atomic JSON persistence + backups
├── exceptions/custom_exceptions.py
├── ui/                     # CLI menus, prompts, table formatting
├── tests/                  # 57 unittest cases
├── data/                   # books.json, members.json, loans.json (+ backups/)
└── docs/                   # UML, backlog, technical docs, AI log, debugging log
```
Layering: `main → ui → services → models → (storage serialises models)`.

## Testing
```bash
python -m unittest discover -s tests -t . -v
```
57 automated tests cover normal cases, boundaries, invalid input, custom exceptions,
business rules, persistence round-trips, corrupted data, backups and the CLI.

## AI Usage Disclosure
See `docs/AI_USAGE_LOG.md`. The team must keep this log up to date and be able to explain all code.

## Known Limitations
- Command-line only; no graphical interface
- One computer at a time (no multi-user/network access, no file locking)
- No reservations/holds, barcode scanning or renewals
- Lost-book replacement is recorded as a note only
- Learner and teacher records cannot yet be edited or deleted from the menu

## Authors
Bonquin · Santos · Sta. Ana — IT121AL Capstone (fill in full names and roles).

## Input Validation

The system uses input validation to help ensure that user-provided data follows the expected format and requirements.

Invalid inputs are handled through validation checks and custom exceptions.
# User Stories, Acceptance Criteria and Product Backlog

| ID | Pri | Sprint | Status | User story |
|----|-----|--------|--------|------------|
| US-01 | High | 1 | Done | As a teacher-librarian, I want to add books to a catalog so that the school knows what the library owns. |
| US-02 | High | 1 | Done | As a learner, I want to borrow a book so that I can read and study at home. |
| US-03 | Medium | 1 | Done | As a teacher, I want extended borrowing privileges so I can prepare lessons and class activities. |
| US-04 | Medium | 1 | Done | As a teacher-librarian, I want reference materials protected so that they stay in the library. |
| US-05 | High | 2 | Done | As a teacher-librarian, I want overdue penalties applied automatically without cash fines so that late returns are discouraged fairly. |
| US-06 | High | 2 | Done | As a teacher-librarian, I want a list of overdue books so that I can follow up with borrowers. |
| US-07 | High | 2 | Done | As a teacher-librarian, I want data saved safely with backups so that power loss does not erase records. |
| US-08 | High | 2 | Done | As a developer, I want custom exception handling so that invalid inputs don't crash the CLI. |
| US-09 | Medium | 2 | Done | As a teacher-librarian, I want to register learners and teachers so that I know who may borrow. |
| US-10 | Medium | 2 | Done | As a teacher-librarian, I want to record lost or damaged books so that the catalog stays accurate. |
| US-11 | Low | 2 | Done | As a teacher-librarian, I want to restore a backup so that I can recover from a corrupted file. |

> Update **Status** honestly as your team works. Statuses above reflect this codebase; they are not a record of your sprints.

## Acceptance criteria
**US-01 Add books** — Title, author and condition are required; copies ≥ 1; type is Storybook/Textbook/Reference; ID is unique and auto-generated; saved to `books.json` and visible after restart.

**US-02 Borrow (learner)** — Rejected if member is suspended (`BorrowingSuspendedError`), already holds 2 loans (`BorrowLimitExceededError`), or no copy is available (`ItemUnavailableError`); otherwise a `LoanRecord` is created, stock drops by 1, due date = issue date + 7 days.

**US-03 Teacher privileges** — Teacher may hold 5 active loans; due date = issue date + 14 days.

**US-04 Reference protection** — Borrowing a `ReferenceMaterial` raises `NonCirculatingItemError` with a clear message; stock is unchanged.

**US-05 Overdue penalties** — On return, learners gain 1 demerit per overdue day; reaching 5 suspends borrowing for 7 days and resets points; teachers get a reminder flag and are never suspended; no money is involved.

**US-06 Overdue report** — Lists loan, borrower, item, due date and days overdue, sorted by most overdue first; excludes returned and not-yet-due loans.

**US-07 Safe persistence** — Each save writes via temp file + atomic rename; previous files are copied to `data/backups/<timestamp>/`; no `.tmp` files remain; data reloads after restart.

**US-08 Exception handling** — Unknown IDs, bad numbers, empty fields, double returns and corrupted files show a friendly `[!]` message instead of a traceback.

**US-09 Register members** — Name required; learners need grade 1–12 and section; teachers need department; ID auto-generated and unique.

**US-10 Lost/damaged** — Lost: owned copies −1, no penalty, loan closed as LOST with note. Damaged: copy restocked, item condition set to Poor, loan closed as DAMAGED.

**US-11 Restore backup** — Requires confirmation; replaces live data with the newest backup and reloads it.

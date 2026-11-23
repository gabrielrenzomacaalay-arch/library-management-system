# UML Class Diagram

Render with any Mermaid viewer (GitHub, VS Code "Markdown Preview Mermaid", https://mermaid.live)
or redraw in draw.io/Lucidchart for the formal deliverable.

```mermaid
classDiagram
    direction TB

    class LibraryItem {
        <<abstract>>
        -str _item_id
        -str _title
        -str _author
        -str _condition
        -int _copies_owned
        -int _copies_available
        +is_circulating()* bool
        +is_available() bool
        +checkout_copy()
        +return_copy()
        +write_off_copy()
        +to_dict() dict
    }
    class Storybook { -str reading_level  +is_circulating() bool }
    class Textbook { -str subject  -int grade_level  +is_circulating() bool }
    class ReferenceMaterial { -str edition  +is_circulating() bool }
    LibraryItem <|-- Storybook
    LibraryItem <|-- Textbook
    LibraryItem <|-- ReferenceMaterial

    class Member {
        <<abstract>>
        -str _member_id
        -str _name
        -int _demerit_points
        -date _suspended_until
        -list _active_loans
        +grade_or_dept* str
        +get_max_loans()* int
        +get_loan_period_days()* int
        +apply_overdue_penalty(days, today)* str
        +is_suspended(today) bool
        +can_borrow_more() bool
        +add_loan(loan_id)
        +remove_loan(loan_id)
    }
    class Learner { -int grade_level  -str section  +DEMERIT_THRESHOLD=5 }
    class Teacher { -str department  -int reminder_flags }
    Member <|-- Learner
    Member <|-- Teacher

    class LoanRecord {
        -str _loan_id
        -date _issue_date
        -date _due_date
        -date _return_date
        -LoanStatus _status
        -str _note
        +is_overdue(today) bool
        +days_overdue(as_of) int
        +close_loan(date, status, note)
    }
    class LoanStatus { <<enumeration>> ACTIVE RETURNED LOST DAMAGED }

    class Library {
        -dict _items
        -dict _members
        -dict _loans
        +add_item() +get_item() +search_items() +retire_item()
        +add_member() +get_member()
        +add_loan() +get_loan() +active_loans()
        +generate_item_id() +generate_member_id() +generate_loan_id()
    }

    class LoanService {
        +borrow_item(member_id, item_id)
        +return_item(loan_id)
        +report_lost(loan_id)
        +report_damaged(loan_id)
    }
    class ReportService {
        +overdue_report()
        +inventory_summary()
        +suspended_members()
    }
    class JsonRepository {
        -str _data_dir
        +save_all(library)
        +load_all() Library
        +create_backup()
        +restore_backup()
    }
    class LibraryApp { +run() }

    class PSLMSError { <<exception>> }
    PSLMSError <|-- ItemUnavailableError
    PSLMSError <|-- BorrowLimitExceededError
    PSLMSError <|-- NonCirculatingItemError
    PSLMSError <|-- BorrowingSuspendedError
    PSLMSError <|-- InvalidReturnStateError
    PSLMSError <|-- RecordNotFoundError
    PSLMSError <|-- DuplicateRecordError
    PSLMSError <|-- ItemInUseError
    PSLMSError <|-- DataCorruptionError

    Library "1" o-- "0..*" LibraryItem : aggregates
    Library "1" o-- "0..*" Member : aggregates
    Library "1" *-- "0..*" LoanRecord : composes
    LoanRecord "0..*" --> "1" Member : borrower
    LoanRecord "0..*" --> "1" LibraryItem : item
    LoanRecord --> LoanStatus
    LoanService --> Library
    ReportService --> Library
    JsonRepository ..> Library : saves / loads
    LibraryApp --> LoanService
    LibraryApp --> ReportService
    LibraryApp --> JsonRepository
    LoanService ..> PSLMSError : raises
```

## Relationship justification
| Relationship | Type | Why |
|---|---|---|
| Library → LoanRecord | **Composition** | A loan only has meaning inside the library that issued it; the Library creates and owns every loan. |
| Library → LibraryItem / Member | **Aggregation** | Items and members are independent concepts the library keeps track of. |
| LoanRecord → Member / LibraryItem | **Association** (1 each) | A loan *refers to* a borrower and an item but does not own them; both outlive the loan. |
| Learner/Teacher → Member | **Inheritance** | A learner *is a* member; shared identity/suspension state lives in the base class. |
| Storybook/Textbook/Reference → LibraryItem | **Inheritance** | Each *is a* catalog item sharing ID, title, author and stock handling. |

> **Note vs. the proposal:** the proposal described LoanRecord as "composing" Member and LibraryItem.
> Because a Member does not die when a loan is closed, that relationship is really an *association*,
> and the true composition is **Library → LoanRecord**. Be ready to explain this in the defense.
> `Member.grade_or_dept` is now a derived property (Learner: "Grade 5 - Narra"; Teacher: department)
> instead of a stored field, to avoid duplicating `grade_level`/`section`/`department`.

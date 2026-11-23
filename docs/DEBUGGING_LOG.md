# Debugging and Refactoring Log (brief §25)

Record **at least three real problems** your team encounters, one of which is a design/maintainability improvement.

| # | What was the problem? | How discovered? | Cause | Fix | How verified? |
|---|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |
| 3 (design) | | | | | |

## Discussion starters from this codebase (verify in your own code before using)
- Why does `LoanService.borrow_item` check every rule *before* `checkout_copy()`, and what could go wrong if stock were decremented first? (see `test_failed_borrow_leaves_stock_unchanged`)
- Why are active-loan IDs not stored in `members.json`? (single source of truth, rebuilt in `Library.add_loan`)
- Why is a lost book handled by `write_off_copy()` instead of `return_copy()`?

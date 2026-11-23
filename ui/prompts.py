"""Validated input helpers. Each loops until the user gives acceptable input."""
from datetime import date


def ask_text(prompt, allow_empty=False):
    while True:
        value = input(prompt).strip()
        if value or allow_empty:
            return value
        print("  [!] This field cannot be empty.")


def ask_int(prompt, minimum=None, maximum=None):
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
        except ValueError:
            print("  [!] Please enter a whole number.")
            continue
        if minimum is not None and value < minimum:
            print(f"  [!] Value must be at least {minimum}.")
        elif maximum is not None and value > maximum:
            print(f"  [!] Value must be at most {maximum}.")
        else:
            return value


def ask_choice(prompt, options):
    """Show a numbered list and return the chosen option."""
    print(prompt)
    for number, option in enumerate(options, 1):
        print(f"  {number}. {option}")
    return options[ask_int("  Choice: ", 1, len(options)) - 1]


def ask_date(prompt):
    while True:
        raw = input(prompt).strip()
        try:
            return date.fromisoformat(raw)
        except ValueError:
            print("  [!] Use the format YYYY-MM-DD (e.g. 2026-11-20).")


def confirm(prompt):
    while True:
        answer = input(f"{prompt} [y/n]: ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("  [!] Please answer y or n.")

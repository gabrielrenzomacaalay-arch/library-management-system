"""Small reusable validators used by the domain classes."""
from datetime import date


def require_text(value, label):
    """Return ``value`` stripped; raise ValueError if empty or not a string."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} cannot be empty.")
    return value.strip()


def require_int(value, label, minimum=None, maximum=None):
    """Return ``value`` if it is an int within bounds; otherwise ValueError."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be a whole number.")
    if minimum is not None and value < minimum:
        raise ValueError(f"{label} must be at least {minimum}.")
    if maximum is not None and value > maximum:
        raise ValueError(f"{label} must be at most {maximum}.")
    return value


def require_date(value, label):
    """Return ``value`` if it is a date; otherwise ValueError."""
    if not isinstance(value, date):
        raise ValueError(f"{label} must be a valid date.")
    return value

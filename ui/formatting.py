"""Plain-text table formatting for the CLI."""


def format_table(headers, rows):
    if not rows:
        return "  (nothing to show)"
    table = [[str(c) for c in row] for row in rows]
    widths = [max(len(str(h)), *(len(r[i]) for r in table)) for i, h in enumerate(headers)]
    line = "  ".join("-" * w for w in widths)
    out = ["  ".join(str(h).ljust(w) for h, w in zip(headers, widths)), line]
    out += ["  ".join(c.ljust(w) for c, w in zip(row, widths)) for row in table]
    return "\n".join(out)

"""Plain-text tables: the summary every tool prints, and the board.

`render` lays rows out in left-aligned columns, each as wide as its widest cell, under a header and
a rule of dashes. It prints nothing and knows no tool: a command builds the rows and prints the
result.
"""


def render(rows: list[dict], columns: list[str]) -> str:
    """The rows as a table with the given columns, header and rule first, without a final newline.

    A row is a dict; a column it lacks, or holds None for, is an empty cell. Any other value is
    shown as text with its runs of whitespace (newlines too) collapsed to one space, so a row is
    always one line. The columns are separated by two spaces and no line ends in a space.
    """
    cells = [[_cell(row.get(column)) for column in columns] for row in rows]
    widths = [
        max([len(column), *(len(line[i]) for line in cells)]) for i, column in enumerate(columns)
    ]
    lines = [columns, ["-" * width for width in widths], *cells]
    return "\n".join(_line(line, widths) for line in lines)


def _cell(value: object) -> str:
    return "" if value is None else " ".join(str(value).split())


def _line(cells: list[str], widths: list[int]) -> str:
    return "  ".join(cell.ljust(width) for cell, width in zip(cells, widths, strict=True)).rstrip()

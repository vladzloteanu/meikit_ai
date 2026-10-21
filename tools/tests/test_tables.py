from factory import tables


def test_render_pads_each_column_to_its_widest_cell():
    out = tables.render(
        [{"a": "x", "b": "long value"}, {"a": "longer", "b": "y"}],
        ["a", "b"],
    )
    assert out.splitlines() == [
        "a       b",
        "------  ----------",
        "x       long value",
        "longer  y",
    ]


def test_render_widens_a_column_to_its_header():
    out = tables.render([{"name": "x"}], ["name", "n"])
    assert out.splitlines() == ["name  n", "----  -", "x"]


def test_render_cells_are_text_on_one_line():
    rows = [{"a": None, "b": 1.5}, {"a": "two\nlines\t here", "extra": "not a column"}]
    out = tables.render(rows, ["a", "b"])
    assert out.splitlines() == [
        "a               b",
        "--------------  ---",
        "                1.5",
        "two lines here",
    ]


def test_render_follows_the_order_of_the_columns_it_is_given():
    out = tables.render([{"a": "1", "b": "2"}], ["b", "a"])
    assert out.splitlines()[0] == "b  a"
    assert out.splitlines()[2] == "2  1"


def test_render_without_rows_is_the_header_and_its_rule():
    assert tables.render([], ["slug", "status"]).splitlines() == ["slug  status", "----  ------"]


def test_render_leaves_no_trailing_spaces():
    out = tables.render([{"a": "x", "b": ""}, {"a": "yy", "b": "z"}], ["a", "b"])
    assert all(line == line.rstrip() for line in out.splitlines())

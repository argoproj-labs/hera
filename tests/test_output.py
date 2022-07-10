from hera import Output, OutputPathParameter


def test_output_returns_default_expected_spec():
    o = Output("o", default="d")
    assert o.name == "o"
    assert o.default == "d"

    s = o.get_spec()
    assert s.name == "o"
    assert s.default == "d"


def test_output_parameter_returns_expected_spec():
    o = OutputPathParameter("o", "/test.txt", default="d")
    assert o.name == "o"
    assert o.path == "/test.txt"
    assert o.default == "d"

    s = o.get_spec()
    assert s.name == "o"
    assert s.value_from.default == "d"
    assert s.value_from.path == "/test.txt"

    o = OutputPathParameter("o", "/test.txt")
    assert o.name == "o"
    assert o.path == "/test.txt"
    assert o.default is None

    s = o.get_spec()
    assert s.name == "o"
    assert not hasattr(s.value_from, "default")
    assert s.value_from.path == "/test.txt"

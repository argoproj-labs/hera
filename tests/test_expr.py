import pytest

from hera.expr import B, C, I


@pytest.mark.parametrize(
    "expr,value",
    [
        (C(1), "1"),
        (C("test"), "'test'"),
        (C({"test": 1}), """{'test': 1}"""),
        (C(1) + C(2) * C(3) / C(4), "1 + 2 * 3 / 4"),
        (C(1) >= C(2), "1 >= 2"),
        (C(1) >= 2, "1 >= 2"),
        (C(1) * 2 + 2, "1 * 2 + 2"),
        ((C(1) >= C(2)) & (C(2) < C(3)), "1 >= 2 and 2 < 3"),
        (B(C(1) >= C(2)) & B(C(2) < C(3)), "(1 >= 2) and (2 < 3)"),
        (C([1, 2, 3])[2], "[1, 2, 3][2]"),
        (I("test")[2], "test[2]"),
        (I("test")['as'], "test['as']"),
        (I("test").attr, "test.attr"),
        (I("test").length(), "len(test)"),
        (I("test").length() > 2, "len(test) > 2"),
        (I("test")[I("test").length() - 1], "test[len(test) - 1]"),
    ],
)
def test_expr(expr, value):
    assert str(expr) == value

import pytest
from jsonpath_ng import Fields, Slice

from hera.expr import C, P, g, it, sprig


@pytest.mark.parametrize(
    "expr,value",
    [
        (C(1), "1"),
        (C(None), "nil"),
        (C(True), "true"),
        (C(False), "false"),
        (C(range(1, 10)), "1..9"),
        (g.test[1:9], "test[1:9]"),
        (g.test[1:], "test[1:]"),
        (g.test[:], "test[:]"),
        (g.test[:9], "test[:9]"),
        (g.test[0:9], "test[0:9]"),
        (g.x**2 + g.y, "x ** 2 + y"),
        (-g.y, "-y"),
        (+g.y, "+y"),
        (~g.y, "!y"),
        (sprig.trim("c"), "sprig.trim('c')"),
        (sprig.add(g.test.length(), 1), "sprig.add(len(test), 1)"),
        (g.test.check(g.test1, g.test2), "test ? test1 : test2"),
        (g.get("check").get("check"), "check.check"),
        (C("test"), "'test'"),
        (C({"test": 1}), """{'test': 1}"""),
        (C({"test": None}), """{'test': nil}"""),
        (
            C({"test": 'None is "None"', None: {None: {False: {True: [None, {True: [False, None]}]}}}}),
            """{'test': 'None is "None"', nil: {nil: {false: {true: [nil, {true: [false, nil]}]}}}}""",
        ),
        (C(1) + C(2) * C(3) / C(4), "1 + 2 * 3 / 4"),
        (C(1) >= C(2), "1 >= 2"),
        (C(1).not_in([1, 2, 3]), "1 not in [1, 2, 3]"),
        (C(1).in_([1, 2, 3]), "1 in [1, 2, 3]"),
        (C("has").contains("as"), "'has' contains 'as'"),
        (C("has").matches(".*"), "'has' matches '.*'"),
        (C("has").starts_with("h"), "'has' startsWith 'h'"),
        (C("has").ends_with("s"), "'has' endsWith 's'"),
        (C(1) >= 2, "1 >= 2"),
        (C(1) * 2 + 2, "1 * 2 + 2"),
        ((C(1) >= C(2)) & (C(2) < C(3)), "1 >= 2 && 2 < 3"),
        (P(C(1) >= C(2)) | P(C(2) < C(3)), "(1 >= 2) || (2 < 3)"),
        (C([1, 2, 3])[2], "[1, 2, 3][2]"),
        (g.test[2], "test[2]"),
        (g.test['as'], "test['as']"),
        (g.test.attr, "test.attr"),
        (g.test.length(), "len(test)"),
        (g.test.length() > 2, "len(test) > 2"),
        (g.test.to_json(), "toJson(test)"),
        (g.test[g.test.length() - 1], "test[len(test) - 1]"),
        (g.test.string(), "string(test)"),
        (g.test.jsonpath(Fields("foo").child("test").child(Slice("*"))), "jsonpath(test, 'foo.test.[*]')"),
        (g.test.jsonpath("test").test.length(), """len(jsonpath(test, 'test').test)"""),
        (g.test.jsonpath("test").test.as_float(), """asFloat(jsonpath(test, 'test').test)"""),
        (g.test.jsonpath("test").test.as_int(), """asInt(jsonpath(test, 'test').test)"""),
        (g.test.map(it + 2), "map(test, {# + 2})"),
        (g.test.map(it.Size + 2), "map(test, {#.Size + 2})"),
        (g.test.filter(P(it["items"].length() + 1) > 0), "filter(test, {(len(#['items']) + 1) > 0})"),
    ],
)
def test_expr(expr, value):
    assert str(expr) == value
    assert f"{expr:}" == value
    assert f"{expr:$}" == "{{" + value + "}}"


def test_raises():
    with pytest.raises(Exception, match="Only ranges with a step size of 1 are allowed"):
        C(range(1, 2, 3))
    with pytest.raises(Exception, match="Only slices with a step size of 1 are allowed"):
        C([1, 2])[1:2:2]
    with pytest.raises(Exception, match="Invalid format spec '!!'. Only allowed value is '.*'"):
        f"{C([1, 2])[1:2]:!!}"

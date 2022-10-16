import hashlib

import pytest

from hera import Env


def test_param_name_sanitization():
    suffix_hash = lambda v: hashlib.md5(v.encode("utf-8")).hexdigest()
    no_change = "no-change"
    no_change_expected = f"{no_change}-{suffix_hash(no_change)}"
    assert no_change_expected == Env._sanitise_param_for_argo(no_change)

    dash_dot_replaced = "this_is.replaced"
    dash_dot_replaced_expected = f"this-is-replaced-{suffix_hash(dash_dot_replaced)}"
    assert dash_dot_replaced_expected == Env._sanitise_param_for_argo(dash_dot_replaced)

    shortened_stripped = "a" * 16 + "(()){{}}" + "_" * 16 + "b" * 32
    shortened_stripped_expected = "a" * 16 + "-" * 16 + "-" + suffix_hash(shortened_stripped)
    assert shortened_stripped_expected == Env._sanitise_param_for_argo(shortened_stripped)

    prefix_collision1 = "aa__"
    prefix_collision2 = "aa.."
    assert Env._sanitise_param_for_argo(prefix_collision1) != Env._sanitise_param_for_argo(prefix_collision2)


def test_env_postinit():
    with pytest.raises(ValueError):
        Env(name="any", value="foo", value_from_input="bar")

from textwrap import dedent
from unittest.mock import patch

import pytest

from hera import _yaml


def test_dump_multiline_string():
    result = _yaml.dump({"args": '\'payload={\n    "text": "example"\n}\''})
    assert result == dedent(
        """\
        args: |-
          'payload={
              "text": "example"
          }'
        """
    )


def test_dump_does_not_wrap_long_strings_by_default():
    result = _yaml.dump(
        {"args": "ref={{= sprig.trunc(7, workflow.parameters.gh-ref) }}, push={{ workflow.parameters.push }}"}
    )
    assert (
        result == "args: ref={{= sprig.trunc(7, workflow.parameters.gh-ref) }}, push={{ workflow.parameters.push }}\n"
    )


@pytest.mark.parametrize(
    "value",
    [
        "y",
        "Y",
        "yes",
        "Yes",
        "YES",
        "on",
        "On",
        "ON",
        "n",
        "N",
        "no",
        "No",
        "NO",
        "off",
        "Off",
        "OFF",
    ],
)
def test_dump_quotes_yaml_1_1_bool_aliases(value):
    result = _yaml.dump({"name": value})

    assert f"name: {value}" not in result.splitlines(), f"Argo/kubectl YAML 1.1 parses unquoted {value!r} as a boolean"
    assert f"name: '{value}'" in result.splitlines()


def test_dump_squashes_multiple_wrapped_expressions_on_one_line():
    result = _yaml._squash_wrapped_expressions(
        dedent(
            """\
            test-case-3: {{some
                brackets}} {{more
                brackets}}
            """
        )
    )
    assert result == "test-case-3: {{some brackets}} {{more brackets}}\n"


def test_dump_squashes_each_wrapped_expression_line_independently():
    result = _yaml._squash_wrapped_expressions(
        dedent(
            """\
            test-case-4: {{some
                brackets}}
                {{more
                brackets}}
            """
        )
    )
    assert result == "test-case-4: {{some brackets}}\n    {{more brackets}}\n"


def test_dump_does_not_modify_block_scalars():
    result = _yaml._squash_wrapped_expressions(
        dedent(
            """\
            description: |
              {{some
              brackets}}
            """
        )
    )
    assert result == dedent(
        """\
        description: |
          {{some
          brackets}}
        """
    )


def test_yaml_missing():
    with patch("hera._yaml._yaml", new=None):
        with pytest.raises(ImportError) as e:
            _yaml.dump({})

    assert "Install `hera[yaml]`" in str(e.value)

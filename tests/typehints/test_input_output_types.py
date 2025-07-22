from textwrap import dedent

import pytest

from hera.shared._pydantic import _PYDANTIC_VERSION

from .mypy_utils import run_mypy

ENABLE_FOR_V2 = pytest.mark.skipif(_PYDANTIC_VERSION < 2, reason="Pydantic v2 compatibility test")


def extract_notes(mypy_output: str) -> list[str]:
    return [line.split("note:")[1].strip() for line in mypy_output.splitlines() if "note:" in line]


@pytest.mark.parametrize(
    "pydantic_version",
    [
        pytest.param(1, id="pydantic_v1"),
        pytest.param(2, marks=[ENABLE_FOR_V2], id="pydantic_v2"),
    ],
)
def test_custom_input_type(pydantic_version: int):
    script = f"""
        from typing import Optional
        from hera.workflows.io.v{pydantic_version} import Input

        class MyInput(Input):
            param_a: str
            param_b: Optional[int] = None

        input = MyInput(param_a="test", param_b=42)
        reveal_type(input.param_a)
        reveal_type(input.param_b)
    """
    notes = extract_notes(run_mypy(dedent(script.strip("\n"))))
    assert notes == [
        'Revealed type is "builtins.str"',
        'Revealed type is "Union[builtins.int, None]"',
    ]


@pytest.mark.parametrize(
    "pydantic_version",
    [
        pytest.param(1, id="pydantic_v1"),
        pytest.param(2, marks=[ENABLE_FOR_V2], id="pydantic_v2"),
    ],
)
def test_custom_output_type(pydantic_version: int):
    script = f"""
        from typing import Optional
        from hera.workflows.io.v{pydantic_version} import Output

        class MyOutput(Output):
            param_a: str
            param_b: Optional[int] = None

        output = MyOutput(param_a="test", param_b=42)
        reveal_type(output.param_a)
        reveal_type(output.param_b)
        reveal_type(output.exit_code)
        reveal_type(output.result)
    """
    notes = extract_notes(run_mypy(dedent(script.strip("\n"))))
    assert notes == [
        'Revealed type is "builtins.str"',
        'Revealed type is "Union[builtins.int, None]"',
        'Revealed type is "builtins.int"',
        'Revealed type is "Any"',
    ]

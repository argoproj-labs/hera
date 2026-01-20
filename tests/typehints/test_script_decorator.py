import dataclasses
from textwrap import dedent
from typing import Iterator, Tuple

import pytest

from hera.workflows import Step, Task

from .mypy_utils import run_mypy

SIMPLE_SCRIPT = """
from hera.workflows import script

@script()
def simple_script(input: str) -> int:
    print(input)
    return len(input)
""".strip()


def test_underlying_function_args_invocation():
    """Verify the underlying implementation of a script can be invoked with positional arguments."""
    STEP_INVOCATION = """
        result = simple_script("Hello World!")
        reveal_type(result)
    """
    result = run_mypy(SIMPLE_SCRIPT + dedent(STEP_INVOCATION))
    assert 'Revealed type is "builtins.int"' in result


def test_underlying_function_kwargs_invocation():
    """Verify the underlying implementation of a script can be invoked with named arguments."""
    STEP_INVOCATION = """
        result = simple_script(input="Hello World!")
        reveal_type(result)
    """
    result = run_mypy(SIMPLE_SCRIPT + dedent(STEP_INVOCATION))
    assert 'Revealed type is "builtins.int"' in result


def test_invocation_with_no_arguments():
    """Verify a script can be invoked with no arguments.

    Without knowing the invocation context, which the type system does not have access to,
    the return type could be None, Step or Task.
    """
    STEP_INVOCATION = """
        result = simple_script()
        reveal_type(result)
    """
    result = run_mypy(SIMPLE_SCRIPT + dedent(STEP_INVOCATION))
    assert 'Revealed type is "Union[hera.workflows.steps.Step, hera.workflows.task.Task, None]"' in result


def test_parameter_named_name():
    """If a script has a 'name' argument, the user function will take precedence over other overloads."""
    INVOCATION = """
        from hera.workflows import script

        @script()
        def simple_script(name: str) -> int:
            return len(name)

        result = simple_script(name="some_step")
        reveal_type(result)
    """
    result = run_mypy(dedent(INVOCATION))
    assert 'Revealed type is "builtins.int"' in result


def step_and_task_parameters() -> Iterator[Tuple[str, str, str]]:
    """Return all parameters on Step, Task or both"""
    # pydantic-v1 syntax:
    step_fields = {field.name for field in dataclasses.fields(Step) if not field.name.startswith("_")}
    task_fields = {field.name for field in dataclasses.fields(Task) if not field.name.startswith("_")}

    for field_name in step_fields | task_fields:
        if field_name not in task_fields:
            yield (field_name, "Step", "hera.workflows.steps.Step")
        elif field_name not in step_fields:
            yield (field_name, "Task", "hera.workflows.task.Task")
        else:
            yield (field_name, "Step", "Union[hera.workflows.steps.Step, hera.workflows.task.Task]")
            yield (field_name, "Task", "Union[hera.workflows.steps.Step, hera.workflows.task.Task]")


@pytest.mark.parametrize(("parameter_name", "input_type", "revealed_type"), tuple(step_and_task_parameters()))
def test_optional_step_and_task_arguments(parameter_name: str, input_type: str, revealed_type: str) -> None:
    """Verify a script can be invoked with any argument that Step and/or Task accept."""
    STEP_INVOCATION = f"""
        from hera.workflows import Step, Task
        def some_function(param: {input_type}) -> None:
            result = simple_script({parameter_name}=param.{parameter_name})
            reveal_type(result)
    """
    result = run_mypy(SIMPLE_SCRIPT + dedent(STEP_INVOCATION))
    assert f'Revealed type is "{revealed_type}"' in result

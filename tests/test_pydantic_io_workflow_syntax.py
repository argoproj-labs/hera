import pytest

from hera.shared._global_config import _CONTEXT_MANAGER_PYDANTIC_IO_FLAG
from hera.workflows import Input, Output, Steps, Workflow, script


class IntInput(Input):
    field: int


class IntOutput(Output):
    field: int


@pytest.fixture(autouse=True)
def enable_pydantic_io(global_config_fixture):
    global_config_fixture.experimental_features[_CONTEXT_MANAGER_PYDANTIC_IO_FLAG] = True


def test_output_field_contains_argo_template(global_config_fixture):
    @script()
    def triple(input: IntInput) -> IntOutput:
        return IntOutput(field=input.field * 3)

    with Workflow(name="foo"):
        with Steps(name="bar"):
            result = triple(IntInput(field=5)).field

    assert result == "{{steps.triple.outputs.parameters.field}}"


def test_script_can_return_none():
    @script()
    def print_field(input: IntInput) -> None:
        print(input.field)

    with Workflow(name="foo"):
        with Steps(name="bar"):
            result = print_field(IntInput(field=5))

    assert result is None


def test_invalid_pydantic_io_outside_of_context():
    @script()
    def triple(input: IntInput) -> IntOutput:
        return IntOutput(field=input.field * 3)

    with Workflow(name="foo"):
        with pytest.raises(SyntaxError, match="Cannot use Pydantic I/O outside of a .* context"):
            triple(IntInput(field=5))


def test_invalid_non_pydantic_return_type():
    @script()
    def triple(input: IntInput) -> int:
        return input.field * 3

    with Workflow(name="foo"):
        with Steps(name="bar"):
            with pytest.raises(SyntaxError, match="Cannot use Pydantic input type without a Pydantic output type"):
                triple(IntInput(field=5))

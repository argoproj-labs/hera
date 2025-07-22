from textwrap import dedent

from .mypy_utils import run_mypy

COMMON_SETUP = """
from hera.shared import global_config
from hera.workflows import Input, Output, Workflow

w = Workflow()

"""


def test_script_decoration_no_arguments():
    """Verify a script can be decorated with no extra arguments."""
    SCRIPT = """
        @w.script()
        def simple_script(_: Input) -> Output:
            return Output()

        reveal_type(simple_script(Input()))
    """
    result = run_mypy(COMMON_SETUP + dedent(SCRIPT))
    assert 'Revealed type is "hera.workflows.io.v2.Output"' in result


def test_script_decoration_accepts_name_argument():
    """Verify the script decorator can be passed a name."""
    SCRIPT = """
        @w.script(name = "some_script")
        def simple_script(_: Input) -> Output:
            return Output()

        reveal_type(simple_script(Input()))
    """
    result = run_mypy(COMMON_SETUP + dedent(SCRIPT))
    assert 'Revealed type is "hera.workflows.io.v2.Output"' in result

from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory
from textwrap import dedent

COMMON_SETUP = """
from hera.shared import global_config
from hera.workflows import Input, Output, Workflow

w = Workflow()

"""


def run_mypy(python_code: str):
    with TemporaryDirectory() as d:
        python_file = Path(d) / "example.py"
        python_file.write_text(python_code)
        mypy_cmd = ["mypy", "--config-file", "tests/typehints/test-mypy.toml", str(python_file)]
        result = run(mypy_cmd, check=False, capture_output=True, encoding="utf-8")
        if result.returncode != 0:
            msg = f"Error calling {' '.join(mypy_cmd)}:\n{result.stderr}{result.stdout}"
            raise AssertionError(msg)
        return result.stdout.replace(d, "")


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

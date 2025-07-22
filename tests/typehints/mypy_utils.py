from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory


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

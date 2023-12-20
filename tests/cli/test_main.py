from unittest.mock import patch

import cappa
import pytest

from hera.__main__ import main


def test_main_dependency_missing():
    with patch("importlib.import_module", side_effect=ModuleNotFoundError):
        with pytest.raises(ModuleNotFoundError) as e:
            main()

    assert "pip install hera[cli]" in str(e.value)


def test_main_dependency_exists(capsys):
    with pytest.raises(cappa.Exit) as e:
        main(["--help"])

    assert e.value.code == 0

    err = capsys.readouterr().err
    assert "CLI is a work-in-progress" in err

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


def test_yaml_missing():
    with patch("hera._yaml._yaml", new=None):
        with pytest.raises(ImportError) as e:
            _yaml.dump({})

    assert "Install `hera[yaml]`" in str(e.value)

from types import ModuleType
from typing import Optional

_yaml: Optional[ModuleType] = None
try:
    import yaml

    _yaml = yaml
except ImportError:
    _yaml = None
else:

    def str_presenter(dumper, data):
        """Configures yaml for dumping multiline strings.

        Ref: https://github.com/yaml/pyyaml/issues/240
        """
        if data.count("\n") > 0:  # check for multiline string
            return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
        return dumper.represent_scalar("tag:yaml.org,2002:str", data)

    _yaml.add_representer(str, str_presenter)
    _yaml.representer.SafeRepresenter.add_representer(str, str_presenter)


def _line_indent(line: str) -> int:
    return len(line) - len(line.lstrip())


def _is_block_scalar(line: str) -> bool:
    stripped = line.rstrip()
    return (
        stripped.endswith(": |")
        or stripped.endswith(": |-")
        or stripped.endswith(": |+")
        or stripped.endswith(": >")
        or stripped.endswith(": >-")
        or stripped.endswith(": >+")
    )


def _squash_wrapped_expressions(yaml_str: str) -> str:
    lines = yaml_str.splitlines()
    if not lines:
        return yaml_str

    squashed = []
    block_scalar_indent = None
    i = 0

    while i < len(lines):
        line = lines[i]

        if block_scalar_indent is not None:
            if line == "" or _line_indent(line) > block_scalar_indent:
                squashed.append(line)
                i += 1
                continue
            block_scalar_indent = None

        if _is_block_scalar(line):
            block_scalar_indent = _line_indent(line)
            squashed.append(line)
            i += 1
            continue

        while line.count("{{") > line.count("}}") and i + 1 < len(lines):
            i += 1
            line += " " + lines[i].lstrip()

        squashed.append(line)
        i += 1

    result = "\n".join(squashed)
    if yaml_str.endswith("\n"):
        result += "\n"
    return result


def dump(*args, **kwargs) -> str:
    """Builds the Workflow as an Argo schema Workflow object and returns it as yaml string."""
    if not _yaml:
        raise ImportError("`PyYAML` is not installed. Install `hera[yaml]` to bring in the extra dependency")

    # Set some default options if not provided by the user
    kwargs.setdefault("default_flow_style", False)
    kwargs.setdefault("sort_keys", False)
    return _squash_wrapped_expressions(_yaml.dump(*args, **kwargs))

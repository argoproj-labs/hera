import re
from types import ModuleType
from typing import Optional

_yaml: Optional[ModuleType] = None
try:
    import yaml

    _yaml = yaml
except ImportError:
    _yaml = None
else:
    # YAML 1.1 (used by Argo/kubectl) parses unquoted y/Y/n/N as booleans, but PyYAML
    # leaves them unquoted on dump. Longer forms (yes, no, on, off, ...) are already
    # quoted by PyYAML; only the single-letter forms need forcing here.
    _YAML_1_1_BOOL_LITERALS = frozenset({"y", "Y", "n", "N"})

    # go-yaml (used by Argo/kubectl) resolves more plain scalars as numbers than PyYAML does:
    # exponents without a dot or a signed exponent (1e3, 1e-5, 1.5e3), signed dot-floats (+.5),
    # 0o/0X prefixes, leading-zero decimals (08) and underscores anywhere (1_0e3). PyYAML leaves
    # these unquoted on dump, so they would change type on the way to Argo. The patterns mirror
    # strconv.ParseInt(s, 0, 64) and go-yaml's yamlStyleFloat, applied after removing underscores.
    _GO_YAML_INT = re.compile(r"[-+]?(?:0[xX][0-9a-fA-F]+|0[oO][0-7]+|0[bB][01]+|0[0-7]*|[1-9][0-9]*)")
    _GO_YAML_FLOAT = re.compile(r"[-+]?(?:\.[0-9]+|[0-9]+(?:\.[0-9]*)?)(?:[eE][-+]?[0-9]+)?")

    def _is_go_yaml_number(data: str) -> bool:
        if not data or data[0] not in "-+.0123456789":
            return False
        plain = data.replace("_", "")
        return bool(_GO_YAML_INT.fullmatch(plain) or _GO_YAML_FLOAT.fullmatch(plain))

    def str_presenter(dumper, data):
        """Represent string scalars so the dumped YAML stays safe for Argo/kubectl.

        - Multiline strings use block scalar style (``|``).
        - Single-letter YAML 1.1 boolean literals (``y``, ``Y``, ``n``, ``N``) are
          single-quoted so Argo/kubectl do not parse them as booleans.
        - Strings that go-yaml would resolve as a number (``1e-5``, ``0o17``, ``08``, ...)
          are single-quoted so Argo/kubectl keep them as strings.

        Refs: https://github.com/yaml/pyyaml/issues/240
              https://github.com/yaml/pyyaml/issues/791
        """
        if data.count("\n") > 0:  # check for multiline string
            return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
        if data in _YAML_1_1_BOOL_LITERALS or _is_go_yaml_number(data):
            return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="'")
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

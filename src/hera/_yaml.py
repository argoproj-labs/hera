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


def dump(*args, **kwargs) -> str:
    """Builds the Workflow as an Argo schema Workflow object and returns it as yaml string."""
    if not _yaml:
        raise ImportError("`PyYAML` is not installed. Install `hera[yaml]` to bring in the extra dependency")

    # Set some default options if not provided by the user
    kwargs.setdefault("default_flow_style", False)
    kwargs.setdefault("sort_keys", False)
    return _yaml.dump(*args, **kwargs)

from argo_workflows.models import (
    ConfigMapKeySelector,
    IoArgoprojWorkflowV1alpha1Cache,
    IoArgoprojWorkflowV1alpha1Memoize,
)


class Memoize:
    """Memoization configuration for task inputs.

    Parameters
    ----------
    key : str
        The input parameter key to use for memoization. This gets turned into {{inputs.parameters.key}}. Generally,
        this can be used with passing functions to `Task`.
    config_map_name : str
        The name of the ConfigMap to use for memoization.
    config_map_key: str
        The key within the ConfigMap used for memoization.
    max_age : str
        The maximum age of the memoized value. This takes the form of `value[unit]`. For example, `1h` is 1 hour and
        `1d` is 1 day.
    """

    def __init__(self, key: str, config_map_name: str, config_map_key: str, max_age: str = "1h"):
        self.key = key
        self.config_map_name = config_map_name
        self.config_map_key = config_map_key
        self.max_age = max_age

    def build(self) -> IoArgoprojWorkflowV1alpha1Memoize:
        return IoArgoprojWorkflowV1alpha1Memoize(
            cache=IoArgoprojWorkflowV1alpha1Cache(
                config_map=ConfigMapKeySelector(name=self.config_map_name, key=self.config_map_key),
            ),
            key=f"{{{{inputs.parameters.{self.key}}}}}",
            max_age=self.max_age,
        )

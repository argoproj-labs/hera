"""
When we use a DAG task's `with_items` field, we typically pass in a list of dictionaries as (str, str). The problem
with the auto-generated `argo_workflows` SDK, however, is that it will attempt to interpret each element in this
list of `with_items` as a non-primitive type, ultimately attempting to convert it to an internal representation,
which, clearly, does not exist. This happens during the call to `argo_workflows.model_utils.model_to_dict()`, which
recursively calls `model_to_dict` on the elements present in `with_items`. Since each element is a primitive `dict`
that does not have the methods necessary for `model_to_dict`, we get SDK exceptions during workflow/task
submission. To overcome this by not modifying the SDK, we can implement our own wrapper around a primitive type
by using `ModelSimple`. The `ParallelSteps` construct, of the SDK, is a wrapper around a primitive `list`/`array`,
and it uses a similar structure. This implementation is very similar to `ParallelSteps` but uses `dict` rather
than internal `str` and `list`.
"""

from typing import Any, Dict, Set

from argo_workflows.model_utils import (
    ApiTypeError,
    ModelSimple,
    cached_property,
    convert_js_args_to_python_args,
)


class _Item(ModelSimple):
    allowed_values: Dict[Any, Any] = {}
    validations: Dict[Any, Any] = {}

    @cached_property
    def openapi_types():  # type: ignore
        """
        This must be a method because a model may have properties that are of type self, this must run
        after the class is loaded.
        """
        return {
            "value": (dict,),
        }

    @cached_property
    def discriminator():  # type: ignore
        """
        Typically returns an internal SDK class that can be used to discriminate between inheriting
        classes, not necessary in this case.
        """
        return None

    attribute_map: Dict[Any, Any] = {}
    read_only_vars: Set[Any] = set()
    _composed_schemas = None
    required_properties = set(
        [
            "_data_store",
            "_check_type",
            "_spec_property_naming",
            "_path_to_item",
            "_configuration",
            "_visited_composed_classes",
        ]
    )

    @convert_js_args_to_python_args
    def __init__(self, *args, **kwargs):
        # required up here when default value is not given
        _path_to_item = kwargs.pop("_path_to_item", ())

        if "value" in kwargs:
            value = kwargs.pop("value")
        elif args:
            args = list(args)  # type: ignore
            value = args.pop(0)  # type: ignore
        else:
            raise ApiTypeError(
                "value is required, but not passed in args or kwargs and doesn't have default",
                path_to_item=_path_to_item,
                valid_classes=(self.__class__,),
            )

        _check_type = kwargs.pop("_check_type", True)
        _spec_property_naming = kwargs.pop("_spec_property_naming", False)
        _configuration = kwargs.pop("_configuration", None)
        _visited_composed_classes = kwargs.pop("_visited_composed_classes", ())

        if args:
            raise ApiTypeError(
                "Invalid positional arguments=%s passed to %s. Remove those invalid positional arguments."
                % (
                    args,
                    self.__class__.__name__,
                ),
                path_to_item=_path_to_item,
                valid_classes=(self.__class__,),
            )

        self._data_store = {}
        self._check_type = _check_type
        self._spec_property_naming = _spec_property_naming
        self._path_to_item = _path_to_item
        self._configuration = _configuration
        self._visited_composed_classes = _visited_composed_classes + (self.__class__,)
        self.value = value
        if kwargs:
            raise ApiTypeError(
                "Invalid named arguments=%s passed to %s. Remove those invalid named arguments."
                % (
                    kwargs,
                    self.__class__.__name__,
                ),
                path_to_item=_path_to_item,
                valid_classes=(self.__class__,),
            )

"""Global config module supports configuring Hera's behavior based on client requirements."""
from __future__ import annotations

import inspect
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union

from pydantic import root_validator

from hera.auth import TokenGenerator

from ._base_model import BaseModel

TBase = TypeVar("TBase", bound="BaseMixin")
TypeTBase = Type[TBase]

Hook = Callable[[TBase], TBase]
"""`Hook` is a callable that takes a Hera objects and returns the same, optionally mutated, object. 

This can be a Workflow, a Script, a Container, etc - any Hera object. 
"""

_HookMap = Dict[Type[TBase], List[Hook]]
"""mapping of Hera object type to the list of mutating hooks to apply to the object"""

_Defaults = Dict[TBase, Dict]
"""mapping of Hera object type to a dictionary of default field/value combinations"""


@dataclass
class _GlobalConfig:
    """Hera global configuration holds any user configuration such as global tokens, hooks, etc.

    Notes:
    -----
    This should not be instantiated directly by the user. There is an instance of the `_GlobalConfig` in this module,
    which is what should be used. Access as `hera.shared.global_config` or `hera.shared.GlobalConfig`.
    """

    # protected attributes are ones that are computed/go through some light processing upon setting or
    # are processed upon accessing. The rest, which use primitive types, such as `str`, can remain public
    _token: Optional[Union[str, TokenGenerator, Callable[[], Optional[str]]]] = None
    """an optional authentication token used by Hera in communicating with the Argo server"""

    _image: Union[str, Callable[[], str]] = "python:3.8"
    """an optional Docker image specification"""

    _pre_build_hooks: Optional[_HookMap] = None
    """any pre build hooks to invoke before Hera builds the objects necessary for communicating with Argo"""

    _defaults: _Defaults = field(default_factory=lambda: defaultdict(dict))
    """any Hera class defaults to use. These can be overriden by users, otherwise assume the specified default"""

    host: Optional[str] = None
    """the host address of the Argo server"""

    verify_ssl: bool = True
    """whether to perform SSL verification on the path towards communicating with the Argo server"""

    api_version: str = "argoproj.io/v1alpha1"
    """the Argo API verison to use on models"""

    namespace: Optional[str] = None
    """the Kubernetes namespace to use on any submitted workflows. This is used by the Argo workflow controller"""

    service_account_name: Optional[str] = None
    """the service account name to be used by pods created via a workflow"""

    script_command: Optional[List[str]] = field(default_factory=lambda: ["python"])
    """the default script command to use in starting up `Script` containers"""

    experimental_features: Dict[str, bool] = field(default_factory=lambda: defaultdict(bool))
    """an indicator holder for any Hera experimental features to use"""

    def reset(self) -> None:
        """Resets the global config container to its initial state."""
        self.__dict__ = _GlobalConfig().__dict__

    @property
    def image(self) -> str:
        """Return the default image to use for Tasks."""
        if isinstance(self._image, str):
            return self._image
        return self._image()

    @image.setter
    def image(self, image: Union[str, Callable[[], str]]) -> None:
        """Set the default image to use for Tasks."""
        self._image = image

    @property
    def token(self) -> Optional[str]:
        """Returns an Argo Workflows global token."""
        if self._token is None or isinstance(self._token, str):
            return self._token
        return self._token()

    @token.setter
    def token(self, t: Union[Optional[str], TokenGenerator, Callable[[], Optional[str]]]) -> None:
        """Sets the Argo Workflows token at a global level so services can use it."""
        self._token = t

    def register_pre_build_hook(self, hook: Hook) -> Hook:
        """Registers a hook to be called before building a model."""
        return_type = inspect.signature(hook).return_annotation
        if return_type is inspect.Signature.empty:
            raise TypeError("Hook must have a return type annotation")
        self._pre_build_hooks = self._pre_build_hooks or {}
        self._pre_build_hooks.setdefault(return_type, []).append(hook)
        return hook

    def _get_pre_build_hooks(self, instance: TBase) -> List[Hook]:
        """Registers a hook to be called before building a model."""
        self._pre_build_hooks = self._pre_build_hooks or {}
        return self._pre_build_hooks.get(type(instance)) or []

    def set_class_defaults(self, cls: Type[TBase], **kwargs: Any) -> None:
        """Sets default values for a class.

        Args:
            cls: The class to set defaults for.
            kwargs: The default values to set.
        """
        invalid_keys = set(kwargs) - set(cls.__fields__)
        if invalid_keys:
            raise ValueError(f"Invalid keys for class {cls}: {invalid_keys}")
        self._defaults[cls].update(kwargs)

    def _get_class_defaults(self, cls: BaseMixin) -> Any:
        """Gets a default value for a class.

        Args:
            cls: The class to get defaults for.
        """
        return self._defaults[cls]


class BaseMixin(BaseModel):
    def _init_private_attributes(self):
        """A pydantic private method called after `__init__`.

        Notes:
        -----
        In order to inject `__hera_init__` after `__init__` without destroying the autocomplete, we opted for
        this method. We also tried other ways including creating a metaclass that invokes hera_init after init,
        but that always broke auto-complete for IDEs like VSCode.
        """
        super()._init_private_attributes()
        self.__hera_init__()

    def __hera_init__(self):
        """A method that is optionally implemented and invoked by `BaseMixin` subclasses to perform some post init."""
        ...

    @root_validator(pre=True)
    def _set_defaults(cls, values):
        """Sets the user-provided defaults of Hera objects."""
        defaults = global_config._get_class_defaults(cls)
        for key, value in defaults.items():
            if values.get(key) is None:
                values[key] = value
        return values


GlobalConfig = global_config = _GlobalConfig()
register_pre_build_hook = global_config.register_pre_build_hook

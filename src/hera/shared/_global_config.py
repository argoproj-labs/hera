from __future__ import annotations

import inspect
from typing import Callable, Dict, List, Optional, Type, Union

from ._base_model import TBase

Hook = Callable[[TBase], TBase]
_HookMap = Dict[Type[TBase], List[Hook]]


class _GlobalConfig:
    """Hera global configuration holds any user configuration such as global tokens, hooks, etc.

    Notes:
        This should not be instantiated directly by the user. There is an instance of the `_GlobalConfig` in this module,
        which is what should be used. Access as `hera.shared.global_config` or `hera.shared.GlobalConfig`.
    """

    # protected attributes are ones that are computed/go through some light processing upon setting or
    # are processed upon accessing. The rest, which use primitive types, such as `str`, can remain public
    _token: Union[Optional[str], Callable[[], Optional[str]]] = None

    host: Optional[str] = None
    verify_ssl: bool = True
    api_version: str = "argoproj.io/v1alpha1"
    namespace: Optional[str] = None
    _image: Union[str, Callable[[], str]] = "python:3.7"
    service_account_name: Optional[str] = None
    script_command: Optional[List[str]] = ["python"]
    _pre_build_hooks: Optional[_HookMap] = None

    def reset(self) -> None:
        """Resets the global config container to its initial state"""
        self.__dict__.clear()  # Wipe instance values to fallback to the class defaults

    @property
    def image(self) -> str:
        """Return the default image to use for Tasks"""
        if isinstance(self._image, str):
            return self._image
        return self._image()

    @image.setter
    def image(self, image: Union[str, Callable[[], str]]) -> None:
        """Set the default image to use for Tasks"""
        self._image = image

    @property
    def token(self) -> Optional[str]:
        """Returns an Argo Workflows global token"""
        if self._token is None or isinstance(self._token, str):
            return self._token
        return self._token()

    @token.setter
    def token(self, t: Union[Optional[str], Callable[[], Optional[str]]]) -> None:
        """Sets the Argo Workflows token at a global level so services can use it"""
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


GlobalConfig = global_config = _GlobalConfig()
register_pre_build_hook = global_config.register_pre_build_hook

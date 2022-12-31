from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Callable, Optional, Tuple, Union

from typing_extensions import Protocol

if TYPE_CHECKING:
    from hera.task import Task
    from hera.workflow import Workflow


class _GlobalConfig:
    """Hera global configuration holds any user configuration such as global tokens, hooks, etc.

    Notes
    -----
    This should not be instantiated directly by the user. There is an instance of the `_GlobalConfig` in this module,
    which is what should be used. Access as either `hera.GlobalConfig` or `hera.global_config.GlobalConfig/Config`.
    """

    # protected attributes are ones that are computed/go through some light processing upon setting or
    # are processed upon accessing. The rest, which use primitive types, such as `str`, can remain public
    _token: Union[Optional[str], Callable[[], Optional[str]]] = None

    host: str = "localhost:2746"
    verify_ssl: Optional[bool] = None
    api_version: str = "argoproj.io/v1alpha1"
    namespace: str = "default"
    image: str = "python:3.7"
    service_account_name: Optional[str] = None
    task_post_init_hooks: Tuple[Callable[[Task], None], ...] = ()
    workflow_post_init_hooks: Tuple[Callable[[Workflow], None], ...] = ()

    def reset(self) -> None:
        """Resets the global config container to its initial state"""
        self.__dict__.clear()  # Wipe instance values to fall back to the class defaults

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


GlobalConfig = _GlobalConfig()

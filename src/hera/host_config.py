from __future__ import annotations

from collections.abc import Callable
from typing import Optional, Union

_api_version: str = "argoproj.io/v1alpha1"


def set_global_api_version(v: str) -> None:
    """Sets the global API version that is used to control the `api_version` field on Argo payload submissions.

    Workflows, workflow templates, etc. use an API specification that is based on the requirements of Kubernetes:
    https://kubernetes.io/docs/reference/using-api/#api-versioning
    """
    global _api_version
    _api_version = v


def get_global_api_version() -> str:
    """Returns the set global API version. See `set_global_api_version` for more details"""
    global _api_version
    return _api_version


_host: Optional[str] = None


def set_global_host(h: Optional[str]) -> None:
    """Sets the Argo Workflows host at a global level so services can use it"""
    global _host
    _host = h


def get_global_host() -> Optional[str]:
    """Returns the Argo Workflows global host"""
    return _host


_token: Union[Optional[str], Callable[[], Optional[str]]] = None


def set_global_token(t: Union[Optional[str], Callable[[], Optional[str]]]) -> None:
    """Sets the Argo Workflows token at a global level so services can use it"""
    global _token
    _token = t


def get_global_token() -> Optional[str]:
    """Returns an Argo Workflows global token"""
    if _token is None or isinstance(_token, str):
        return _token
    return _token()


_namespace: str = "default"


def set_global_namespace(n: str) -> None:
    """Sets the Argo Workflows namespace at the global level so services can use it"""
    global _namespace
    _namespace = n


def get_global_namespace() -> str:
    """Returns the Argo Workflows global namespace"""
    return _namespace

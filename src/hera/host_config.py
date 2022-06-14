from __future__ import annotations

from collections.abc import Callable
from typing import Optional, Union

host: Optional[str] = None
token: Union[Optional[str], Callable[[], Optional[str]]] = None


def set_global_host(h: Optional[str]) -> None:
    """Sets the Argo Workflows host at a global level so services can use it"""
    global host
    host = h


def get_global_host() -> Optional[str]:
    """Returns the Argo Workflows global host"""
    return host


def set_global_token(t: Union[Optional[str], Callable[[], Optional[str]]]) -> None:
    """Sets the Argo Workflows token at a global level so services can use it"""
    global token
    token = t


def get_global_token() -> Optional[str]:
    """Returns an Argo Workflows global token"""
    if token is None or isinstance(token, str):
        return token
    return token()

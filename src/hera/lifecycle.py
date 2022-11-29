from typing import Optional

from argo_workflows.models import (
    Lifecycle as ArgoLifecycle,
    LifecycleHandler as ArgoLifecycleHandler,
)

from hera.action import ExecAction, HTTPGetAction, TCPSocketAction


class LifecycleHandler:
    """Lifecycle handler representation.

    Parameters
    ----------
    _exec: Optional[ExecAction] = None
        Optional command exec action.
    http_get: Optional[HTTPGetAction] = None
        Optional HTTP GET action.
    tcp_socket: Optional[TCPSocketAction] = None
        Optional TCP socket action.
    """

    def __init__(
        self,
        _exec: Optional[ExecAction] = None,
        http_get: Optional[HTTPGetAction] = None,
        tcp_socket: Optional[TCPSocketAction] = None,
    ) -> None:
        self._exec = _exec
        self.http_get = http_get
        self.tcp_socket = tcp_socket

    def build(self) -> ArgoLifecycleHandler:
        handler = ArgoLifecycleHandler()
        if self._exec is not None:
            setattr(handler, "_exec", self._exec)
        if self.http_get is not None:
            setattr(handler, "http_get", self.http_get)
        if self.tcp_socket is not None:
            setattr(handler, "tcp_socket", self.tcp_socket)
        return handler


class Lifecycle:
    """Pod lifecycle management.

    Parameters
    ----------
    pre_start: Optional[LifecycleHandler] = None
        Pre start lifecycle handler.
    post_start: Optional[LifecycleHandler] = None
        Post start lifecycle handler.
    """

    def __init__(self, pre_start: Optional[LifecycleHandler], post_start: Optional[LifecycleHandler]) -> None:
        self.pre_start = pre_start
        self.post_start = post_start

    def build(self) -> ArgoLifecycle:
        lifecycle = ArgoLifecycle()
        if self.pre_start is not None:
            setattr(lifecycle, "pre_start", self.pre_start)
        if self.post_start is not None:
            setattr(lifecycle, "post_start", self.post_start)
        return lifecycle

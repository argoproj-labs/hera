from typing import Optional

from argo_workflows.model.lifecycle_handler import (
    LifecycleHandler as ArgoLifecycleHandler,
)
from argo_workflows.models import Lifecycle as ArgoLifecycle

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
            setattr(handler, "_exec", self._exec.build())
        if self.http_get is not None:
            setattr(handler, "http_get", self.http_get.build())
        if self.tcp_socket is not None:
            setattr(handler, "tcp_socket", self.tcp_socket.build())
        return handler


class Lifecycle:
    """Pod lifecycle management.

    Parameters
    ----------
    pre_stop: Optional[LifecycleHandler] = None
        Pre start lifecycle handler.
    pre_stop: Optional[LifecycleHandler] = None
        Post start lifecycle handler.
    """

    def __init__(
        self, post_start: Optional[LifecycleHandler] = None, pre_stop: Optional[LifecycleHandler] = None
    ) -> None:
        self.post_start = post_start
        self.pre_stop = pre_stop

    def build(self) -> ArgoLifecycle:
        lifecycle = ArgoLifecycle()
        if self.post_start is not None:
            setattr(lifecycle, "post_start", self.post_start.build())
        if self.pre_stop is not None:
            setattr(lifecycle, "pre_stop", self.pre_stop.build())
        return lifecycle

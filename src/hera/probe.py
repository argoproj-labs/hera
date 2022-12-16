from typing import Optional

from argo_workflows.models import Probe as ArgoProbe

from hera.action import ExecAction, GRPCAction, HTTPGetAction, TCPSocketAction


class Probe:
    """Probe for lifecycle management.

    Parameters
    ----------
    """

    def __init__(
        self,
        _exec: Optional[ExecAction] = None,
        failure_threshold: Optional[int] = None,
        grpc: Optional[GRPCAction] = None,
        http_get: Optional[HTTPGetAction] = None,
        initial_delay_seconds: Optional[int] = None,
        period_seconds: Optional[int] = None,
        success_threshold: Optional[int] = None,
        tcp_socket: Optional[TCPSocketAction] = None,
        termination_grace_period_seconds: Optional[int] = None,
        timeout_seconds: Optional[int] = None,
    ) -> None:
        self._exec = _exec
        self.failure_threshold = failure_threshold
        self.grpc = grpc
        self.http_get = http_get
        self.initial_delay_seconds = initial_delay_seconds
        self.period_seconds = period_seconds
        self.success_threshold = success_threshold
        self.tcp_socket = tcp_socket
        self.termination_grace_period_seconds = termination_grace_period_seconds
        self.timeout_seconds = timeout_seconds

    def build(self) -> ArgoProbe:
        probe = ArgoProbe()
        if self._exec is not None:
            setattr(probe, "_exec", self._exec.build())
        if self.failure_threshold is not None:
            setattr(probe, "failure_threshold", self.failure_threshold)
        if self.grpc is not None:
            setattr(probe, "grpc", self.grpc.build())
        if self.http_get is not None:
            setattr(probe, "http_get", self.http_get.build())
        if self.initial_delay_seconds is not None:
            setattr(probe, "initial_delay_seconds", self.initial_delay_seconds)
        if self.period_seconds is not None:
            setattr(probe, "period_seconds", self.period_seconds)
        if self.success_threshold is not None:
            setattr(probe, "success_threshold", self.success_threshold)
        if self.tcp_socket is not None:
            setattr(probe, "tcp_socket", self.tcp_socket.build())
        if self.termination_grace_period_seconds is not None:
            setattr(probe, "termination_grace_period_seconds", self.termination_grace_period_seconds)
        if self.timeout_seconds is not None:
            setattr(probe, "timeout_seconds", self.timeout_seconds)
        return probe

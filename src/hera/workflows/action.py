from enum import Enum
from typing import List, Optional

from argo_workflows.models import ExecAction as ArgoExecAction
from argo_workflows.models import GRPCAction as ArgoGRPCAction
from argo_workflows.models import HTTPGetAction as ArgoHTTPGetAction
from argo_workflows.models import HTTPHeader as ArgoHTTPHeader
from argo_workflows.models import TCPSocketAction as ArgoTCPSocketAction


class Scheme(Enum):
    """HTTP scheme representation for HTTP GET actions"""

    http = "HTTP"
    https = "HTTPS"


class GRPCAction:
    """GRPC action to execute in lifecycle.

    Parameters
    ----------
    port: int
        Port number of the gRPC service. Number must be in the range 1 to 65535.
    service: Optional[str] = None
        Service is the name of the service to place in the gRPC HealthCheckRequest
        (see https://github.com/grpc/grpc/blob/master/doc/health-checking.md).
    """

    def __init__(self, port: int, service: Optional[str] = None) -> None:
        assert 1 <= port <= 65535, "GRPC port number must be between 1 and 65535"
        self.port = port
        self.service = service

    def build(self) -> ArgoGRPCAction:
        action = ArgoGRPCAction(self.port)
        if self.service is not None:
            setattr(action, "service", self.service)
        return action


class ExecAction:
    """Command to execute in lifecycle.

    Parameters
    ----------
    command: Optional[List[str]] = None
        Command line to execute inside the container, the working directory for the command  is root ('/') in the
        container's filesystem. The command is simply exec'd, it is not run inside a shell, so traditional shell
        instructions ('|', etc) won't work. To use a shell, you need to explicitly call out to that shell.
        Exit status of 0 is treated as live/healthy and non-zero is unhealthy.
    """

    def __init__(self, command: Optional[List[str]] = None):
        self.command = command

    def build(self) -> ArgoExecAction:
        action = ArgoExecAction()
        if self.command is not None:
            setattr(action, "command", self.command)
        return action


class HTTPHeader:
    """HTTP header representation for HTTP GET actions"""

    def __init__(self, name: str, value: str) -> None:
        self.name = name
        self.value = value

    def build(self) -> ArgoHTTPHeader:
        return ArgoHTTPHeader(self.name, self.value)


class HTTPGetAction:
    """HTTP get action to execute in lifecycle.

    Parameters
    ----------
    port: str
        Port to target for the HTTP call.
    host: Optional[str]
        Host name to connect to, defaults to the pod IP.
    http_headers: Optional[List[HTTPHeader]]
        Custom headers to set in the request.
    path: Optional[str]
        Path to access on the HTTP server.
    scheme: Optional[Scheme] = None
        Scheme to use for connecting to the host.
    """

    def __init__(
        self,
        port: str,
        host: Optional[str] = None,
        http_headers: Optional[List[HTTPHeader]] = None,
        path: Optional[str] = None,
        scheme: Optional[Scheme] = None,
    ):
        self.port = port
        self.host: Optional[str] = host  # some IDEs might complain about special forms, so setting an explicit type
        self.http_headers: Optional[List[HTTPHeader]] = http_headers
        self.path: Optional[str] = path
        self.scheme = scheme

    def build(self) -> ArgoHTTPGetAction:
        action = ArgoHTTPGetAction(self.port)
        if self.host is not None:
            setattr(action, "host", self.host)
        if self.http_headers is not None:
            setattr(action, "http_headers", [h.build() for h in self.http_headers])
        if self.path is not None:
            setattr(action, "path", self.path)
        if self.scheme is not None:
            setattr(action, "scheme", self.scheme.value)
        return action


class TCPSocketAction:
    """TCP socket action to perform during a lifecycle.

    Parameters
    ----------
    port: str
        Port to target for the HTTP call.
    host: Optional[str] = None
        Host name to connect to, defaults to the pod IP.
    """

    def __init__(self, port: str, host: Optional[str] = None):
        self.port = port
        self.host = host

    def build(self) -> ArgoTCPSocketAction:
        action = ArgoTCPSocketAction(self.port)
        if self.host is not None:
            setattr(action, "host", self.host)
        return action

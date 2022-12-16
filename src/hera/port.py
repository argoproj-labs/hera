from enum import Enum
from typing import Optional

from argo_workflows.models import ContainerPort as ArgoContainerPort


class Protocol(Enum):
    udp = "UDP"
    tcp = "TCP"
    sctp = "SCTP"


class ContainerPort:
    """Container port to expose.

    Parameters
    ----------
    container_port: int
        Port to expose on the pod's IP address. This must be a valid port number, 0 < x < 65536.
    host_ip: Optional[str] = None
        Host IP to bind external port to.
    host_port: Optional[int] = None
        Number of port to expose on the host. This must be a valid port number, 0 < x < 65536.
    name: Optional[str] = None
        An IANA_SVC_NAME and unique within the pod. Each named port in a pod must have a unique name.
        Name for the port that can be referred to by services.
    protocol: Optional[Protocol] = None
        Protocol for port. Must be UDP, TCP, or SCTP. See `Protocol`.
    """

    def __init__(
        self,
        container_port: int,
        host_ip: Optional[str] = None,
        host_port: Optional[int] = None,
        name: Optional[str] = None,
        protocol: Optional[Protocol] = None,
    ):
        if container_port is not None:
            assert 0 <= container_port <= 65535, "`container_port` must be an integer value between 0 and 65535"
        if host_port is not None:
            assert 0 <= host_port <= 65535, "`host_port` must be an integer value between 0 and 65535"

        self.container_port = container_port
        self.host_ip = host_ip
        self.host_port = host_port
        self.name = name
        self.protocol = protocol

    def build(self) -> ArgoContainerPort:
        port = ArgoContainerPort(self.container_port)
        if self.host_ip is not None:
            setattr(port, "host_ip", self.host_ip)
        if self.host_port is not None:
            setattr(port, "host_port", self.host_port)
        if self.name is not None:
            setattr(port, "name", self.name)
        if self.protocol is not None:
            setattr(port, "protocol", self.protocol.value)
        return port

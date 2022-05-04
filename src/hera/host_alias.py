from typing import List

from argo_workflows.models import HostAlias as ArgoHostAlias
from pydantic import BaseModel


class HostAlias(BaseModel):
    """mapping between IP and hostnames

    Notes
    -----
        See https://github.com/argoproj/argo-workflows/blob/master/sdks/python/client/docs/HostAlias.md
    """

    hostnames: List[str]
    ip: str

    @property
    def argo_host_alias(self) -> ArgoHostAlias:
        return ArgoHostAlias(hostnames=self.hostnames, ip=self.ip)

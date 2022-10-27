"""Holds the configurations required for submitting workflows to the Argo server"""
import os
from typing import Optional

from argo_workflows.api_client import Configuration as ArgoConfig

from hera.host_config import get_global_host, get_global_verify_ssl

try:
    import urllib3

    # __get_config() explicitly disables SSL verification, so urllib3 will throw a warning to the user. Since we have
    # explicitly asked for it to disable SSL, it's safe to ignore the warning.
    urllib3.disable_warnings()
except ImportError:  # pragma: no cover
    pass


class Config:
    """A representation for a collection of settings used to control the submission behaviour of Argo workflows.

    This configures the domain, address, and port to which workflows can be submitted.

    Parameters
    ----------
    host: Optional[str] = None
        The host of the Argo server to submit workflows to. An attempt to assemble a host from Argo K8S cluster
        environment variables is pursued if this is not specified.
    verify_ssl: Optional[bool] = None
        Whether to perform SSL/TLS verification. Set this as False to skip verifying SSL certificate when submitting
        workflows from an HTTPS server. Alternatively, you can set it globally via `host_config.set_global_verify_ssl`.
    """

    def __init__(self, host: Optional[str] = None, verify_ssl: Optional[bool] = None):
        self.host = host or self._assemble_host()
        self.verify_ssl = get_global_verify_ssl() if verify_ssl is None else verify_ssl
        self._config = self.__get_config()

    def _assemble_host(self) -> str:
        """Assembles a host from the default K8S cluster env variables with Argo's address.

        Note that there are multiple possibilities for the host. This method will try to assemble a host from the
        following sources (in order):
            - global host
            - environment host set by K8S via the `ARGO_SERVER_PORT_2746_TCP_ADDR` environment variable

        Notes
        -----
        The pod containers should have an environment variable with the address of the Argo server, and this is
        # the default one. Users who wish to assemble this on their own can do so and submit the result via the `host`

        Returns
        -------
        str
            Assembled host.
        """
        host = get_global_host()
        if host is not None:
            return host

        tcp_addr = os.getenv("ARGO_SERVER_PORT_2746_TCP_ADDR", None)
        assert tcp_addr is not None, "A configuration/service host is required for submitting workflows"

        tcp_port = os.getenv("ARGO_SERVER_PORT_2746_TCP_PORT", None)
        return f"https://{tcp_addr}:{tcp_port}" if tcp_port else f"https://{tcp_addr}"

    def __get_config(self) -> ArgoConfig:
        """Assembles the Argo configuration.

        This attempts to get environment variables that are typically
        shared with all the deployments of K8S. If those are not specified, it uses the passed in domain to configure
        the address.

        Returns
        -------
        _ArgoConfig
            The Argo service configuration.

        Notes
        -----
        The Argo server runs on HTTPS, so it sends back a certificate. However, this server runs on HTTP, and we have
        to force skip SSL verification on the ApiClient side (Argo client inside the containers of the ArgoApi clients)
        for otherwise the connection fails.

        Use this together with Client to instantiate a WorkflowService/CronWorkflowService.
        """
        config = ArgoConfig(host=self.host)
        config.verify_ssl = self.verify_ssl
        return config

    @property
    def config(self) -> ArgoConfig:
        """Returns the Argo configuration that was assembled by the class"""
        return self._config

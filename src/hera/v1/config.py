"""Holds the configurations required for submitting workflows to the Argo server"""
import os

import urllib3
from argo.workflows.client import Configuration as ArgoConfig

# __get_config() explicitly disables SSL verification, so urllib3 will throw a warning to the user. Since we have
# explicitly asked for it to disable SSL, it's safe to ignore the warning.
urllib3.disable_warnings()


class Config:
    """A representation for a collection of settings used to control the submission behaviour of Argo workflows.

    This configures the domain, address, and port to which workflows can be submitted.

    Parameters
    ----------
    domain: str
        The domain of the Argo
    """

    def __init__(self, domain: str):
        self._domain = domain
        self._config = self.__get_config()

    def __get_config(self) -> ArgoConfig:
        """Assembles the Argo configuration.

        This attempts to get environment variables that are typically
        shared with all the deployments of K8S. If those are not specified, it uses the passed in domain to configure
        the address.

        Notes
        -----
        The Argo server runs on HTTPS, so it sends back a certificate. However, this server runs on HTTP, and we have
        to force skip SSL verification on the ApiClient side (Argo client inside the containers of the ArgoApi clients)
        for otherwise the connection fails.

        Use this together with Client to instantiate a WorkflowServiceApi.
        """
        scheme = 'https'
        config = ArgoConfig()

        argo_tcp_addr = os.getenv('ARGO_SERVER_PORT_2746_TCP_ADDR')
        if argo_tcp_addr:
            host = argo_tcp_addr
        else:
            host = self._domain

        if host != self._domain:
            port = os.getenv('ARGO_SERVER_PORT_2746_TCP_PORT')
            # K8S deployments in a namespace that has an Argo deployment get Argo specific environment variables,
            # so this _should_ be safe
            assert port, 'unspecified port'
            config.verify_ssl = False
        else:
            port = ''

        addr = f'{scheme}://{host}:{port}' if port else f'{scheme}://{host}'
        config.host = addr
        return config

    @property
    def config(self) -> ArgoConfig:
        """Returns the Argo configuration that was assembled by the class"""
        return self._config

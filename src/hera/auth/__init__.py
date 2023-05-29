import base64
import errno
import os
import shutil
import subprocess
from typing import Optional

from kubernetes import client, config


class TokenGenerator:
    """A token generator can be used to generate tokens for authentication with Argo Workflows/Events APIs.

    A token generator can be set for invocation on the Hera global config via
    `hera.shared.global_config.token`.
    """

    def __call__(self) -> str:
        """Generates an authentication token for use with Argo Workflows/Events APIs"""
        raise NotImplementedError("Implement me")


class ArgoCLITokenGenerator(TokenGenerator):
    """A token generator that uses the Argo CLI to generate a token.

    Note that this involves invoking the Argo CLI, which means that the Argo CLI must be installed on the machine.
    An exception is raised if this is not the case.

    Raises
    ------
    RuntimeError
        If the Argo CLI is not installed.
    """

    def __call__(self) -> str:
        if shutil.which("argo") is None:
            raise RuntimeError(
                "The Argo CLI is not installed. "
                "See `https://argoproj.github.io/argo-workflows/walk-through/argo-cli/` for more information"
            )

        token = subprocess.check_output("argo auth token".split()).strip().decode()
        if token.startswith("Bearer "):
            token = token[7:]
        return token


class KubernetesServiceAccountTokenGenerator(TokenGenerator):
    """A token generator that uses the K8s local config file to generate a token for the specific service account.

    Parameters
    ----------
    service_account : str
        The name of the service account to generate a token for.
    namespace : Optional[str]
        The namespace of the service account. Defaults to "default".
    config_file : Optional[str]
        The path to the K8s local config file. Defaults to "~/.kube/config".

    Raises
    ------
    FileNotFoundError
        If the K8s local config file does not exist.
    """

    def __init__(self, service_account: str, namespace: str = "default", config_file: Optional[str] = None) -> None:
        self.service_account = service_account
        self.namespace: str = namespace
        self.config_file: Optional[str] = config_file

    def __call__(self) -> str:
        if self.config_file is not None and not os.path.isfile(self.config_file):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), self.config_file)

        config.load_kube_config(config_file=self.config_file)
        v1 = client.CoreV1Api()
        secret_name = v1.read_namespaced_service_account(self.service_account, self.namespace).secrets[0].name
        sec = v1.read_namespaced_secret(secret_name, self.namespace).data
        return base64.b64decode(sec["token"]).decode()

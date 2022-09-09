"""This example showcases the hello world example of Hera using kubernetes user token"""
import base64
import errno
import os
from typing import Optional

from kubernetes import client, config

from hera import Task, Workflow, WorkflowService


def get_sa_token(service_account: str, namespace: str = "default", config_file: Optional[str] = None):
    """Get ServiceAccount token using kubernetes config.

     Parameters
    ----------
    service_account: str
        The service account to authenticate from.
    namespace: str = 'default'
        The K8S namespace the workflow service submits workflows to. This defaults to the `default` namespace.
    config_file: Optional[str] = None
        The path to k8s configuration file.

     Raises
    ------
    FileNotFoundError
        When the config_file can not be found.
    """
    if config_file is not None and not os.path.isfile(config_file):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), config_file)

    config.load_kube_config(config_file=config_file)
    v1 = client.CoreV1Api()
    secret_name = v1.read_namespaced_service_account(service_account, namespace).secrets[0].name
    sec = v1.read_namespaced_secret(secret_name, namespace).data
    return base64.b64decode(sec["token"]).decode()


def hello():
    print("Hello, Hera!")


namespace = "argo"
_token = get_sa_token("argo-server", namespace=namespace)

with Workflow(
    "k8s-sa", service=WorkflowService(host="https://my-argo-server.com", token=_token, namespace=namespace)
) as w:
    Task("t", hello)

w.create(namespace=namespace)

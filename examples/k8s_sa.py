"""This example showcases the hello world example of Hera using kubernetes user token"""
from typing import Optional
import errno
import os

from hera.v1.task import Task
from hera.v1.workflow import Workflow
from hera.v1.workflow_service import WorkflowService

from kubernetes import client, config
import base64


def get_sa_token(
    service_account: str, namespace: str = "default", config_file: Optional[str] = None
):
    """Get ServiceAccount token using kubernetes config.

     Parameters
    ----------
    service_account: str
        The service account to authenticate from.
    namespace: str = 'default'
        The K8S namespace the workflow service submits workflows to. This defaults to the `default` namespace.
    config_file: str
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
    secret_name = (
        v1.read_namespaced_service_account(service_account, namespace).secrets[0].name
    )
    sec = v1.read_namespaced_secret(secret_name, namespace).data
    return base64.b64decode(sec["token"]).decode()


def hello():
    print("Hello, Hera!")


namespace = "argo"
token = get_sa_token("argo-server", namespace=namespace)

# TODO: replace the domain and token with your own
ws = WorkflowService("my-argo-server.com", token, namespace=namespace)
w = Workflow("hello-hera", ws)
t = Task("t", hello)
w.add_task(t)
ws.submit(w.workflow, namespace=namespace)

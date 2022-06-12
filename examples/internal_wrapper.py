"""
This example showcases how clients can simplify their workflow submission process by introducing some abstractions on
top of Hera to support consistency in submission across users, teams, etc.
"""

from typing import Callable, Dict, List, Optional, Union

from pydantic import BaseModel

from hera import (
    EnvSpec,
    ExistingVolume,
    InputFrom,
    Resources,
    Retry,
    Task,
    Toleration,
    Workflow,
    WorkflowService,
)


def generate_token() -> str:
    """Abstractly, generates a client Bearer token that passes auth with the Argo server for workflow submission"""
    return 'my-bearer-token'


class MyWorkflowService(WorkflowService):
    """Internal WorkflowService wrapper around Hera's WorkflowService to support consistency in auth token generation"""

    def __init__(self, host: str = 'https://my-argo-domain.com', token: str = generate_token()):
        super(MyWorkflowService, self).__init__(host=host, token=token, namespace='my-default-k8s-namespace')


class MyWorkflow(Workflow):
    """Internal Workflow wrapper around Hera's Workflow to support consistent MyWorkflowService usage"""

    def __init__(self, name: str, service: WorkflowService = MyWorkflowService(), parallelism: int = 50):
        super(MyWorkflow, self).__init__(name, service, parallelism=parallelism)


class MyTask(Task):
    """Internal Task wrapper around Hera's Task to set usage defaults"""

    def __init__(
        self,
        name: str,
        func: Callable,
        func_params: Optional[List[Dict[str, Union[int, str, float, dict, BaseModel]]]] = None,
        input_from: Optional[InputFrom] = None,
        image: str = 'python:3.7',
        command: Optional[List[str]] = None,
        env_specs: Optional[List[EnvSpec]] = None,
        resources: Resources = Resources(),
        tolerations: Optional[List[Toleration]] = None,
    ):
        default_retry = Retry(duration=1, max_duration=20)
        # note that this gke-accelerator spec is only valid for GKE GPUs. For Azure and AWS you
        # might have to use the `node_selectors` field exclusively
        default_node_selectors = {'cloud.google.com/gke-accelerator': 'nvidia-tesla-k80'}
        default_working_dir = '/my-volume'
        resources.existing_volume = ExistingVolume(name='my-volume', mount_path='/my-volume')
        super(MyTask, self).__init__(
            name,
            func,
            func_params,
            input_from=input_from,
            image=image,
            command=command,
            env_specs=env_specs,
            resources=resources,
            working_dir=default_working_dir,
            retry=default_retry,
            tolerations=tolerations,
            node_selectors=default_node_selectors,
        )


def example():
    """Example usage of wrapper to demonstrate how it can slightly simplify submission"""
    w = MyWorkflow('my-workflow')
    t = MyTask('t', lambda: print(42))
    w.add_task(t)
    w.create()

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, List, Optional, Tuple, Union

if TYPE_CHECKING:
    from hera.workflows.container import Container
    from hera.workflows.container_set import ContainerNode, ContainerSet
    from hera.workflows.cron_workflow import CronWorkflow
    from hera.workflows.dag import DAG
    from hera.workflows.resource import Resource
    from hera.workflows.script import Script
    from hera.workflows.steps import Step, Steps
    from hera.workflows.task import Task
    from hera.workflows.workflow import Workflow
    from hera.workflows.workflow_template import WorkflowTemplate


class _GlobalConfig:
    """Hera global configuration holds any user configuration such as global tokens, hooks, etc.

    Notes
    -----
    This should not be instantiated directly by the user. There is an instance of the `_GlobalConfig` in this module,
    which is what should be used. Access as either `hera.GlobalConfig` or `hera.global_config.GlobalConfig/Config`.
    """

    # protected attributes are ones that are computed/go through some light processing upon setting or
    # are processed upon accessing. The rest, which use primitive types, such as `str`, can remain public
    _token: Union[Optional[str], Callable[[], Optional[str]]] = None

    host: Optional[str] = None
    verify_ssl: bool = True
    api_version: str = "argoproj.io/v1alpha1"
    namespace: Optional[str] = None
    image: str = "python:3.7"
    service_account_name: Optional[str] = None
    script_command: Optional[List[str]] = ["python"]

    # These hooks are applied once the workflow is constructed for submission
    # subbable hooks
    workflow_pre_build_hooks: Tuple[Callable[[Workflow], None], ...] = ()
    cron_workflow_pre_build_hooks: Tuple[Callable[[CronWorkflow], None], ...] = ()
    workflow_template_pre_build_hooks: Tuple[Callable[[WorkflowTemplate], None], ...] = ()
    dag_pre_build_hooks: Tuple[Callable[[DAG], None], ...] = ()
    container_set_pre_build_hooks: Tuple[Callable[[ContainerSet], None], ...] = ()
    steps_pre_build_hooks: Tuple[Callable[[Steps], None], ...] = ()

    # subnode hooks
    task_pre_build_hooks: Tuple[Callable[[Task], None], ...] = ()
    resource_pre_build_hooks: Tuple[Callable[[Resource], None], ...] = ()
    container_node_pre_build_hooks: Tuple[Callable[[ContainerNode], None], ...] = ()
    step_pre_build_hooks: Tuple[Callable[[Step], None], ...] = ()
    container_pre_build_hooks: Tuple[Callable[[Container], None], ...] = ()
    script_pre_build_hooks: Tuple[Callable[[Script], None], ...] = ()

    def reset(self) -> None:
        """Resets the global config container to its initial state"""
        self.__dict__.clear()  # Wipe instance values to fallback to the class defaults

    @property
    def token(self) -> Optional[str]:
        """Returns an Argo Workflows global token"""
        if self._token is None or isinstance(self._token, str):
            return self._token
        return self._token()

    @token.setter
    def token(self, t: Union[Optional[str], Callable[[], Optional[str]]]) -> None:
        """Sets the Argo Workflows token at a global level so services can use it"""
        self._token = t


GlobalConfig = _GlobalConfig()

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, List, Optional, Tuple, Union

from hera.workflows.exceptions import InvalidDispatchType

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

    # subbable hooks
    workflow_post_init_hooks: Tuple[Callable[[Workflow], None], ...] = ()
    cron_workflow_post_init_hooks: Tuple[Callable[[CronWorkflow], None], ...] = ()
    workflow_template_post_init_hooks: Tuple[Callable[[WorkflowTemplate], None], ...] = ()
    dag_post_init_hooks: Tuple[Callable[[DAG], None], ...] = ()
    container_set_post_init_hooks: Tuple[Callable[[ContainerSet], None], ...] = ()
    steps_post_init_hooks: Tuple[Callable[[Steps], None], ...] = ()

    # subnode hooks
    task_post_init_hooks: Tuple[Callable[[Task], None], ...] = ()
    resource_post_init_hooks: Tuple[Callable[[Resource], None], ...] = ()
    container_node_post_init_hooks: Tuple[Callable[[ContainerNode], None], ...] = ()
    step_post_init_hooks: Tuple[Callable[[Step], None], ...] = ()
    container_post_init_hooks: Tuple[Callable[[Container], None], ...] = ()
    script_post_init_hooks: Tuple[Callable[[Script], None], ...] = ()

    def dispatch_hooks(
        self,
        obj: Union[
            Workflow,
            WorkflowTemplate,
            CronWorkflow,
            Container,
            ContainerSet,
            ContainerNode,
            DAG,
            Resource,
            Script,
            Step,
            Steps,
            Task,
        ],
    ) -> None:
        if isinstance(obj, Workflow):
            _dispatch_hooks_to_obj(obj, self.workflow_post_init_hooks)
        elif isinstance(obj, CronWorkflow):
            _dispatch_hooks_to_obj(obj, self.cron_workflow_post_init_hooks)
        elif isinstance(obj, WorkflowTemplate):
            _dispatch_hooks_to_obj(obj, self.workflow_template_post_init_hooks)
        elif isinstance(obj, DAG):
            _dispatch_hooks_to_obj(obj, self.dag_post_init_hooks)
        elif isinstance(obj, ContainerSet):
            _dispatch_hooks_to_obj(obj, self.container_set_post_init_hooks)
        elif isinstance(obj, Steps):
            _dispatch_hooks_to_obj(obj, self.steps_post_init_hooks)
        elif isinstance(obj, Task):
            _dispatch_hooks_to_obj(obj, self.task_post_init_hooks)
        elif isinstance(obj, Resource):
            _dispatch_hooks_to_obj(obj, self.resource_post_init_hooks)
        elif isinstance(obj, ContainerNode):
            _dispatch_hooks_to_obj(obj, self.container_node_post_init_hooks)
        elif isinstance(obj, Step):
            _dispatch_hooks_to_obj(obj, self.step_post_init_hooks)
        elif isinstance(obj, Container):
            _dispatch_hooks_to_obj(obj, self.container_post_init_hooks)
        elif isinstance(obj, Script):
            _dispatch_hooks_to_obj(obj, self.script_post_init_hooks)
        else:
            raise InvalidDispatchType(f"Invalid dispatch type: {type(obj)}")

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


def _dispatch_hooks_to_obj(
    obj: Union[
        Workflow,
        WorkflowTemplate,
        CronWorkflow,
        Container,
        ContainerSet,
        ContainerNode,
        DAG,
        Resource,
        Script,
        Step,
        Steps,
        Task,
    ],
    hooks: Tuple[Callable[[Any], None], ...],
) -> None:
    for hook in hooks:
        hook(obj)


GlobalConfig = _GlobalConfig()

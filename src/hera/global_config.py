from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Optional, Tuple, Union, cast

from typing_extensions import Protocol

if TYPE_CHECKING:
    from hera.task import Task
    from hera.workflow import Workflow


class TaskHook(Protocol):
    def __call__(self, t: Task) -> None:
        ...


class WorkflowHook(Protocol):
    def __call__(self, w: Workflow) -> None:
        ...


class _GlobalConfig:
    """Hera global configuration holds any user configuration such as global tokens, hooks, etc.

    Notes
    -----
    This should not be instantiated directly by the user. There is an instance of the `_GlobalConfig` in this module,
    which is what should be used. Access as either `hera.GlobalConfig` or `hera.global_config.GlobalConfig/Config`.
    """

    _host: Optional[str] = None
    _token: Union[Optional[str], Callable[[], Optional[str]]] = None
    _verify_ssl: bool = True

    _api_version: str = "argoproj.io/v1alpha1"
    _namespace: str = "default"
    _image: str = "python:3.7"
    _service_account_name: Optional[str] = None

    _task_post_init_hooks: Tuple[TaskHook, ...] = ()
    _workflow_post_init_hooks: Tuple[WorkflowHook, ...] = ()

    def reset(self) -> None:
        """Resets the global config container to its initial state"""
        self.__dict__.clear()
        self._host = None
        self._token = None
        self._verify_ssl = True

        self._api_version = "argoproj.io/v1alpha1"
        self._namespace = "default"
        self._image = "python:3.7"
        self._service_account_name = None

        self._task_post_init_hooks = ()
        self._workflow_post_init_hooks = ()

    @property
    def host(self) -> Optional[str]:
        """Returns the Argo Workflows global host"""
        return self._host

    @host.setter
    def host(self, h: Optional[str]) -> None:
        """Sets the Argo Workflows host at a global level so services can use it"""
        self._host = h

    @property
    def token(self) -> Union[Optional[str], Callable[[], Optional[str]]]:
        """Returns an Argo Workflows global token"""
        if self._token is None or isinstance(self._token, str):
            return self._token
        return self._token()

    @token.setter
    def token(self, t: Union[Optional[str], Callable[[], Optional[str]]]) -> None:
        """Sets the Argo Workflows token at a global level so services can use it"""
        self._token = t

    @property
    def verify_ssl(self) -> bool:
        """Returns the Argo Workflows global namespace"""
        return self._verify_ssl

    @verify_ssl.setter
    def verify_ssl(self, v: bool) -> None:
        """Sets the Argo Workflows namespace at the global level so services can use it"""
        self._verify_ssl = v

    @property
    def api_version(self) -> str:
        """Returns the set global API version. See `set_global_api_version` for more details"""
        return self._api_version

    @api_version.setter
    def api_version(self, v: str) -> None:
        """Sets the global API version that is used to control the `api_version` field on Argo payload submissions.

        Workflows, workflow templates, etc. use an API specification that is based on the requirements of Kubernetes:
        https://kubernetes.io/docs/reference/using-api/#api-versioning
        """
        self._api_version = v

    @property
    def namespace(self) -> str:
        """Returns the Argo Workflows global namespace"""
        return self._namespace

    @namespace.setter
    def namespace(self, n: str) -> None:
        """Sets the Argo Workflows namespace at the global level so services can use it"""
        self._namespace = n

    @property
    def image(self) -> str:
        """Returns the Argo Task global image"""
        return self._image

    @image.setter
    def image(self, i: str) -> None:
        """Sets the Argo Task image at the global level which Tasks will use by default"""
        self._image = i

    @property
    def service_account_name(self) -> Optional[str]:
        """Returns the set global service account"""
        return self._service_account_name

    @service_account_name.setter
    def service_account_name(self, sa: Optional[str]) -> None:
        """Sets the service account to use for workflow submissions on a global level"""
        self._service_account_name = sa

    @property
    def task_post_init_hooks(self) -> Tuple[TaskHook, ...]:
        """Returns the set global task post init hooks"""
        return self._task_post_init_hooks

    @task_post_init_hooks.setter
    def task_post_init_hooks(self, h: Union[TaskHook, Tuple[TaskHook, ...]]) -> None:
        """Adds a task post init hook. The hooks are executed in FIFO order"""
        # note, your IDE might show these instance checks as incorrect but, they should be fine
        if isinstance(h, list) or isinstance(h, tuple):
            self._task_post_init_hooks = self._task_post_init_hooks + tuple(h)
        else:
            self._task_post_init_hooks = self._task_post_init_hooks + (cast(TaskHook, h),)

    @property
    def workflow_post_init_hooks(self) -> Tuple[WorkflowHook, ...]:
        """Returns the set global workflow post init hooks"""
        return self._workflow_post_init_hooks

    @workflow_post_init_hooks.setter
    def workflow_post_init_hooks(self, h: Union[WorkflowHook, Tuple[WorkflowHook, ...]]) -> None:
        """Adds a workflow post init hook. The hooks are executed in FIFO order"""
        if isinstance(h, list) or isinstance(h, tuple):
            self._workflow_post_init_hooks = self._workflow_post_init_hooks + tuple(h)
        else:
            self._workflow_post_init_hooks = self._workflow_post_init_hooks + (cast(WorkflowHook, h),)


GlobalConfig = _GlobalConfig()

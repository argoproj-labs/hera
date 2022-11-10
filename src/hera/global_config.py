from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Optional, Tuple, Union, cast

from typing_extensions import Protocol

if TYPE_CHECKING:
    from hera.task import Task
    from hera.workflow import Workflow


# usage of `pragma: no cover` since coverage will complain that protocols are not tested. These are indeed tested
# but protocols encourage nominal typing, so any function definition that implements a protocol will not be "noticed"
# by coverage. See `test_global_config` for test coverage
class TaskHook(Protocol):  # pragma: no cover
    def __call__(self, t: Task) -> None:
        ...


# usage of `pragma: no cover` since coverage will complain that protocols are not tested. These are indeed tested
# but protocols encourage nominal typing, so any function definition that implements a protocol will not be "noticed"
# by coverage. See `test_global_config` for test coverage
class WorkflowHook(Protocol):  # pragma: no cover
    def __call__(self, w: Workflow) -> None:
        ...


class _GlobalConfig:
    """Hera global configuration holds any user configuration such as global tokens, hooks, etc.

    Notes
    -----
    This should not be instantiated directly by the user. There is an instance of the `_GlobalConfig` in this module,
    which is what should be used. Access as either `hera.GlobalConfig` or `hera.global_config.GlobalConfig/Config`.
    """

    # note: protected attributes are ones that are computed/go through some light processing upon setting or
    # are processed upon accessing. The rest, which use primitive types, such as `str`, can remain public
    host: Optional[str] = None
    verify_ssl: bool = True
    api_version: str = "argoproj.io/v1alpha1"
    namespace: str = "default"
    image: str = "python:3.7"
    service_account_name: Optional[str] = None

    _token: Union[Optional[str], Callable[[], Optional[str]]] = None
    _task_post_init_hooks: Tuple[TaskHook, ...] = ()
    _workflow_post_init_hooks: Tuple[WorkflowHook, ...] = ()

    def reset(self) -> None:
        """Resets the global config container to its initial state"""
        self.__dict__.clear()
        self._token = None
        self._task_post_init_hooks = ()
        self._workflow_post_init_hooks = ()

        self.host = None
        self.verify_ssl = True
        self.api_version = "argoproj.io/v1alpha1"
        self.namespace = "default"
        self.image = "python:3.7"
        self.service_account_name = None

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

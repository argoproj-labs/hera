from typing import Dict, List, Optional

from hera.workflows.models import HTTP as _ModelHTTP
from hera.workflows.models import (
    Arguments,
    ContinueOn,
    HTTPBodySource,
    Item,
    LifecycleHook,
    Sequence,
)
from hera.workflows.models import Template as _ModelTemplate
from hera.workflows.models import V1HTTPHeader as HTTPHeader
from hera.workflows.v5._mixins import _DAGTaskMixin, _SubNodeMixin, _TemplateMixin


class HTTP(_TemplateMixin, _SubNodeMixin):
    url: str
    body: Optional[str] = None
    body_from: Optional[HTTPBodySource] = None
    headers: Optional[List[HTTPHeader]] = None
    insecure_skip_verify: Optional[bool] = None
    method: Optional[str] = None
    success_condition: Optional[str] = None
    timeout_seconds: Optional[int] = None

    def __call__(
        self,
        name: str,
        arguments: Optional[Arguments] = None,
        continue_on: Optional[ContinueOn] = None,
        dependencies: Optional[List[str]] = None,
        depends: Optional[str] = None,
        hooks: Optional[Dict[str, LifecycleHook]] = None,
        on_exit: Optional[str] = None,
        when: Optional[str] = None,
        with_items: Optional[List[Item]] = None,
        with_param: Optional[str] = None,
        with_sequence: Optional[Sequence] = None,
    ) -> _DAGTaskMixin:
        from hera.workflows.v5._context import _context

        dag_task = _DAGTaskMixin(
            name=self.name,
            arguments=arguments,
            continue_on=continue_on,
            dependencies=dependencies,
            depends=depends,
            hooks=hooks,
            on_exit=on_exit,
            when=when,
            with_items=with_items,
            with_param=with_param,
            with_sequence=with_sequence,
        )
        _context.add_sub_node(dag_task)
        return dag_task

    def _build_http_template(self) -> _ModelHTTP:
        return _ModelHTTP(
            url=self.url,
            body=self.body,
            body_from=self.body_from,
            headers=self.headers,
            insecure_skip_verify=self.insecure_skip_verify,
            method=self.method,
            success_condition=self.success_condition,
            timeout_seconds=self.timeout_seconds,
        )

    def _build_template(self) -> _ModelTemplate:
        return _ModelTemplate(
            active_deadline_seconds=self.active_deadline_seconds,
            affinity=self.affinity,
            archive_location=self.archive_location,
            automount_service_account_token=self.automount_service_account_token,
            executor=self.executor,
            fail_fast=self.fail_fast,
            host_aliases=self.host_aliases,
            http=self._build_http_template(),
            init_containers=self.init_containers,
            memoize=self.memoize,
            metadata=self._build_metadata(),
            name=self.name,
            node_selector=self.node_selector,
            plugin=self.plugin,
            priority=self.priority,
            priority_class_name=self.priority_class_name,
            retry_strategy=self.retry_strategy,
            scheduler_name=self.scheduler_name,
            security_context=self.pod_security_context,
            service_account_name=self.service_account_name,
            sidecars=self.sidecars,
            synchronization=self.synchronization,
            timeout=self.timeout,
            tolerations=self.tolerations,
        )

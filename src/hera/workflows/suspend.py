"""The suspend module provides the Suspend class. The Suspend template in Hera
provides a convenience wrapper around the "Intermediate Parameters" Argo feature.

See https://argoproj.github.io/argo-workflows/walk-through/suspending/
for more on suspending.

See https://argoproj.github.io/argo-workflows/intermediate-inputs/
for more on intermediate parameters.

"""
from typing import List, Optional, Union

from hera.workflows._mixins import TemplateMixin
from hera.workflows.models import (
    Inputs,
    Outputs,
    SuspendTemplate as _ModelSuspendTemplate,
    Template as _ModelTemplate,
)
from hera.workflows.parameter import Parameter


class Suspend(TemplateMixin):
    """The Suspend template allows the user to pause a workflow for a specified length of time
    given by `duration` or indefinitely (i.e. until manually resumed). The Suspend template also
    allows you to specify `intermediate_parameters` which will replicate the given parameters to
    the "inputs" and "outputs" of the template, resulting in a Suspend template that pauses and
    waits for values from the user for the given list of parameters.
    """

    duration: Optional[Union[int, str]] = None
    intermediate_parameters: List[Parameter] = []

    def _build_suspend_template(self) -> _ModelSuspendTemplate:
        return _ModelSuspendTemplate(
            duration=self.duration,
        )

    def _build_outputs(self) -> Optional[Outputs]:
        outputs = []
        for param in self.intermediate_parameters:
            outputs.append(
                Parameter(name=param.name, value_from={"supplied": {}}, description=param.description).as_output()
            )
        return Outputs(parameters=outputs) if outputs else None

    def _build_inputs(self) -> Optional[Inputs]:
        inputs = []
        for param in self.intermediate_parameters:
            inputs.append(param.as_input())
        return Inputs(parameters=inputs) if inputs else None

    def _build_template(self) -> _ModelTemplate:
        return _ModelTemplate(
            active_deadline_seconds=self.active_deadline_seconds,
            affinity=self.affinity,
            archive_location=self.archive_location,
            automount_service_account_token=self.automount_service_account_token,
            executor=self.executor,
            fail_fast=self.fail_fast,
            host_aliases=self.host_aliases,
            init_containers=self.init_containers,
            inputs=self._build_inputs(),
            memoize=self.memoize,
            metadata=self._build_metadata(),
            name=self.name,
            node_selector=self.node_selector,
            outputs=self._build_outputs(),
            plugin=self.plugin,
            priority_class_name=self.priority_class_name,
            priority=self.priority,
            retry_strategy=self.retry_strategy,
            scheduler_name=self.scheduler_name,
            security_context=self.pod_security_context,
            service_account_name=self.service_account_name,
            sidecars=self.sidecars,
            suspend=self._build_suspend_template(),
            synchronization=self.synchronization,
            timeout=self.timeout,
            tolerations=self.tolerations,
        )


__all__ = ["Suspend"]

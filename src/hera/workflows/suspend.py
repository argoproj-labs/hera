"""The `hera.workflows.suspend` module provides the Suspend class.

The Suspend template in Hera provides a convenience wrapper around the "Intermediate Parameters" Argo feature.

Note:
    * See <https://argoproj.github.io/argo-workflows/walk-through/suspending> for more on suspending.
    * See <https://argoproj.github.io/argo-workflows/intermediate-inputs> for more on intermediate parameters.
"""

from typing import List, Optional, Union

from hera.workflows._meta_mixins import CallableTemplateMixin
from hera.workflows._mixins import IOMixin, TemplateMixin
from hera.workflows.models import (
    Inputs,
    Outputs,
    SuppliedValueFrom,
    SuspendTemplate as _ModelSuspendTemplate,
    Template as _ModelTemplate,
    ValueFrom,
)
from hera.workflows.parameter import Parameter


class Suspend(
    TemplateMixin,
    CallableTemplateMixin,
    IOMixin,
):
    """The Suspend template allows the user to pause a workflow for a specified length of time.

    The workflow can pause based on the given by `duration` or indefinitely (i.e. until manually resumed).
    The Suspend template also allows you to specify `intermediate_parameters` which will replicate the given
    parameters to the "inputs" and "outputs" of the template, resulting in a Suspend template that pauses and
    waits for values from the user for the given list of parameters.
    """

    duration: Optional[Union[int, str]] = None
    intermediate_parameters: List[Parameter] = []

    def _build_suspend_template(self) -> _ModelSuspendTemplate:
        return _ModelSuspendTemplate(
            duration=str(self.duration) if self.duration else None,
        )

    def _build_outputs(self) -> Optional[Outputs]:
        intermediate_param_outputs = []
        for param in self.intermediate_parameters:
            intermediate_param_outputs.append(
                Parameter(
                    name=param.name,
                    value_from=ValueFrom(supplied=SuppliedValueFrom()),
                    description=param.description,
                ).as_output()
            )

        all_outputs = super()._build_outputs()
        if all_outputs is not None:
            if all_outputs.parameters is None:
                all_outputs.parameters = []
            all_outputs.parameters.extend(intermediate_param_outputs)
            return all_outputs
        else:
            return Outputs(parameters=intermediate_param_outputs) if intermediate_param_outputs else None

    def _build_inputs(self) -> Optional[Inputs]:
        intermediate_param_inputs = []
        for param in self.intermediate_parameters:
            intermediate_param_inputs.append(param.as_input())

        all_inputs = super()._build_inputs()
        if all_inputs is not None:
            if all_inputs.parameters is None:
                all_inputs.parameters = []
            all_inputs.parameters.extend(intermediate_param_inputs)
            return all_inputs
        else:
            return Inputs(parameters=intermediate_param_inputs) if intermediate_param_inputs else None

    def _build_template(self) -> _ModelTemplate:
        return _ModelTemplate(
            active_deadline_seconds=self.active_deadline_seconds,
            affinity=self.affinity,
            archive_location=self.archive_location,
            automount_service_account_token=self.automount_service_account_token,
            executor=self.executor,
            fail_fast=self.fail_fast,
            host_aliases=self.host_aliases,
            init_containers=self._build_init_containers(),
            inputs=self._build_inputs(),
            memoize=self.memoize,
            metadata=self._build_metadata(),
            name=self.name,
            node_selector=self.node_selector,
            outputs=self._build_outputs(),
            plugin=self.plugin,
            priority_class_name=self.priority_class_name,
            retry_strategy=self._build_retry_strategy(),
            scheduler_name=self.scheduler_name,
            security_context=self.pod_security_context,
            service_account_name=self.service_account_name,
            sidecars=self._build_sidecars(),
            suspend=self._build_suspend_template(),
            synchronization=self.synchronization,
            timeout=self.timeout,
            tolerations=self.tolerations,
        )


__all__ = ["Suspend"]

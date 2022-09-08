"""The implementation of a Hera cron workflow for Argo-based cron workflows"""
from typing import Tuple

from argo_workflows.models import IoArgoprojWorkflowV1alpha1WorkflowTemplate

from hera.workflow import Workflow


class WorkflowTemplate(Workflow):
    """A cron workflow representation.

    CronWorkflow are workflows that run on a preset schedule.
    In essence, CronWorkflow = Workflow + some specific cron options.

    See https://argoproj.github.io/argo-workflows/cron-workflows/

    Parameters
    ----------
    schedule: str
        Schedule at which the Workflow will be run in Cron format. E.g. 5 4 * * *.
    timezone: str
        Timezone during which the Workflow will be run from the IANA timezone standard, e.g. America/Los_Angeles.

    """

    # TODO: add support for node selectors, variables, and tolerations
    def build(self) -> IoArgoprojWorkflowV1alpha1WorkflowTemplate:
        spec = super().build_spec(workflow_template=True)
        return IoArgoprojWorkflowV1alpha1WorkflowTemplate(metadata=self.build_metadata(), spec=spec)

    def create(self):
        if self.in_context:
            raise ValueError("Cannot invoke `create` when using a Hera context")
        assert self.dag
        return self.service.create_template(self.build())

    def delete(self) -> Tuple[object, int, dict]:
        """Deletes the workflow"""
        return self.service.delete_template(self.name)

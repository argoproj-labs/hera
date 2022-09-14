"""The implementation of a Hera workflow for Argo-based workflows"""
from typing import List, Optional, Union

from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1DAGTemplate,
    IoArgoprojWorkflowV1alpha1Template,
    PersistentVolumeClaim,
)
from argo_workflows.models import Volume as ArgoVolume

from hera.artifact import Artifact
from hera.io import IO
from hera.parameter import Parameter
from hera.task import Task
from hera.validators import validate_name
from hera.workflow_editors import add_task, add_tasks


class DAG(IO):
    """A directed acyclic graph representation (workflow) representation.

    The DAG/workflow is used as a functional representation for a collection of tasks and
    steps. The workflow context controls the overall behaviour of tasks, such as whether to notify completion, whether
    to execute retires, overall parallelism, etc. The workflow can be constructed and submitted to multiple Argo
    endpoints as long as a token can be associated with the endpoint at the given domain.

    Parameters
    ----------
    name: str
        The workflow name. Note that the workflow initiation will replace underscores with dashes.
    inputs: Optional[List[Union[Parameter, Artifact]]] = None
        Any inputs to set on the DAG at a global level.
    outputs: Optional[List[Union[Parameter, Artifact]]] = None
        Any outputs to set on the DAG at a global level.
    """

    def __init__(
        self,
        name: str,
        inputs: Optional[List[Union[Parameter, Artifact]]] = None,
        outputs: Optional[List[Union[Parameter, Artifact]]] = None,
    ):
        self.name = validate_name(name)
        self.inputs = inputs or []
        self.outputs = outputs or []
        self.tasks: List[Task] = []

    def build_templates(self):
        """Assembles the templates from sub-DAGs of the DAG"""
        templates = [t for t in [t.build_template() for t in self.tasks] if t]
        # Assemble the templates from sub-dags
        sub_templates = [t.dag.build_templates() for t in self.tasks if t.dag]
        sub_templates = [t for sublist in sub_templates for t in sublist]  # flatten
        return templates + sub_templates

    def build_dag_tasks(self):
        """Assembles all the DAG tasks"""
        return [t for t in [t.build_dag_task() for t in self.tasks if not t.is_exit_task] if t]

    def build_volume_claim_templates(self) -> List[PersistentVolumeClaim]:
        """Assembles the volume claim templates"""
        # make sure we only have unique names
        vcs = dict()
        for t in self.tasks:
            for v in t.build_volume_claim_templates():
                vcs[v.metadata.name] = v

        # sub-claims:
        sub_volume_claims = [t.dag.build_volume_claim_templates() for t in self.tasks if t.dag]
        for volume_claims in sub_volume_claims:
            for v in volume_claims:
                vcs[v.metadata.name] = v

        return [v for _, v in vcs.items()]

    def build_persistent_volume_claims(self) -> List[ArgoVolume]:
        """Assembles the persistent volume claim templates"""
        # Make sure we only have unique names
        pcvs = dict()
        for t in self.tasks:
            for v in t.build_persistent_volume_claims():
                pcvs[v.name] = v

        # sub-claims:
        sub_volume_claims = [t.dag.build_persistent_volume_claims() for t in self.tasks if t.dag]
        for volume_claims in sub_volume_claims:
            for v in volume_claims:
                pcvs[v.name] = v

        return [v for _, v in pcvs.items()]

    def build(self) -> List[IoArgoprojWorkflowV1alpha1Template]:
        """Assembles the main DAG/workflow template"""
        dag = IoArgoprojWorkflowV1alpha1Template(
            name=self.name, dag=IoArgoprojWorkflowV1alpha1DAGTemplate(tasks=self.build_dag_tasks())
        )
        inputs = self.build_inputs()
        if inputs:
            setattr(dag, "inputs", inputs)
        outputs = self.build_outputs()
        if outputs:
            setattr(dag, "outputs", outputs)
        # Assemble the sub-dags if present in task templates
        sub_dags = [t.dag.build() for t in self.tasks if t.dag]
        sub_dags = [item for sublist in sub_dags for item in sublist]  # flatten
        return [dag] + sub_dags

    def __enter__(self) -> "DAG":
        """Enter the context of the DAG. This supports the use of `with DAG(...)`"""
        from hera import dag_context

        self.in_context = True
        dag_context.enter(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the context of the DAG. This supports the use of `with DAG(...)`"""
        from hera import dag_context

        self.in_context = False
        dag_context.exit()

    def add_task(self, t: Task) -> None:
        """Add a task to the DAG. Note that tasks are added automatically when the DAG context is used"""
        add_task(self, t)

    def add_tasks(self, *ts: Task) -> None:
        """Add a collection of tasks to the DAG.

        Note that tasks are added automatically when the DAG context is used
        """
        add_tasks(self, *ts)

    def get_parameter(self, name: str):
        """Returns the parameter specification of a DAG"""
        if next((p for p in self.inputs if p.name == name), None) is None:
            raise KeyError("`{name}` not in DAG inputs")
        return Parameter(name, value=f"{{{{inputs.parameters.{name}}}}}")

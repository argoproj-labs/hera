"""The implementation of a Hera workflow for Argo-based workflows"""
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

if TYPE_CHECKING:
    from hera.task import Task

from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1DAGTask,
    IoArgoprojWorkflowV1alpha1DAGTemplate,
    IoArgoprojWorkflowV1alpha1Template,
    PersistentVolumeClaim,
)
from argo_workflows.models import Volume as ArgoVolume

from hera.artifact import Artifact
from hera.io import IO
from hera.parameter import Parameter
from hera.validators import validate_name


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
    inputs: Optional[
            Union[
                List[Union[Parameter, Artifact]],
                List[Union[Parameter, Artifact, Dict[str, Any]]],
                Dict[str, Any],
            ]
    ] = None,
        `Input` or `Parameter` objects that hold parameter inputs. When a dictionary is specified all the key/value
        pairs will be transformed into `Parameter`s. The `key` will be the `name` field of the `Parameter` while the
        `value` will be the `value` field of the `Parameter.
    outputs: Optional[List[Union[Parameter, Artifact]]] = None
        Any outputs to set on the DAG at a global level.
    """

    def __init__(
        self,
        name: str,
        inputs: Optional[
            Union[
                List[Union[Parameter, Artifact]],
                List[Union[Parameter, Artifact, Dict[str, Any]]],
                Dict[str, Any],
            ]
        ] = None,
        outputs: Optional[List[Union[Parameter, Artifact]]] = None,
    ):
        self.name = validate_name(name)
        self.inputs = [] if inputs is None else self._parse_inputs(inputs)
        self.outputs = outputs or []
        self.tasks: List["Task"] = []

    def _build_templates(self) -> List[IoArgoprojWorkflowV1alpha1Template]:
        """Assembles the templates from sub-DAGs of the DAG"""
        templates = [t for t in [t._build_template() for t in self.tasks] if t]
        # Assemble the templates from sub-dags
        sub_templates = [t.dag._build_templates() for t in self.tasks if t.dag]
        sub_templates = [t for sublist in sub_templates for t in sublist]  # flatten
        return templates + sub_templates

    def _build_dag_tasks(self) -> Optional[List[IoArgoprojWorkflowV1alpha1DAGTask]]:
        """Assembles all the DAG tasks"""
        return [t for t in [t._build_dag_task() for t in self.tasks if not t.is_exit_task] if t]

    def _build_volume_claim_templates(self) -> List[PersistentVolumeClaim]:
        """Assembles the volume claim templates"""
        # make sure we only have unique names
        vcs = dict()
        for t in self.tasks:
            for v in t._build_volume_claim_templates():
                vcs[v.metadata.name] = v

        # sub-claims:
        sub_volume_claims = [t.dag._build_volume_claim_templates() for t in self.tasks if t.dag]
        for volume_claims in sub_volume_claims:
            for v in volume_claims:
                vcs[v.metadata.name] = v
        return list(vcs.values())

    def _build_persistent_volume_claims(self) -> List[ArgoVolume]:
        """Assembles the persistent volume claim templates"""
        # Make sure we only have unique names
        pvcs = dict()
        for t in self.tasks:
            for v in t._build_persistent_volume_claims():
                pvcs[v.name] = v

        # sub-claims:
        sub_volume_claims = [t.dag._build_persistent_volume_claims() for t in self.tasks if t.dag]
        for volume_claims in sub_volume_claims:
            for v in volume_claims:
                pvcs[v.name] = v

        return list(pvcs.values())

    def build(self) -> List[IoArgoprojWorkflowV1alpha1Template]:
        """Assembles the main DAG/workflow template"""
        dag = IoArgoprojWorkflowV1alpha1Template(
            name=self.name, dag=IoArgoprojWorkflowV1alpha1DAGTemplate(tasks=self._build_dag_tasks())
        )
        inputs = self._build_inputs()
        if inputs:
            setattr(dag, "inputs", inputs)
        outputs = self._build_outputs()
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

    def add_task(self, t: "Task") -> "DAG":
        """Add a task to the DAG. Note that tasks are added automatically when the DAG context is used"""
        self.tasks.append(t)
        return self

    def add_tasks(self, *ts: "Task") -> "DAG":
        """Add a collection of tasks to the DAG.

        Note that tasks are added automatically when the DAG context is used
        """
        self.tasks.extend(ts)
        return self

    def get_parameter(self, name: str) -> Parameter:
        """Returns a DAG output as a `Parameter` to use an input somewhere else"""
        if next((p for p in self.outputs if p.name == name), None) is None:
            raise KeyError(f"Could not assemble a parameter as `{name}` is not a DAG output")
        return Parameter(name, value=f"{{{{inputs.parameters.{name}}}}}")

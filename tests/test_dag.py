from unittest import mock

import pytest
from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1DAGTask,
    IoArgoprojWorkflowV1alpha1Inputs,
    IoArgoprojWorkflowV1alpha1Outputs,
    IoArgoprojWorkflowV1alpha1Template,
    PersistentVolumeClaim,
    Volume as ArgoVolume,
)

from hera.workflows.artifact import Artifact
from hera.workflows.dag import DAG
from hera.workflows.parameter import Parameter
from hera.workflows.task import Task
from hera.workflows.volumes import EmptyDirVolume, Volume


class TestDAG:
    def test_builds_templates(self):
        dag = DAG("test").add_tasks(Task("a"), Task("b"), Task("c"))
        templates = dag._build_templates()
        assert len(templates) == 3
        assert templates[0].name == "a"
        assert templates[1].name == "b"
        assert templates[2].name == "c"

    def test_builds_templates_with_subtemplates(self):
        subdag = DAG("subdag").add_tasks(Task("d"), Task("e"), Task("f"))
        dag = DAG("test").add_tasks(Task("a"), Task("b"), Task("c", dag=subdag))
        templates = dag._build_templates()
        names = {"a", "b", "d", "e", "f"}

        assert len(templates) == 5
        for template in templates:
            assert isinstance(template, IoArgoprojWorkflowV1alpha1Template)
            assert template.name in names

    def test_builds_dag_tasks(self):
        dag = DAG("test").add_tasks(Task("a"), Task("b"), Task("c"))
        dag_tasks = dag._build_dag_tasks()
        names = {"a", "b", "c"}
        assert len(dag_tasks) == 3
        for dag_task in dag_tasks:
            assert isinstance(dag_task, IoArgoprojWorkflowV1alpha1DAGTask)
            assert dag_task.name in names

    def test_builds_dag_tasks_with_exit(self):
        dag = DAG("test").add_tasks(Task("a"), Task("b"))
        c = Task("c")
        x = Task("exit")
        c.on_exit(x)

        dag.add_tasks(c, x)
        dag_tasks = dag._build_dag_tasks()
        names = {"a", "b", "c"}
        assert len(dag_tasks) == 3
        for dag_task in dag_tasks:
            assert isinstance(dag_task, IoArgoprojWorkflowV1alpha1DAGTask)
            assert dag_task.name in names

    def test_build_volume_claim_templates(self):
        dag = DAG("test").add_tasks(Task("a", volumes=[Volume("/m", size="1Gi")]))
        templates = dag._build_volume_claim_templates()
        assert len(templates) == 1
        assert isinstance(templates[0], PersistentVolumeClaim)

    def test_build_volume_claim_templates_with_subvolumes(self):
        subdag = DAG("test1").add_tasks(Task("a", volumes=[Volume("/m", size="1Gi")]))
        dag = DAG("test2").add_tasks(Task("b", volumes=[Volume("/m", size="1Gi")], dag=subdag))
        templates = dag._build_volume_claim_templates()
        assert len(templates) == 2
        assert isinstance(templates[0], PersistentVolumeClaim)
        assert isinstance(templates[1], PersistentVolumeClaim)

    def test_build_volume_unique_claim_templates_with_subvolumes(self):
        subdag = DAG("test1").add_tasks(Task("a", volumes=[Volume("/m", name="vol", size="1Gi")]))
        dag = DAG("test2").add_tasks(Task("b", volumes=[Volume("/m", name="vol", size="1Gi")], dag=subdag))
        templates = dag._build_volume_claim_templates()
        assert len(templates) == 1
        assert isinstance(templates[0], PersistentVolumeClaim)

    def test_build_persistent_volume_claims(self):
        dag = DAG("test").add_tasks(Task("a", volumes=[EmptyDirVolume()]))
        claims = dag._build_persistent_volume_claims()
        assert len(claims) == 1
        assert isinstance(claims[0], ArgoVolume)

    def test_build_persistent_volume_claims_with_subvolumes(self):
        subdag = DAG("test1").add_tasks(Task("a", volumes=[EmptyDirVolume()]))
        dag = DAG("test2").add_tasks(Task("b", volumes=[EmptyDirVolume()], dag=subdag))
        claims = dag._build_persistent_volume_claims()
        assert len(claims) == 2
        assert isinstance(claims[0], ArgoVolume)
        assert isinstance(claims[1], ArgoVolume)

    def test_build_persistent_volume_claims_with_unique_subvolumes(self):
        subdag = DAG("test1").add_tasks(Task("a", volumes=[EmptyDirVolume(name="vol")]))
        dag = DAG("test2").add_tasks(Task("b", volumes=[EmptyDirVolume(name="vol")], dag=subdag))
        claims = dag._build_persistent_volume_claims()
        assert len(claims) == 1
        assert isinstance(claims[0], ArgoVolume)

    def test_build(self):
        dag = DAG(
            "test",
            inputs=[Parameter("p1"), Artifact("a1", "/a1"), {"a": 1, "b": 2}],
            outputs=[Parameter("p2", value="p2"), Artifact("a2", "/a2")],
        )
        templates = dag.build()
        assert len(templates) == 1
        template = templates[0]
        assert isinstance(template, IoArgoprojWorkflowV1alpha1Template)
        assert hasattr(template, "inputs")
        assert isinstance(template.inputs, IoArgoprojWorkflowV1alpha1Inputs)
        assert hasattr(template, "outputs")
        assert isinstance(template.outputs, IoArgoprojWorkflowV1alpha1Outputs)

    @mock.patch("hera.workflows.dag_context", return_value=mock.Mock())
    def test_enter(self, ctx_mock: mock.Mock):
        with DAG("test") as dag:
            assert dag.in_context
            ctx_mock.enter.assert_called_once()

    @mock.patch("hera.workflows.dag_context", return_value=mock.Mock())
    def test_exit(self, ctx_mock: mock.Mock):
        with DAG("test") as dag:
            assert dag.in_context
            ctx_mock.enter.assert_called_once()
        assert not dag.in_context
        ctx_mock.exit.assert_called_once()

    def test_add_task(self):
        dag = DAG("test").add_task(Task("a"))
        assert len(dag.tasks) == 1
        assert dag.tasks[0].name == "a"

    def test_add_tasks(self):
        dag = DAG("test").add_tasks(Task("a"), Task("b"))
        assert len(dag.tasks) == 2
        assert dag.tasks[0].name == "a"
        assert dag.tasks[1].name == "b"

    def test_get_parameter_returns_expected_parameter(self):
        dag = DAG("test", outputs=[Parameter("a", value="42")])
        param = dag.get_parameter("a")
        assert isinstance(param, Parameter)
        assert param.name == "a"
        assert param.value == "{{inputs.parameters.a}}"

    def test_get_parameter_raises_on_param_not_found(self):
        dag = DAG("test")
        with pytest.raises(KeyError) as e:
            dag.get_parameter("a")
        assert str(e.value) == "'Could not assemble a parameter as `a` is not a DAG output'"

    def test_adds(self):
        dag = DAG("test").add_tasks(Task("t1"), Task("t2"))
        assert len(dag.tasks) == 2

        dag = DAG("test").add_task(Task("t"))
        assert len(dag.tasks) == 1

    def test_parses_inputs_as_expected(self):
        d = DAG("d", inputs={"a": 1, "b": 2})
        assert len(d.inputs) == 2
        assert all([isinstance(i, Parameter) for i in d.inputs])

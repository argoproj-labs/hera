import json
from textwrap import dedent
from unittest import mock
from unittest.mock import Mock

import pytest
import yaml
from argo_workflows.models import HostAlias as ArgoHostAlias
from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1Workflow,
    IoArgoprojWorkflowV1alpha1WorkflowSpec,
    PodSecurityContext,
)

from hera.dag import DAG
from hera.host_alias import HostAlias
from hera.host_config import set_global_service_account_name
from hera.metric import Metric, Metrics
from hera.parameter import Parameter
from hera.task import Task
from hera.template_ref import TemplateRef
from hera.toleration import GPUToleration
from hera.ttl_strategy import TTLStrategy
from hera.volume_claim_gc import VolumeClaimGCStrategy
from hera.volumes import (
    ConfigMapVolume,
    EmptyDirVolume,
    ExistingVolume,
    SecretVolume,
    Volume,
)
from hera.workflow import Workflow, WorkflowSecurityContext


@pytest.fixture
def workflow_security_context_kwargs():
    return {
        "run_as_user": 1000,
        "run_as_group": 1001,
        "fs_group": 1002,
        "run_as_non_root": False,
    }


class TestWorkflow:
    def test_wf_contains_specified_service_account(self, setup):
        with Workflow("w", service_account_name="w-sa") as w:
            expected_sa = "w-sa"
            assert w.service_account_name == expected_sa
            assert w.build().spec.service_account_name == expected_sa

        set_global_service_account_name("w-sa")
        with Workflow("w") as w:
            expected_sa = "w-sa"
            assert w.service_account_name == expected_sa
            assert w.build().spec.service_account_name == expected_sa
        set_global_service_account_name(None)

    def test_wf_does_not_contain_sa_if_one_is_not_specified(self, setup):
        with Workflow("w") as w:
            assert not hasattr(w.build().spec, "service_account_name")

    def test_wf_contains_specified_security_context(self, workflow_security_context_kwargs, setup):
        wsc = WorkflowSecurityContext(**workflow_security_context_kwargs)
        with Workflow("w", security_context=wsc) as w:
            expected_security_context = PodSecurityContext(**workflow_security_context_kwargs)
            assert w.build().spec.security_context == expected_security_context

    @pytest.mark.parametrize("set_only", ["run_as_user", "run_as_group", "fs_group", "run_as_non_root"])
    def test_wf_specified_partial_security_context(self, set_only, workflow_security_context_kwargs, setup):
        one_param_kwargs = {set_only: workflow_security_context_kwargs[set_only]}
        wsc = WorkflowSecurityContext(**one_param_kwargs)
        with Workflow("w", security_context=wsc) as w:
            expected_security_context = PodSecurityContext(**one_param_kwargs)
            assert w.build().spec.security_context == expected_security_context

    def test_wf_does_not_contain_specified_security_context(self, setup):
        with Workflow("w") as w:
            assert "security_context" not in w.build().spec

    def test_wf_adds_specified_tasks(self, no_op):
        n = 3
        ts = [Task(f"t{i}", no_op) for i in range(n)]
        w = Workflow('w')
        w.add_tasks(*ts)

        assert len(w.dag.tasks) == n
        for i, t in enumerate(w.dag.tasks):
            assert ts[i].name == t.name

    def test_wf_adds_task_volume(self, w, no_op):
        t = Task("t", no_op, volumes=[Volume(name="v", size="1Gi", mount_path="/", storage_class_name="custom")])
        w.add_task(t)

        claim = w.build().spec.volume_claim_templates[0]
        assert claim.spec.access_modes == ["ReadWriteOnce"]
        assert claim.spec.resources.requests["storage"] == "1Gi"
        assert claim.spec.storage_class_name == "custom"
        assert claim.metadata.name == "v"

    def test_wf_adds_task_secret_volume(self, w, no_op):
        t = Task("t", no_op, volumes=[SecretVolume(name="s", secret_name="sn", mount_path="/")])
        w.add_task(t)

        vol = w.build().spec.volumes[0]
        assert vol.name == "s"
        assert vol.secret.secret_name == "sn"

    def test_wf_adds_task_config_map_volume(self, w):
        with Workflow("w") as w:
            Task("t", "print(42)", volumes=[ConfigMapVolume(config_map_name="cmn", mount_path="/")])
        wb = w.build()
        assert wb.spec["volumes"][0].name
        assert wb.spec["volumes"][0].config_map.name == "cmn"

    def test_wf_adds_task_existing_checkpoints_staging_volume(self, w, no_op):
        t = Task("t", no_op, volumes=[ExistingVolume(name="v", mount_path="/")])
        w.add_task(t)

        vol = w.build().spec.volumes[0]
        assert vol.name == "v"
        assert vol.persistent_volume_claim.claim_name == "v"

    def test_wf_adds_task_existing_checkpoints_prod_volume(self, w, no_op):
        t = Task(
            "t",
            no_op,
            volumes=[ExistingVolume(name="vol", mount_path="/")],
        )
        w.add_task(t)

        vol = w.build().spec.volumes[0]
        assert vol.name == "vol"
        assert vol.persistent_volume_claim.claim_name == "vol"

    def test_wf_adds_task_empty_dir_volume(w, no_op):
        with Workflow("w") as w:
            Task("t", no_op, volumes=[EmptyDirVolume(name="v")])

        vol = w.build().spec.volumes[0]
        assert vol.name == "v"
        assert not hasattr(vol.empty_dir, "size_limit")
        assert vol.empty_dir.medium == "Memory"

    def test_wf_contains_specified_labels(self):
        with Workflow("w", labels={"foo": "bar"}) as w:
            expected_labels = {"foo": "bar"}
            assert w.build().metadata.labels == expected_labels

    def test_wf_contains_specified_annotations(self):
        with Workflow("w", annotations={"foo": "bar"}) as w:
            expected_annotations = {"foo": "bar"}
            assert w.build().metadata.annotations == expected_annotations

    def test_wf_submit_with_default(self):
        with Workflow("w") as w:
            w.service = Mock()
        w.create()
        assert w.generated_name is None
        w.service.create_workflow.assert_called_with(w.build())

    def test_wf_submit_with_generate_name(self):
        returned_wf = Mock()
        returned_wf.metadata = {"name": "w-12345"}
        with Workflow("w-", generate_name=True) as w:
            w.service = Mock()
            w.service.create_workflow = Mock(return_value=returned_wf)
        w.create()
        assert w.generated_name == "w-12345"

    def test_wf_adds_image_pull_secrets(self):
        with Workflow("w", image_pull_secrets=["secret0", "secret1"]) as w:
            secrets = [{"name": secret.name} for secret in w.build().spec.get("image_pull_secrets")]
            assert secrets[0] == {"name": "secret0"}
            assert secrets[1] == {"name": "secret1"}

    def test_wf_adds_ttl_strategy(self):
        with Workflow(
            "w",
            ttl_strategy=TTLStrategy(seconds_after_completion=5, seconds_after_failure=10, seconds_after_success=15),
        ) as w:
            expected_ttl_strategy = {
                "seconds_after_completion": 5,
                "seconds_after_failure": 10,
                "seconds_after_success": 15,
            }

            assert w.build().spec.ttl_strategy._data_store == expected_ttl_strategy

    def test_wf_adds_volume_claim_gc_strategy_on_workflow_completion(self):
        with Workflow("w", volume_claim_gc_strategy=VolumeClaimGCStrategy.OnWorkflowCompletion) as w:
            expected_volume_claim_gc = {"strategy": "OnWorkflowCompletion"}
            assert w.build().spec.volume_claim_gc._data_store == expected_volume_claim_gc

    def test_wf_adds_volume_claim_gc_strategy_on_workflow_success(self):
        with Workflow("w", volume_claim_gc_strategy=VolumeClaimGCStrategy.OnWorkflowSuccess) as w:
            expected_volume_claim_gc = {"strategy": "OnWorkflowSuccess"}
            assert w.build().spec.volume_claim_gc._data_store == expected_volume_claim_gc

    def test_wf_adds_host_aliases(self):
        with Workflow(
            "w",
            host_aliases=[
                HostAlias(hostnames=["host1", "host2"], ip="0.0.0.0"),
                HostAlias(hostnames=["host3"], ip="1.1.1.1"),
            ],
        ) as w:
            assert w.build().spec.host_aliases[0] == ArgoHostAlias(hostnames=["host1", "host2"], ip="0.0.0.0")
            assert w.build().spec.host_aliases[1] == ArgoHostAlias(hostnames=["host3"], ip="1.1.1.1")

    def test_wf_add_task_with_template_ref(self, w):
        t = Task("t", template_ref=TemplateRef(name="name", template="template"))
        w.add_task(t)

        assert w.dag.tasks[0] == t

        # Not add a Task with TemplateRef to w.spec.templates
        # Note: w.spec.templates[0] is a template of dag
        assert len(w.build().spec.templates) == 1

    def test_wf_resets_context_indicator(self):
        with Workflow("w") as w:
            assert w.in_context
        assert not w.in_context

    def test_wf_raises_on_create_in_context(self):
        with Workflow("w") as w:
            with pytest.raises(ValueError) as e:
                w.create()
            assert str(e.value) == "Cannot invoke `create` when using a Hera context"

    def test_wf_sets_parameter(self):
        with Workflow("w", parameters=[Parameter("a", "42")]) as w:
            assert w.parameters is not None
            assert len(w.parameters) == 1
            assert w.parameters[0].name == "a"
            assert w.parameters[0].value == "42"
            assert w.get_parameter("a").value == "{{workflow.parameters.a}}"
            assert hasattr(w.build().spec, "arguments")
            assert len(getattr(w.build().spec, "arguments").parameters) == 1

    def test_build_metadata_returns_expected_object_meta(self, setup):
        with Workflow("test", labels={"test": "test"}, annotations={"test": "test"}) as w:
            meta = w._build_metadata(use_name=True)
            assert hasattr(meta, "name")
            assert meta.name == "test"
            assert hasattr(meta, "labels")
            assert meta.labels == {"test": "test"}
            assert hasattr(meta, "annotations")
            assert meta.annotations == {"test": "test"}
            assert not hasattr(meta, "generate_name")

            meta = w._build_metadata(use_name=False)
            assert not hasattr(meta, "name")
            assert hasattr(meta, "labels")
            assert meta.labels == {"test": "test"}
            assert hasattr(meta, "annotations")
            assert meta.annotations == {"test": "test"}

        with Workflow("test", generate_name=True) as w:
            meta = w._build_metadata(use_name=True)
            assert hasattr(meta, "generate_name")
            assert meta.generate_name == "test"

    def test_service_sets_service_as_expected(self, setup):
        with Workflow("w") as w:
            assert w._service is None
            assert w.service is not None

    def test_build_spec(self, affinity):
        with Workflow(
            "w",
            parallelism=50,
            node_selectors={"a": "b"},
            affinity=affinity,
            tolerations=[GPUToleration],
            active_deadline_seconds=42,
            metrics=Metrics(
                [
                    Metric(
                        'a',
                        'b',
                    ),
                    Metric(
                        'c',
                        'd',
                    ),
                ]
            ),
        ) as w:
            spec = w._build_spec()
            assert hasattr(spec, "parallelism")
            assert spec.parallelism == 50
            assert hasattr(spec, "affinity")
            assert spec.affinity is not None
            assert hasattr(spec, "tolerations")
            assert len(spec.tolerations) == 1
            assert hasattr(spec, "affinity")
            assert hasattr(spec, "active_deadline_seconds")
            assert spec.active_deadline_seconds == 42
            assert hasattr(spec, "node_selector")
            assert spec.node_selector == {"a": "b"}
            assert hasattr(spec, "metrics")

        with Workflow("w") as w:
            spec = w._build_spec()
            assert isinstance(spec, IoArgoprojWorkflowV1alpha1WorkflowSpec)
            assert not hasattr(spec, "parallelism")
            assert not hasattr(spec, "affinity")
            assert not hasattr(spec, "tolerations")
            assert not hasattr(spec, "node_selector")
            assert not hasattr(spec, "active_deadline_seconds")
            assert not hasattr(spec, "on_exit")

        with Workflow("w") as w:
            w.on_exit(Task("x"))
            spec = w._build_spec()
            assert isinstance(spec, IoArgoprojWorkflowV1alpha1WorkflowSpec)
            assert hasattr(spec, "on_exit")
            assert spec.on_exit == "x"
            assert not hasattr(spec, "metrics")

    def test_enter_sets_expected_fields(self):
        w = Workflow("w", dag=DAG("d"))
        assert not w.in_context
        assert w.dag.name == 'd'

    def test_on_exit(self):
        with Workflow("w") as w1:
            x = Task("x")
            w1.on_exit(x)
            assert w1.exit_task == "x"
            assert x.is_exit_task

        with Workflow("w") as w2:
            w2.on_exit(DAG("d"))
            assert w2.exit_task == "d"

        with Workflow("w") as w3:
            with pytest.raises(ValueError) as e:
                w3.on_exit(42)  # type: ignore
            assert "Unrecognized exit type" in str(e.value)
            assert "supported types are `Task` and `DAG`" in str(e.value)

    def test_delete(self):
        service = mock.Mock()
        service.delete_workflow = mock.Mock()
        with Workflow("w", service=service) as w:
            w.delete()
        w.service.delete_workflow.assert_called_once_with("w")

    def test_lint(self):
        service = mock.Mock()
        service.lint_workflow = mock.Mock()
        with Workflow("w", service=service) as w:
            w.lint()
        w.service.lint_workflow.assert_called_once_with(w.build())

    def test_parameter(self):
        with Workflow("w", parameters=[Parameter("a", value="42")]) as w:
            p = w.get_parameter("a")
            assert isinstance(p, Parameter)
            assert p.name == "a"
            assert p.value == "{{workflow.parameters.a}}"

        with pytest.raises(KeyError) as e:
            Workflow("w").get_parameter("a")
        assert str(e.value) == "'`a` is not a valid workflow parameter'"

        with pytest.raises(KeyError) as e:
            Workflow("w", parameters=[Parameter("a", value="42")]).get_parameter("b")
        assert str(e.value) == "'`b` is not a valid workflow parameter'"

    def test_get_name(self):
        assert Workflow("w").get_name() == "{{workflow.name}}"

    def test_workflow_adjusts_input_metrics(self):
        with Workflow('w', metrics=Metric('a', 'b')) as w:
            assert isinstance(w.metrics, Metrics)

        with Workflow('w', metrics=[Metric('a', 'b')]) as w:
            assert isinstance(w.metrics, Metrics)

        with Workflow('w', metrics=Metrics([Metric('a', 'b')])) as w:
            assert isinstance(w.metrics, Metrics)

    def test_workflow_sets_dag_name(self):
        w = Workflow("w", dag_name="dag-name")
        assert w.dag.name == "dag-name"
        assert w.build().spec.templates[0].name == "dag-name"

        w = Workflow("w")
        assert w.dag.name == "w"
        assert w.build().spec.templates[0].name == "w"

    def test_build(self):
        wf = Workflow("w").build()
        assert isinstance(wf, IoArgoprojWorkflowV1alpha1Workflow)
        assert hasattr(wf, "api_version")
        assert wf.api_version == "argoproj.io/v1alpha1"
        assert isinstance(wf.api_version, str)
        assert hasattr(wf, "kind")
        assert isinstance(wf.kind, str)
        assert wf.kind == "Workflow"

    def test_raises_on_no_yaml_available(self):
        import yaml

        import hera.workflow

        # TODO: is there a better way to temporarily mock/patch this value to make this test more atomic?
        hera.workflow._yaml = None
        with pytest.raises(ImportError) as e:
            Workflow('w').to_yaml()
        assert (
            str(e.value) == "Attempted to use `to_yaml` but PyYAML is not available. "
            "Install `hera-workflows[yaml]` to install the extra dependency"
        )

        hera.workflow._yaml = yaml

    @pytest.mark.parametrize(
        ["roundtripper"],
        (
            pytest.param(lambda w: w.to_dict(), id="dict"),
            pytest.param(lambda w: json.loads(w.to_json()), id="json"),
            pytest.param(lambda w: yaml.safe_load(w.to_yaml()), id="yaml"),
        ),
    )
    def test_serialization(self, roundtripper):
        def hello():
            print("Hello, Hera!")

        with Workflow("hello-hera", node_selectors={'a_b_c': 'a_b_c'}, labels={'a_b_c': 'a_b_c'}) as w:
            Task("t", hello)

        expected = {
            "metadata": {"name": "hello-hera", "labels": {"a_b_c": "a_b_c"}},
            "spec": {
                "entrypoint": "hello-hera",
                "templates": [
                    {
                        "name": "t",
                        "script": {
                            "image": "python:3.7",
                            "source": dedent(
                                """\
                                import os
                                import sys
                                sys.path.append(os.getcwd())
                                print("Hello, Hera!")
                                """
                            ),
                            "command": ["python"],
                        },
                    },
                    {"name": "hello-hera", "dag": {"tasks": [{"name": "t", "template": "t"}]}},
                ],
                "nodeSelector": {"a_b_c": "a_b_c"},
            },
            "apiVersion": "argoproj.io/v1alpha1",
            "kind": "Workflow",
        }
        assert expected == roundtripper(w)

    def test_workflow_applies_hooks(self, global_config):
        def hook1(w: Workflow) -> None:
            w.service_account_name = "abc"

        def hook2(w: Workflow) -> None:
            w.labels = {'abc': '123'}

        global_config.workflow_post_init_hooks = [hook1, hook2]
        w = Workflow('w')
        assert w.service_account_name == "abc"
        assert w.labels == {'abc': '123'}

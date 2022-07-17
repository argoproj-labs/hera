from unittest.mock import Mock

import pytest
from argo_workflows.model.pod_security_context import PodSecurityContext
from argo_workflows.models import HostAlias as ArgoHostAlias

from hera import (
    ConfigMapVolume,
    EmptyDirVolume,
    ExistingVolume,
    HostAlias,
    Operator,
    Resources,
    SecretVolume,
    Task,
    TemplateRef,
    TTLStrategy,
    Variable,
    Volume,
    VolumeClaimGCStrategy,
    Workflow,
    WorkflowSecurityContext,
    WorkflowStatus,
)


def test_wf_contains_specified_service_account(ws):
    w = Workflow("w", service=ws, service_account_name="w-sa")

    expected_sa = "w-sa"
    assert w.spec.service_account_name == expected_sa
    assert w.spec.templates[0].service_account_name == expected_sa


def test_wf_does_not_contain_sa_if_one_is_not_specified(ws):
    with Workflow("w", service=ws) as w:
        assert not hasattr(w.spec, "service_account_name")


@pytest.fixture
def workflow_security_context_kwargs():
    sc_kwargs = {
        "run_as_user": 1000,
        "run_as_group": 1001,
        "fs_group": 1002,
        "run_as_non_root": False,
    }
    return sc_kwargs


def test_wf_contains_specified_security_context(ws, workflow_security_context_kwargs):
    wsc = WorkflowSecurityContext(**workflow_security_context_kwargs)
    with Workflow("w", service=ws, security_context=wsc) as w:
        expected_security_context = PodSecurityContext(**workflow_security_context_kwargs)
        assert w.spec.security_context == expected_security_context


@pytest.mark.parametrize("set_only", ["run_as_user", "run_as_group", "fs_group", "run_as_non_root"])
def test_wf_specified_partial_security_context(ws, set_only, workflow_security_context_kwargs):
    one_param_kwargs = {set_only: workflow_security_context_kwargs[set_only]}
    wsc = WorkflowSecurityContext(**one_param_kwargs)
    w = Workflow("w", service=ws, security_context=wsc)
    expected_security_context = PodSecurityContext(**one_param_kwargs)
    assert w.spec.security_context == expected_security_context


def test_wf_does_not_contain_specified_security_context(ws):
    w = Workflow("w", service=ws)

    assert "security_context" not in w.spec


def test_wf_does_not_add_empty_task(w):
    t = None
    w.add_task(t)

    assert not w.dag_template.tasks


def test_wf_adds_specified_tasks(w, no_op):
    n = 3
    ts = [Task(f"t{i}", no_op) for i in range(n)]
    w.add_tasks(*ts)

    assert len(w.dag_template.tasks) == n
    for i, t in enumerate(w.dag_template.tasks):
        assert ts[i].name == t.name


def test_wf_adds_task_volume(w, no_op):
    t = Task(
        "t",
        no_op,
        resources=Resources(volumes=[Volume(name="v", size="1Gi", mount_path="/", storage_class_name="custom")]),
    )
    w.add_task(t)

    claim = w.spec.volume_claim_templates[0]
    assert claim.spec.access_modes == ["ReadWriteOnce"]
    assert claim.spec.resources.requests["storage"] == "1Gi"
    assert claim.spec.storage_class_name == "custom"
    assert claim.metadata.name == "v"


def test_wf_adds_task_secret_volume(w, no_op):
    t = Task("t", no_op, resources=Resources(volumes=[SecretVolume(name="s", secret_name="sn", mount_path="/")]))
    w.add_task(t)

    vol = w.spec.volumes[0]
    assert vol.name == "s"
    assert vol.secret.secret_name == "sn"


def test_wf_adds_task_config_map_volume(w):
    t = Task("t", resources=Resources(volumes=[ConfigMapVolume(config_map_name="cmn", mount_path="/")]))
    w.add_task(t)

    assert w.spec.volumes[0].name
    assert w.spec.volumes[0].config_map.name == "cmn"


def test_wf_adds_task_existing_checkpoints_staging_volume(w, no_op):
    t = Task("t", no_op, resources=Resources(volumes=[ExistingVolume(name="v", mount_path="/")]))
    w.add_task(t)

    vol = w.spec.volumes[0]
    assert vol.name == "v"
    assert vol.persistent_volume_claim.claim_name == "v"


def test_wf_adds_task_existing_checkpoints_prod_volume(w, no_op):
    t = Task(
        "t",
        no_op,
        resources=Resources(volumes=[ExistingVolume(name="vol", mount_path="/")]),
    )
    w.add_task(t)

    vol = w.spec.volumes[0]
    assert vol.name == "vol"
    assert vol.persistent_volume_claim.claim_name == "vol"


def test_wf_adds_task_empty_dir_volume(w, no_op):
    t = Task("t", no_op, resources=Resources(volumes=[EmptyDirVolume(name="v")]))
    w.add_task(t)

    vol = w.spec.volumes[0]
    assert vol.name == "v"
    assert not vol.empty_dir.size_limit
    assert vol.empty_dir.medium == "Memory"


def test_wf_adds_head(w, no_op):
    t1 = Task("t1", no_op)
    t2 = Task("t2", no_op)
    t1 >> t2
    w.add_tasks(t1, t2)

    h = Task("head", no_op)
    w.add_head(h)

    assert t1.argo_task.dependencies == ["head"]
    assert t2.argo_task.dependencies == ["t1", "head"]


def test_wf_adds_tail(w, no_op):
    t1 = Task("t1", no_op)
    t2 = Task("t2", no_op)
    t1 >> t2
    w.add_tasks(t1, t2)

    t = Task("tail", no_op)
    w.add_tail(t)

    assert not hasattr(t1.argo_task, "dependencies")
    assert t2.argo_task.dependencies == ["t1"]
    assert t.argo_task.dependencies == ["t2"]


def test_wf_overwrites_head_and_tail(w, no_op):
    t1 = Task("t1", no_op)
    t2 = Task("t2", no_op)
    t1 >> t2
    w.add_tasks(t1, t2)

    h2 = Task("head2", no_op)
    w.add_head(h2)

    assert t1.argo_task.dependencies == ["head2"]
    assert t2.argo_task.dependencies == ["t1", "head2"]

    h1 = Task("head1", no_op)
    w.add_head(h1)

    assert h2.argo_task.dependencies == ["head1"]
    assert t1.argo_task.dependencies == ["head2", "head1"]
    assert t2.argo_task.dependencies == ["t1", "head2", "head1"]


def test_wf_contains_specified_labels(ws):
    w = Workflow("w", service=ws, labels={"foo": "bar"})

    expected_labels = {"foo": "bar"}
    assert w.metadata.labels == expected_labels


def test_wf_contains_specified_annotations(ws):
    w = Workflow("w", service=ws, annotations={"foo": "bar"})

    expected_annotations = {"foo": "bar"}
    assert w.metadata.annotations == expected_annotations


def test_wf_submit_with_default(ws):
    w = Workflow("w", service=ws, labels={"foo": "bar"})
    w.service = Mock()
    w.create()
    w.service.create.assert_called_with(w.workflow)


def test_wf_adds_image_pull_secrets(ws):
    w = Workflow("w", service=ws, image_pull_secrets=["secret0", "secret1"])
    secrets = [{"name": secret.name} for secret in w.spec.get("image_pull_secrets")]
    assert secrets[0] == {"name": "secret0"}
    assert secrets[1] == {"name": "secret1"}


def test_wf_adds_ttl_strategy(ws):
    w = Workflow(
        "w",
        service=ws,
        ttl_strategy=TTLStrategy(seconds_after_completion=5, seconds_after_failure=10, seconds_after_success=15),
    )

    expected_ttl_strategy = {
        "seconds_after_completion": 5,
        "seconds_after_failure": 10,
        "seconds_after_success": 15,
    }

    assert w.spec.ttl_strategy._data_store == expected_ttl_strategy


def test_wf_adds_volume_claim_gc_strategy_on_workflow_completion(ws):
    w = Workflow("w", service=ws, volume_claim_gc_strategy=VolumeClaimGCStrategy.OnWorkflowCompletion)

    expected_volume_claim_gc = {"strategy": "OnWorkflowCompletion"}

    assert w.spec.volume_claim_gc._data_store == expected_volume_claim_gc


def test_wf_adds_volume_claim_gc_strategy_on_workflow_success(ws):
    w = Workflow("w", service=ws, volume_claim_gc_strategy=VolumeClaimGCStrategy.OnWorkflowSuccess)

    expected_volume_claim_gc = {"strategy": "OnWorkflowSuccess"}

    assert w.spec.volume_claim_gc._data_store == expected_volume_claim_gc


def test_wf_adds_host_aliases(ws):
    w = Workflow(
        "w",
        service=ws,
        host_aliases=[
            HostAlias(hostnames=["host1", "host2"], ip="0.0.0.0"),
            HostAlias(hostnames=["host3"], ip="1.1.1.1"),
        ],
    )

    assert w.spec.host_aliases[0] == ArgoHostAlias(hostnames=["host1", "host2"], ip="0.0.0.0")
    assert w.spec.host_aliases[1] == ArgoHostAlias(hostnames=["host3"], ip="1.1.1.1")


def test_wf_add_task_with_template_ref(w):
    t = Task("t", template_ref=TemplateRef(name="name", template="template"))
    w.add_task(t)

    assert w.dag_template.tasks[0] == t.argo_task

    # Not add a Task with TemplateRef to w.spec.templates
    # Note: w.spec.templates[0] is a template of dag
    assert len(w.spec.templates) == 1


def test_wf_adds_exit_tasks(w, no_op):
    t1 = Task("t1", no_op)
    w.add_task(t1)

    t2 = Task(
        "t2",
        no_op,
        resources=Resources(volumes=[SecretVolume(name="my-vol", mount_path="/mnt/my-vol", secret_name="my-secret")]),
    ).on_workflow_status(Operator.equals, WorkflowStatus.Succeeded)
    w.on_exit(t2)

    t3 = Task(
        "t3", no_op, resources=Resources(volumes=[Volume(name="my-vol", mount_path="/mnt/my-vol", size="5Gi")])
    ).on_workflow_status(Operator.equals, WorkflowStatus.Failed)
    w.on_exit(t3)

    assert len(w.exit_template.dag.tasks) == 2
    assert len(w.spec.templates) == 5
    assert len(w.spec.volume_claim_templates) == 1
    assert len(w.spec.volumes) == 1


def test_wf_catches_tasks_without_exit_status_conditions(w, no_op):
    t1 = Task("t1", no_op)
    w.add_task(t1)

    t2 = Task("t2", no_op)
    with pytest.raises(AssertionError) as e:
        w.on_exit(t2)
    assert (
        str(e.value)
        == "Each exit task must contain a workflow status condition. Use `task.on_workflow_status(...)` to set it"
    )


def test_wf_catches_exit_tasks_without_parent_workflow_tasks(w, no_op):
    t1 = Task("t1", no_op)
    with pytest.raises(AssertionError) as e:
        w.on_exit(t1)
    assert str(e.value) == "Cannot add an exit condition to empty workflows"


def test_wf_contains_expected_default_exit_template(w):
    assert w.exit_template
    assert w.exit_template.name == "exit-template"
    assert w.exit_template.dag.tasks == []


def test_wf_contains_expected_node_selectors(ws):
    w = Workflow("w", ws, node_selectors={"foo": "bar"})
    assert w.template.node_selector == {"foo": "bar"}
    assert w.exit_template.node_selector == {"foo": "bar"}
    assert w.dag_template.node_selector == {"foo": "bar"}


def test_wf_contains_expected_affinity(ws, affinity):
    w = Workflow("w", ws, affinity=affinity)
    assert w.affinity == affinity
    assert hasattr(w.template, "affinity")
    assert hasattr(w.exit_template, "affinity")


def test_wf_raises_on_double_context(ws):
    with Workflow("w", service=ws):
        with pytest.raises(ValueError) as e:
            with Workflow("w2", service=ws):
                pass
        assert "Hera context already defined with workflow" in str(e.value)


def test_wf_resets_context_indicator(ws):
    with Workflow("w", service=ws) as w:
        assert w.in_context
    assert not w.in_context


def test_wf_raises_on_create_in_context(ws):
    with Workflow("w", service=ws) as w:
        with pytest.raises(ValueError) as e:
            w.create()
        assert str(e.value) == "Cannot invoke `create` when using a Hera context"


def test_wf_sets_variables_as_global_args(ws):
    with Workflow("w", service=ws, variables=[Variable("a", "42")]) as w:
        assert len(w.variables) == 1
        assert w.variables[0].name == "a"
        assert w.variables[0].value == "42"
        assert hasattr(w.spec, "arguments")
        assert len(getattr(w.spec, "arguments").parameters) == 1

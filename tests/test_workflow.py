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
    Volume,
    VolumeClaimGCStrategy,
    Workflow,
    WorkflowSecurityContext,
    WorkflowStatus,
    set_global_host,
    set_global_token,
)
from hera.parameter import Parameter


def test_wf_contains_specified_service_account(setup):
    with Workflow("w", service_account_name="w-sa") as w:
        expected_sa = "w-sa"
        assert w.service_account_name == expected_sa
        assert w.build().spec.service_account_name == expected_sa


def test_wf_does_not_contain_sa_if_one_is_not_specified(setup):
    with Workflow("w") as w:
        assert not hasattr(w.build().spec, "service_account_name")


@pytest.fixture
def workflow_security_context_kwargs():
    sc_kwargs = {
        "run_as_user": 1000,
        "run_as_group": 1001,
        "fs_group": 1002,
        "run_as_non_root": False,
    }
    return sc_kwargs


def test_wf_contains_specified_security_context(workflow_security_context_kwargs, setup):
    wsc = WorkflowSecurityContext(**workflow_security_context_kwargs)
    with Workflow("w", security_context=wsc) as w:
        expected_security_context = PodSecurityContext(**workflow_security_context_kwargs)
        assert w.build().spec.security_context == expected_security_context


@pytest.mark.parametrize("set_only", ["run_as_user", "run_as_group", "fs_group", "run_as_non_root"])
def test_wf_specified_partial_security_context(set_only, workflow_security_context_kwargs, setup):
    one_param_kwargs = {set_only: workflow_security_context_kwargs[set_only]}
    wsc = WorkflowSecurityContext(**one_param_kwargs)
    with Workflow("w", security_context=wsc) as w:
        expected_security_context = PodSecurityContext(**one_param_kwargs)
        assert w.build().spec.security_context == expected_security_context


def test_wf_does_not_contain_specified_security_context(setup):
    with Workflow("w") as w:
        assert "security_context" not in w.build().spec


def test_wf_does_not_add_empty_task(w):
    t = None
    w.add_task(t)
    assert not w.tasks


def test_wf_adds_specified_tasks(w, no_op):
    n = 3
    ts = [Task(f"t{i}", no_op) for i in range(n)]
    w.add_tasks(*ts)

    assert len(w.tasks) == n
    for i, t in enumerate(w.tasks):
        assert ts[i].name == t.name


def test_wf_adds_task_volume(w, no_op):
    t = Task("t", no_op, volumes=[Volume(name="v", size="1Gi", mount_path="/", storage_class_name="custom")])
    w.add_task(t)

    claim = w.build().spec.volume_claim_templates[0]
    assert claim.spec.access_modes == ["ReadWriteOnce"]
    assert claim.spec.resources.requests["storage"] == "1Gi"
    assert claim.spec.storage_class_name == "custom"
    assert claim.metadata.name == "v"


def test_wf_adds_task_secret_volume(w, no_op):
    t = Task("t", no_op, volumes=[SecretVolume(name="s", secret_name="sn", mount_path="/")])
    w.add_task(t)

    vol = w.build().spec.volumes[0]
    assert vol.name == "s"
    assert vol.secret.secret_name == "sn"


def test_wf_adds_task_config_map_volume(w):
    with Workflow("w") as w:
        Task("t", "print(42)", volumes=[ConfigMapVolume(config_map_name="cmn", mount_path="/")])
    wb = w.build()
    assert wb.spec["volumes"][0].name
    assert wb.spec["volumes"][0].config_map.name == "cmn"


def test_wf_adds_task_existing_checkpoints_staging_volume(w, no_op):
    t = Task("t", no_op, volumes=[ExistingVolume(name="v", mount_path="/")])
    w.add_task(t)

    vol = w.build().spec.volumes[0]
    assert vol.name == "v"
    assert vol.persistent_volume_claim.claim_name == "v"


def test_wf_adds_task_existing_checkpoints_prod_volume(w, no_op):
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


def test_wf_contains_specified_labels():
    with Workflow("w", labels={"foo": "bar"}) as w:
        expected_labels = {"foo": "bar"}
        assert w.build().metadata.labels == expected_labels


def test_wf_contains_specified_annotations():
    with Workflow("w", annotations={"foo": "bar"}) as w:
        expected_annotations = {"foo": "bar"}
        assert w.build().metadata.annotations == expected_annotations


def test_wf_submit_with_default():
    with Workflow("w", labels={"foo": "bar"}) as w:
        w.service = Mock()
    w.create()
    w.service.create_workflow.assert_called_with(w.build())


def test_wf_adds_image_pull_secrets():
    with Workflow("w", image_pull_secrets=["secret0", "secret1"]) as w:
        secrets = [{"name": secret.name} for secret in w.build().spec.get("image_pull_secrets")]
        assert secrets[0] == {"name": "secret0"}
        assert secrets[1] == {"name": "secret1"}


def test_wf_adds_ttl_strategy():
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


def test_wf_adds_volume_claim_gc_strategy_on_workflow_completion():
    with Workflow("w", volume_claim_gc_strategy=VolumeClaimGCStrategy.OnWorkflowCompletion) as w:
        expected_volume_claim_gc = {"strategy": "OnWorkflowCompletion"}
        assert w.build().spec.volume_claim_gc._data_store == expected_volume_claim_gc


def test_wf_adds_volume_claim_gc_strategy_on_workflow_success():
    with Workflow("w", volume_claim_gc_strategy=VolumeClaimGCStrategy.OnWorkflowSuccess) as w:
        expected_volume_claim_gc = {"strategy": "OnWorkflowSuccess"}
        assert w.build().spec.volume_claim_gc._data_store == expected_volume_claim_gc


def test_wf_adds_host_aliases():
    with Workflow(
        "w",
        host_aliases=[
            HostAlias(hostnames=["host1", "host2"], ip="0.0.0.0"),
            HostAlias(hostnames=["host3"], ip="1.1.1.1"),
        ],
    ) as w:
        assert w.build().spec.host_aliases[0] == ArgoHostAlias(hostnames=["host1", "host2"], ip="0.0.0.0")
        assert w.build().spec.host_aliases[1] == ArgoHostAlias(hostnames=["host3"], ip="1.1.1.1")


def test_wf_add_task_with_template_ref(w):
    t = Task("t", template_ref=TemplateRef(name="name", template="template"))
    w.add_task(t)

    assert w.tasks[0] == t

    # Not add a Task with TemplateRef to w.spec.templates
    # Note: w.spec.templates[0] is a template of dag
    assert len(w.build().spec.templates) == 1


def test_wf_resets_context_indicator():
    with Workflow("w") as w:
        assert w.in_context
    assert not w.in_context


def test_wf_raises_on_create_in_context():
    with Workflow("w") as w:
        with pytest.raises(ValueError) as e:
            w.create()
        assert str(e.value) == "Cannot invoke `create` when using a Hera context"


def test_wf_sets_parameter():
    with Workflow("w", parameters=[Parameter("a", "42")]) as w:
        assert w.parameters is not None
        assert len(w.parameters) == 1
        assert w.parameters[0].name == "a"
        assert w.parameters[0].value == "42"
        assert w.get_parameter("a").value == "{{workflow.parameters.a}}"
        assert hasattr(w.build().spec, "arguments")
        assert len(getattr(w.build().spec, "arguments").parameters) == 1

from unittest.mock import Mock

import pytest
from argo_workflows.model.io_argoproj_workflow_v1alpha1_cron_workflow import (
    IoArgoprojWorkflowV1alpha1CronWorkflow,
)
from argo_workflows.model.io_argoproj_workflow_v1alpha1_cron_workflow_spec import (
    IoArgoprojWorkflowV1alpha1CronWorkflowSpec,
)
from argo_workflows.model.io_argoproj_workflow_v1alpha1_workflow_spec import (
    IoArgoprojWorkflowV1alpha1WorkflowSpec,
)
from argo_workflows.model.object_meta import ObjectMeta
from argo_workflows.models import HostAlias as ArgoHostAlias

from hera import (
    CronWorkflow,
    EmptyDirVolume,
    ExistingVolume,
    HostAlias,
    Operator,
    Resources,
    SecretVolume,
    Task,
    TTLStrategy,
    Variable,
    Volume,
    WorkflowStatus,
)


def test_wf_contains_specified_service_account(cws, schedule):
    w = CronWorkflow("w", schedule, service=cws, service_account_name="w-sa")

    expected_sa = "w-sa"
    assert w.spec.service_account_name == expected_sa
    assert w.spec.templates[0].service_account_name == expected_sa


def test_wf_does_not_contain_sa_if_one_is_not_specified(cws, schedule):
    w = CronWorkflow("w", schedule, service=cws)

    assert not hasattr(w.spec.templates[0], "service_account_name")


def test_cwf_does_not_add_empty_task(cw):
    t = None
    cw.add_task(t)

    assert not cw.dag_template.tasks


def test_cwf_adds_specified_tasks(cw, no_op):
    n = 3
    ts = [Task(f"t{i}", no_op) for i in range(n)]
    cw.add_tasks(*ts)

    assert len(cw.dag_template.tasks) == n
    for i, t in enumerate(cw.dag_template.tasks):
        assert ts[i].name == t.name


def test_cwf_adds_task_volume(cw, no_op):
    t = Task(
        "t",
        no_op,
        resources=Resources(volumes=[Volume(name="v", size="1Gi", mount_path="/", storage_class_name="custom")]),
    )
    cw.add_task(t)

    claim = cw.spec.volume_claim_templates[0]
    assert claim.spec.access_modes == ["ReadWriteOnce"]
    assert claim.spec.resources.requests["storage"] == "1Gi"
    assert claim.spec.storage_class_name == "custom"
    assert claim.metadata.name == "v"


def test_wf_adds_task_secret_volume(cw, no_op):
    t = Task("t", no_op, resources=Resources(volumes=[SecretVolume(name="s", secret_name="sn", mount_path="/")]))
    cw.add_task(t)

    vol = cw.spec.volumes[0]
    assert vol.name == "s"
    assert vol.secret.secret_name == "sn"


def test_cwf_adds_task_existing_checkpoints_staging_volume(cw, no_op):
    t = Task("t", no_op, resources=Resources(volumes=[ExistingVolume(name="v", mount_path="/")]))
    cw.add_task(t)

    vol = cw.spec.volumes[0]
    assert vol.name == "v"
    assert vol.persistent_volume_claim.claim_name == "v"


def test_cwf_adds_task_existing_checkpoints_prod_volume(cw, no_op):
    t = Task(
        "t",
        no_op,
        resources=Resources(volumes=[ExistingVolume(name="vol", mount_path="/")]),
    )
    cw.add_task(t)

    vol = cw.spec.volumes[0]
    assert vol.name == "vol"
    assert vol.persistent_volume_claim.claim_name == "vol"


def test_cwf_adds_task_empty_dir_volume(cw, no_op):
    t = Task("t", no_op, resources=Resources(volumes=[EmptyDirVolume(name="v")]))
    cw.add_task(t)

    vol = cw.spec.volumes[0]
    assert vol.name == "v"
    assert not vol.empty_dir.size_limit
    assert vol.empty_dir.medium == "Memory"


def test_cwf_adds_head(cw, no_op):
    t1 = Task("t1", no_op)
    t2 = Task("t2", no_op)
    t1.next(t2)
    cw.add_tasks(t1, t2)

    h = Task("head", no_op)
    cw.add_head(h)

    assert t1.argo_task.dependencies == ["head"]
    assert t2.argo_task.dependencies == ["t1", "head"]


def test_cwf_adds_tail(cw, no_op):
    t1 = Task("t1", no_op)
    t2 = Task("t2", no_op)
    t1.next(t2)
    cw.add_tasks(t1, t2)

    t = Task("tail", no_op)
    cw.add_tail(t)

    assert not hasattr(t1.argo_task, "dependencies")
    assert t2.argo_task.dependencies == ["t1"]
    assert t.argo_task.dependencies == ["t2"]


def test_cwf_overwrites_head_and_tail(cw, no_op):
    t1 = Task("t1", no_op)
    t2 = Task("t2", no_op)
    t1.next(t2)
    cw.add_tasks(t1, t2)

    h2 = Task("head2", no_op)
    cw.add_head(h2)

    assert t1.argo_task.dependencies == ["head2"]
    assert t2.argo_task.dependencies == ["t1", "head2"]

    h1 = Task("head1", no_op)
    cw.add_head(h1)

    assert h2.argo_task.dependencies == ["head1"]
    assert t1.argo_task.dependencies == ["head2", "head1"]
    assert t2.argo_task.dependencies == ["t1", "head2", "head1"]


def test_cwf_valid_field_set(cws):
    cw = CronWorkflow("cw", "* * * * *", service=cws, parallelism=33)
    assert cw.schedule == "* * * * *"
    assert cw.timezone is None
    assert cw.service == cws
    assert cw.parallelism == 33


def test_cwf_valid_timezone_set(cws):
    cw = CronWorkflow("cw", "* * * * *", timezone="UTC", service=cws)
    assert cw.timezone == "UTC"


def test_cwf_invalid_timezone_set(cws):
    with pytest.raises(ValueError) as e:
        cw = CronWorkflow("cw", "* * * * *", timezone="foobar", service=cws)
    assert "foobar is not a valid timezone" in str(e)


def test_cwf_contains_specified_labels(ws):
    w = CronWorkflow("w", schedule="* * * * *", service=ws, labels={"foo": "bar"})

    expected_labels = {"foo": "bar"}
    assert w.metadata.labels == expected_labels


def test_cwf_contains_specified_annotations(ws):
    w = CronWorkflow("w", schedule="* * * * *", service=ws, annotations={"foo": "bar"})

    expected_annotations = {"foo": "bar"}
    assert w.metadata.annotations == expected_annotations


def test_cwf_create_with_defaults(ws):
    w = CronWorkflow("w", schedule="* * * * *", service=ws, labels={"foo": "bar"})
    w.service = Mock()
    w.create()
    w.service.create.assert_called_with(w.workflow)


def test_cwf_update_with_defaults(ws):
    w = CronWorkflow("w", schedule="* * * * *", service=ws, labels={"foo": "bar"})
    w.service.get_workflow = Mock(  # type: ignore
        return_value=IoArgoprojWorkflowV1alpha1CronWorkflow(
            metadata=ObjectMeta(
                resourceVersion="rv",
                uid="uid",
            ),
            spec=IoArgoprojWorkflowV1alpha1CronWorkflowSpec(
                schedule="", workflow_spec=IoArgoprojWorkflowV1alpha1WorkflowSpec()
            ),
        )
    )
    w.service.update = Mock()  # type: ignore
    w.update()

    w.service.get_workflow.assert_called_with(w.name)
    w.service.update.assert_called_with(w.name, w.workflow)
    assert w.workflow.metadata["resourceVersion"] == "rv"
    assert w.workflow.metadata["uid"] == "uid"


def test_cwf_update_with_specified_name_and_namespace(ws):
    w = CronWorkflow("w", schedule="* * * * *", service=ws, labels={"foo": "bar"})
    w.service.get_workflow = Mock(  # type: ignore
        return_value=IoArgoprojWorkflowV1alpha1CronWorkflow(
            metadata=ObjectMeta(
                resourceVersion="rv",
                uid="uid",
            ),
            spec=IoArgoprojWorkflowV1alpha1CronWorkflowSpec(
                schedule="", workflow_spec=IoArgoprojWorkflowV1alpha1WorkflowSpec()
            ),
        )
    )
    w.service.update = Mock()  # type: ignore
    w.update(name="cwf")

    w.service.get_workflow.assert_called_with("cwf")
    w.service.update.assert_called_with("cwf", w.workflow)
    assert w.workflow.metadata["resourceVersion"] == "rv"
    assert w.workflow.metadata["uid"] == "uid"


def test_cwf_resume_with_defaults(ws):
    w = CronWorkflow("w", schedule="* * * * *", service=ws, labels={"foo": "bar"})
    w.service = Mock()
    w.resume()
    w.service.resume.assert_called_with(w.name)


def test_cwf_suspend_with_defaults(ws):
    w = CronWorkflow("w", schedule="* * * * *", service=ws, labels={"foo": "bar"})
    w.service = Mock()
    w.suspend()
    w.service.suspend.assert_called_with(w.name)


def test_cwf_adds_image_pull_secrets(ws):
    w = CronWorkflow("w", schedule="* * * * *", service=ws, image_pull_secrets=["secret0", "secret1"])
    secrets = [{"name": secret.name} for secret in w.spec.get("image_pull_secrets")]
    assert secrets[0] == {"name": "secret0"}
    assert secrets[1] == {"name": "secret1"}


def test_wf_adds_ttl_strategy(ws):
    w = CronWorkflow(
        "w",
        schedule="* * * * *",
        service=ws,
        ttl_strategy=TTLStrategy(seconds_after_completion=5, seconds_after_failure=10, seconds_after_success=15),
    )

    expected_ttl_strategy = {
        "seconds_after_completion": 5,
        "seconds_after_failure": 10,
        "seconds_after_success": 15,
    }

    assert w.spec.ttl_strategy._data_store == expected_ttl_strategy


def test_wf_adds_host_aliases(ws):
    w = CronWorkflow(
        "w",
        schedule="* * * * *",
        service=ws,
        host_aliases=[
            HostAlias(hostnames=["host1", "host2"], ip="0.0.0.0"),
            HostAlias(hostnames=["host3"], ip="1.1.1.1"),
        ],
    )

    assert w.spec.host_aliases[0] == ArgoHostAlias(hostnames=["host1", "host2"], ip="0.0.0.0")
    assert w.spec.host_aliases[1] == ArgoHostAlias(hostnames=["host3"], ip="1.1.1.1")


def test_wf_adds_exit_tasks(cw, no_op):
    t1 = Task("t1", no_op)
    cw.add_task(t1)

    t2 = Task(
        "t2",
        no_op,
        resources=Resources(volumes=[SecretVolume(name="my-vol", mount_path="/mnt/my-vol", secret_name="my-secret")]),
    ).on_workflow_status(Operator.equals, WorkflowStatus.Succeeded)
    cw.on_exit(t2)

    t3 = Task(
        "t3", no_op, resources=Resources(volumes=[Volume(name="my-vol", mount_path="/mnt/my-vol", size="5Gi")])
    ).on_workflow_status(Operator.equals, WorkflowStatus.Failed)
    cw.on_exit(t3)

    assert len(cw.exit_template.dag.tasks) == 2
    assert len(cw.spec.templates) == 5


def test_wf_catches_tasks_without_exit_status_conditions(cw, no_op):
    t1 = Task("t1", no_op)
    cw.add_task(t1)

    t2 = Task("t2", no_op)
    with pytest.raises(AssertionError) as e:
        cw.on_exit(t2)
    assert (
        str(e.value)
        == "Each exit task must contain a workflow status condition. Use `task.on_workflow_status(...)` to set it"
    )


def test_wf_catches_exit_tasks_without_parent_workflow_tasks(cw, no_op):
    t1 = Task("t1", no_op)
    with pytest.raises(AssertionError) as e:
        cw.on_exit(t1)
    assert str(e.value) == "Cannot add an exit condition to empty workflows"


def test_wf_contains_expected_default_exit_template(cw):
    assert cw.exit_template
    assert cw.exit_template.name == "exit-template"
    assert cw.exit_template.dag.tasks == []


def test_wf_contains_expected_node_selectors(cws, schedule):
    w = CronWorkflow("w", schedule, cws, node_selectors={"foo": "bar"})
    assert w.template.node_selector == {"foo": "bar"}
    assert w.exit_template.node_selector == {"foo": "bar"}
    assert w.dag_template.node_selector == {"foo": "bar"}


def test_wf_adds_affinity(cws, schedule, affinity):
    w = CronWorkflow("w", schedule, cws, affinity=affinity)
    assert w.affinity == affinity
    assert hasattr(w.template, "affinity")
    assert hasattr(w.exit_template, "affinity")


def test_wf_raises_on_double_context(cws, schedule):
    with CronWorkflow("w", schedule, service=cws):
        with pytest.raises(ValueError) as e:
            with CronWorkflow("w2", schedule, service=cws):
                pass
        assert "Hera context already defined with workflow" in str(e.value)


def test_wf_resets_context_indicator(cws, schedule):
    with CronWorkflow("w", schedule, service=cws) as w:
        assert w.in_context
    assert not w.in_context


def test_wf_raises_on_create_in_context(cws, schedule):
    with CronWorkflow("w", schedule, service=cws) as w:
        with pytest.raises(ValueError) as e:
            w.create()
        assert str(e.value) == "Cannot invoke `create` when using a Hera context"


def test_wf_sets_variables_as_global_args(cws, schedule):
    with CronWorkflow("w", schedule, service=cws, variables=[Variable("a", "42")]) as w:
        assert len(w.variables) == 1
        assert w.variables[0].name == "a"
        assert w.variables[0].value == "42"
        assert hasattr(w.spec, "arguments")
        assert len(getattr(w.spec, "arguments").parameters) == 1

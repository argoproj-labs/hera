from unittest.mock import Mock

import pytest
from argo_workflows.model.pod_security_context import PodSecurityContext

from hera.operator import Operator
from hera.resources import Resources
from hera.security_context import WorkflowSecurityContext
from hera.task import Task
from hera.ttl_strategy import TTLStrategy
from hera.volumes import SecretVolume, Volume
from hera.workflow_status import WorkflowStatus
from hera.workflow_template import WorkflowTemplate


def test_wft_contains_specified_service_account(wts):
    w = WorkflowTemplate('w', service=wts, service_account_name='w-sa')

    expected_sa = 'w-sa'
    assert w.spec.service_account_name == expected_sa
    assert w.spec.templates[0].service_account_name == expected_sa


def test_wft_does_not_contain_sa_if_one_is_not_specified(ws):
    w = WorkflowTemplate('w', service=ws)

    assert not hasattr(w.spec, 'service_account_name')


@pytest.fixture
def workflow_security_context_kwargs():
    sc_kwargs = {
        "run_as_user": 1000,
        "run_as_group": 1001,
        "fs_group": 1002,
        "run_as_non_root": False,
    }
    return sc_kwargs


def test_wft_contains_specified_security_context(wts, workflow_security_context_kwargs):
    wsc = WorkflowSecurityContext(**workflow_security_context_kwargs)
    w = WorkflowTemplate('w', service=wts, security_context=wsc)

    expected_security_context = PodSecurityContext(**workflow_security_context_kwargs)
    assert w.spec.security_context == expected_security_context


@pytest.mark.parametrize("set_only", ["run_as_user", "run_as_group", "fs_group", "run_as_non_root"])
def test_wft_specified_partial_security_context(ws, set_only, workflow_security_context_kwargs):
    one_param_kwargs = {set_only: workflow_security_context_kwargs[set_only]}
    wsc = WorkflowSecurityContext(**one_param_kwargs)
    w = WorkflowTemplate('w', service=ws, security_context=wsc)
    expected_security_context = PodSecurityContext(**one_param_kwargs)
    assert w.spec.security_context == expected_security_context


def test_wft_does_not_contain_specified_security_context(wt, wts):
    assert "security_context" not in wt.spec


def test_wft_does_not_add_empty_task(w):
    t = None
    w.add_task(t)

    assert not w.dag_template.tasks


def test_wft_adds_specified_tasks(w, no_op):
    n = 3
    ts = [Task(f't{i}', no_op) for i in range(n)]
    w.add_tasks(*ts)

    assert len(w.dag_template.tasks) == n
    for i, t in enumerate(w.dag_template.tasks):
        assert ts[i].name == t.name


def test_wft_contains_specified_labels(wts):
    w = WorkflowTemplate('w', service=wts, labels={'foo': 'bar'})

    expected_labels = {'foo': 'bar'}
    assert w.metadata.labels == expected_labels


def test_wft_submit_with_default(wts):
    w = WorkflowTemplate('w', service=wts, labels={'foo': 'bar'}, namespace="test")
    w.service = Mock()
    w.create()
    w.service.create.assert_called_with(w.workflow_template, w.namespace)


def test_wft_adds_ttl_strategy(wts):
    w = WorkflowTemplate(
        'w',
        service=wts,
        ttl_strategy=TTLStrategy(seconds_after_completion=5, seconds_after_failure=10, seconds_after_success=15),
    )

    expected_ttl_strategy = {
        'seconds_after_completion': 5,
        'seconds_after_failure': 10,
        'seconds_after_success': 15,
    }

    assert w.spec.ttl_strategy._data_store == expected_ttl_strategy


def test_wf_adds_exit_tasks(wt, no_op):
    t1 = Task('t1', no_op)
    wt.add_task(t1)

    t2 = Task(
        't2',
        no_op,
        resources=Resources(volumes=[SecretVolume(name='my-vol', mount_path='/mnt/my-vol', secret_name='my-secret')]),
    ).on_workflow_status(Operator.equals, WorkflowStatus.Succeeded)
    wt.on_exit(t2)

    t3 = Task(
        't3', no_op, resources=Resources(volumes=[Volume(name='my-vol', mount_path='/mnt/my-vol', size='5Gi')])
    ).on_workflow_status(Operator.equals, WorkflowStatus.Failed)
    wt.on_exit(t3)

    assert len(wt.exit_template.dag.tasks) == 2
    assert len(wt.spec.templates) == 5


def test_wf_catches_tasks_without_exit_status_conditions(wt, no_op):
    t1 = Task('t1', no_op)
    wt.add_task(t1)

    t2 = Task('t2', no_op)
    with pytest.raises(AssertionError) as e:
        wt.on_exit(t2)
    assert (
        str(e.value)
        == 'Each exit task must contain a workflow status condition. Use `task.on_workflow_status(...)` to set it'
    )


def test_wf_catches_exit_tasks_without_parent_workflow_tasks(wt, no_op):
    t1 = Task('t1', no_op)
    with pytest.raises(AssertionError) as e:
        wt.on_exit(t1)
    assert str(e.value) == 'Cannot add an exit condition to empty workflows'


def test_wf_contains_expected_default_exit_template(wt):
    assert wt.exit_template
    assert wt.exit_template.name == 'exit-template'
    assert wt.exit_template.dag.tasks == []

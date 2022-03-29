from unittest.mock import Mock

import pytest
from argo_workflows.model.pod_security_context import PodSecurityContext

from hera.resources import Resources
from hera.security_context import WorkflowSecurityContext
from hera.task import Task
from hera.workflow_template import WorkflowTemplate


def test_wft_contains_specified_service_account(ws):
    w = WorkflowTemplate('w', service=ws, service_account_name='w-sa')

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


def test_wft_contains_specified_security_context(ws, workflow_security_context_kwargs):
    wsc = WorkflowSecurityContext(**workflow_security_context_kwargs)
    w = WorkflowTemplate('w', service=ws, security_context=wsc)

    expected_security_context = PodSecurityContext(**workflow_security_context_kwargs)
    assert w.spec.security_context == expected_security_context


@pytest.mark.parametrize("set_only", ["run_as_user", "run_as_group", "fs_group", "run_as_non_root"])
def test_wft_specified_partial_security_context(ws, set_only, workflow_security_context_kwargs):
    one_param_kwargs = {set_only: workflow_security_context_kwargs[set_only]}
    wsc = WorkflowSecurityContext(**one_param_kwargs)
    w = WorkflowTemplate('w', service=ws, security_context=wsc)
    expected_security_context = PodSecurityContext(**one_param_kwargs)
    assert w.spec.security_context == expected_security_context


def test_wft_does_not_contain_specified_security_context(ws):
    w = WorkflowTemplate('w', service=ws)

    assert "security_context" not in w.spec


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


def test_wft_contains_specified_labels(ws):
    w = WorkflowTemplate('w', service=ws, labels={'foo': 'bar'})

    expected_labels = {'foo': 'bar'}
    assert w.metadata.labels == expected_labels


def test_wft_submit_with_default(ws):
    w = WorkflowTemplate('w', service=ws, labels={'foo': 'bar'}, namespace="test")
    w.service = Mock()
    w.create()
    w.service.create.assert_called_with(w.workflow_template, w.namespace)

from unittest.mock import Mock

import pytest
from argo_workflows.model.pod_security_context import PodSecurityContext

from hera.resources import Resources
from hera.security_context import WorkflowSecurityContext
from hera.task import Task
from hera.volumes import (
    ConfigMapVolume,
    EmptyDirVolume,
    ExistingVolume,
    SecretVolume,
    Volume,
)
from hera.workflow import Workflow


def test_wf_contains_specified_service_account(ws):
    w = Workflow('w', service=ws, service_account_name='w-sa')

    expected_sa = 'w-sa'
    assert w.spec.service_account_name == expected_sa
    assert w.spec.templates[0].service_account_name == expected_sa


def test_wf_does_not_contain_sa_if_one_is_not_specified(ws):
    w = Workflow('w', service=ws)

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


def test_wf_contains_specified_security_context(ws, workflow_security_context_kwargs):
    wsc = WorkflowSecurityContext(**workflow_security_context_kwargs)
    w = Workflow('w', service=ws, security_context=wsc)

    expected_security_context = PodSecurityContext(**workflow_security_context_kwargs)
    assert w.spec.security_context == expected_security_context


@pytest.mark.parametrize("set_only", ["run_as_user", "run_as_group", "fs_group", "run_as_non_root"])
def test_wf_specified_partial_security_context(ws, set_only, workflow_security_context_kwargs):
    one_param_kwargs = {set_only: workflow_security_context_kwargs[set_only]}
    wsc = WorkflowSecurityContext(**one_param_kwargs)
    w = Workflow('w', service=ws, security_context=wsc)
    expected_security_context = PodSecurityContext(**one_param_kwargs)
    assert w.spec.security_context == expected_security_context


def test_wf_does_not_contain_specified_security_context(ws):
    w = Workflow('w', service=ws)

    assert "security_context" not in w.spec


def test_wf_does_not_add_empty_task(w):
    t = None
    w.add_task(t)

    assert not w.dag_template.tasks


def test_wf_adds_specified_tasks(w, no_op):
    n = 3
    ts = [Task(f't{i}', no_op) for i in range(n)]
    w.add_tasks(*ts)

    assert len(w.dag_template.tasks) == n
    for i, t in enumerate(w.dag_template.tasks):
        assert ts[i].name == t.name


def test_wf_adds_task_volume(w, no_op):
    t = Task(
        't',
        no_op,
        resources=Resources(volumes=[Volume(name='v', size='1Gi', mount_path='/', storage_class_name='custom')]),
    )
    w.add_task(t)

    claim = w.spec.volume_claim_templates[0]
    assert claim.spec.access_modes == ['ReadWriteOnce']
    assert claim.spec.resources.requests['storage'] == '1Gi'
    assert claim.spec.storage_class_name == 'custom'
    assert claim.metadata.name == 'v'


def test_wf_adds_task_secret_volume(w, no_op):
    t = Task('t', no_op, resources=Resources(volumes=[SecretVolume(name='s', secret_name='sn', mount_path='/')]))
    w.add_task(t)

    vol = w.spec.volumes[0]
    assert vol.name == 's'
    assert vol.secret.secret_name == 'sn'


def test_wf_adds_task_config_map_volume(w):
    t = Task('t', resources=Resources(volumes=[ConfigMapVolume(config_map_name='cmn', mount_path='/')]))
    w.add_task(t)

    assert w.spec.volumes[0].name
    assert w.spec.volumes[0].config_map.name == "cmn"


def test_wf_adds_task_existing_checkpoints_staging_volume(w, no_op):
    t = Task('t', no_op, resources=Resources(volumes=[ExistingVolume(name='v', mount_path='/')]))
    w.add_task(t)

    vol = w.spec.volumes[0]
    assert vol.name == 'v'
    assert vol.persistent_volume_claim.claim_name == 'v'


def test_wf_adds_task_existing_checkpoints_prod_volume(w, no_op):
    t = Task(
        't',
        no_op,
        resources=Resources(volumes=[ExistingVolume(name='vol', mount_path='/')]),
    )
    w.add_task(t)

    vol = w.spec.volumes[0]
    assert vol.name == 'vol'
    assert vol.persistent_volume_claim.claim_name == 'vol'


def test_wf_adds_task_empty_dir_volume(w, no_op):
    t = Task('t', no_op, resources=Resources(volumes=[EmptyDirVolume(name='v')]))
    w.add_task(t)

    vol = w.spec.volumes[0]
    assert vol.name == 'v'
    assert not vol.empty_dir.size_limit
    assert vol.empty_dir.medium == 'Memory'


def test_wf_adds_head(w, no_op):
    t1 = Task('t1', no_op)
    t2 = Task('t2', no_op)
    t1 >> t2
    w.add_tasks(t1, t2)

    h = Task('head', no_op)
    w.add_head(h)

    assert t1.argo_task.dependencies == ['head']
    assert t2.argo_task.dependencies == ['t1', 'head']


def test_wf_adds_tail(w, no_op):
    t1 = Task('t1', no_op)
    t2 = Task('t2', no_op)
    t1 >> t2
    w.add_tasks(t1, t2)

    t = Task('tail', no_op)
    w.add_tail(t)

    assert not hasattr(t1.argo_task, 'dependencies')
    assert t2.argo_task.dependencies == ['t1']
    assert t.argo_task.dependencies == ['t2']


def test_wf_overwrites_head_and_tail(w, no_op):
    t1 = Task('t1', no_op)
    t2 = Task('t2', no_op)
    t1 >> t2
    w.add_tasks(t1, t2)

    h2 = Task('head2', no_op)
    w.add_head(h2)

    assert t1.argo_task.dependencies == ['head2']
    assert t2.argo_task.dependencies == ['t1', 'head2']

    h1 = Task('head1', no_op)
    w.add_head(h1)

    assert h2.argo_task.dependencies == ['head1']
    assert t1.argo_task.dependencies == ['head2', 'head1']
    assert t2.argo_task.dependencies == ['t1', 'head2', 'head1']


def test_wf_contains_specified_labels(ws):
    w = Workflow('w', service=ws, labels={'foo': 'bar'})

    expected_labels = {'foo': 'bar'}
    assert w.metadata.labels == expected_labels


def test_wf_submit_with_default(ws):
    w = Workflow('w', service=ws, labels={'foo': 'bar'}, namespace="test")
    w.service = Mock()
    w.create()
    w.service.submit.assert_called_with(w.workflow, w.namespace)


def test_wf_adds_image_pull_secrets(ws):
    w = Workflow('w', service=ws, image_pull_secrets=['secret0', 'secret1'])
    secrets = [{'name': secret.name} for secret in w.spec.get('image_pull_secrets')]
    assert secrets[0] == {'name': 'secret0'}
    assert secrets[1] == {'name': 'secret1'}

import pytest

from hera.empty_dir_volume import EmptyDirVolume
from hera.existing_volume import ExistingVolume
from hera.resources import Resources
from hera.task import Task
from hera.volume import Volume
from hera.workflow import Workflow
from hera.workflow_service import WorkflowService


def test_wf_contains_specified_service_account(ws):
    w = Workflow('w', service=ws, service_account_name='w-sa')

    expected_sa = 'w-sa'
    assert w.spec.service_account_name == expected_sa
    assert w.spec.templates[0].service_account_name == expected_sa


def test_wf_does_not_contain_sa_if_one_is_not_specified(ws):
    w = Workflow('w', service=ws)

    expected_sa = None
    assert w.spec.service_account_name == expected_sa
    assert w.spec.templates[0].service_account_name == expected_sa


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
        resources=Resources(volume=Volume(name='v', size='1Gi', mount_path='/', storage_class_name='custom')),
    )
    w.add_task(t)

    claim = w.spec.volume_claim_templates[0]
    assert claim.spec.access_modes == ['ReadWriteOnce']
    assert claim.spec.resources.requests['storage'] == '1Gi'
    assert claim.spec.storage_class_name == 'custom'
    assert claim.metadata.name == 'v'


def test_wf_adds_task_existing_checkpoints_staging_volume(w, no_op):
    t = Task('t', no_op, resources=Resources(existing_volume=ExistingVolume(name='v', mount_path='/')))
    w.add_task(t)

    vol = w.spec.volumes[0]
    assert vol.name == 'v'
    assert vol.persistent_volume_claim.claim_name == 'v'


def test_wf_adds_task_existing_checkpoints_prod_volume(w, no_op):
    t = Task(
        't',
        no_op,
        resources=Resources(existing_volume=ExistingVolume(name='vol', mount_path='/')),
    )
    w.add_task(t)

    vol = w.spec.volumes[0]
    assert vol.name == 'vol'
    assert vol.persistent_volume_claim.claim_name == 'vol'


def test_wf_adds_task_empty_dir_volume(w, no_op):
    t = Task('t', no_op, resources=Resources(empty_dir_volume=EmptyDirVolume(name='v')))
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

    assert not t1.argo_task.dependencies
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

from unittest.mock import Mock

import pytest

from hera.cron_workflow import CronWorkflow
from hera.resources import Resources
from hera.task import Task
from hera.volumes import EmptyDirVolume, ExistingVolume, SecretVolume, Volume


def test_wf_contains_specified_service_account(cws, schedule):
    w = CronWorkflow('w', schedule, service=cws, service_account_name='w-sa')

    expected_sa = 'w-sa'
    assert w.spec.service_account_name == expected_sa
    assert w.spec.templates[0].service_account_name == expected_sa


def test_wf_does_not_contain_sa_if_one_is_not_specified(cws, schedule):
    w = CronWorkflow('w', schedule, service=cws)

    assert not hasattr(w.spec.templates[0], 'service_account_name')


def test_cwf_does_not_add_empty_task(cw):
    t = None
    cw.add_task(t)

    assert not cw.dag_template.tasks


def test_cwf_adds_specified_tasks(cw, no_op):
    n = 3
    ts = [Task(f't{i}', no_op) for i in range(n)]
    cw.add_tasks(*ts)

    assert len(cw.dag_template.tasks) == n
    for i, t in enumerate(cw.dag_template.tasks):
        assert ts[i].name == t.name


def test_cwf_adds_task_volume(cw, no_op):
    t = Task(
        't',
        no_op,
        resources=Resources(volume=Volume(name='v', size='1Gi', mount_path='/', storage_class_name='custom')),
    )
    cw.add_task(t)

    claim = cw.spec.volume_claim_templates[0]
    assert claim.spec.access_modes == ['ReadWriteOnce']
    assert claim.spec.resources.requests['storage'] == '1Gi'
    assert claim.spec.storage_class_name == 'custom'
    assert claim.metadata.name == 'v'


def test_wf_adds_task_secret_volume(cw, no_op):
    t = Task('t', no_op, resources=Resources(secret_volume=SecretVolume(name='s', secret_name='sn', mount_path='/')))
    cw.add_task(t)

    vol = cw.spec.volumes[0]
    assert vol.name == 's'
    assert vol.secret.secret_name == 'sn'


def test_cwf_adds_task_existing_checkpoints_staging_volume(cw, no_op):
    t = Task('t', no_op, resources=Resources(existing_volume=ExistingVolume(name='v', mount_path='/')))
    cw.add_task(t)

    vol = cw.spec.volumes[0]
    assert vol.name == 'v'
    assert vol.persistent_volume_claim.claim_name == 'v'


def test_cwf_adds_task_existing_checkpoints_prod_volume(cw, no_op):
    t = Task(
        't',
        no_op,
        resources=Resources(existing_volume=ExistingVolume(name='vol', mount_path='/')),
    )
    cw.add_task(t)

    vol = cw.spec.volumes[0]
    assert vol.name == 'vol'
    assert vol.persistent_volume_claim.claim_name == 'vol'


def test_cwf_adds_task_empty_dir_volume(cw, no_op):
    t = Task('t', no_op, resources=Resources(empty_dir_volume=EmptyDirVolume(name='v')))
    cw.add_task(t)

    vol = cw.spec.volumes[0]
    assert vol.name == 'v'
    assert not vol.empty_dir.size_limit
    assert vol.empty_dir.medium == 'Memory'


def test_cwf_adds_head(cw, no_op):
    t1 = Task('t1', no_op)
    t2 = Task('t2', no_op)
    t1.next(t2)
    cw.add_tasks(t1, t2)

    h = Task('head', no_op)
    cw.add_head(h)

    assert t1.argo_task.dependencies == ['head']
    assert t2.argo_task.dependencies == ['t1', 'head']


def test_cwf_adds_tail(cw, no_op):
    t1 = Task('t1', no_op)
    t2 = Task('t2', no_op)
    t1.next(t2)
    cw.add_tasks(t1, t2)

    t = Task('tail', no_op)
    cw.add_tail(t)

    assert not hasattr(t1.argo_task, 'dependencies')
    assert t2.argo_task.dependencies == ['t1']
    assert t.argo_task.dependencies == ['t2']


def test_cwf_overwrites_head_and_tail(cw, no_op):
    t1 = Task('t1', no_op)
    t2 = Task('t2', no_op)
    t1.next(t2)
    cw.add_tasks(t1, t2)

    h2 = Task('head2', no_op)
    cw.add_head(h2)

    assert t1.argo_task.dependencies == ['head2']
    assert t2.argo_task.dependencies == ['t1', 'head2']

    h1 = Task('head1', no_op)
    cw.add_head(h1)

    assert h2.argo_task.dependencies == ['head1']
    assert t1.argo_task.dependencies == ['head2', 'head1']
    assert t2.argo_task.dependencies == ['t1', 'head2', 'head1']


def test_cwf_valid_field_set(cws):
    cw = CronWorkflow('cw', "* * * * *", service=cws, parallelism=33)
    assert cw.schedule == "* * * * *"
    assert cw.timezone is None
    assert cw.service == cws
    assert cw.parallelism == 33


def test_cwf_valid_timezone_set(cws):
    cw = CronWorkflow('cw', "* * * * *", timezone="UTC", service=cws)
    assert cw.timezone == "UTC"


def test_cwf_invalid_timezone_set(cws):
    with pytest.raises(ValueError) as e:
        cw = CronWorkflow('cw', "* * * * *", timezone="foobar", service=cws)
    assert 'foobar is not a valid timezone' in str(e)


def test_cwf_contains_specified_labels(ws):
    w = CronWorkflow('w', schedule="* * * * *", service=ws, labels={'foo': 'bar'})

    expected_labels = {'foo': 'bar'}
    assert w.metadata.labels == expected_labels


def test_cwf_contains_specified_namespace(ws):
    w = CronWorkflow('w', schedule="* * * * *", service=ws, labels={'foo': 'bar'}, namespace="test")

    assert w.namespace == "test"


def test_cwf_create_with_defaults(ws):
    w = CronWorkflow('w', schedule="* * * * *", service=ws, labels={'foo': 'bar'}, namespace="test")
    w.service = Mock()
    w.create()
    w.service.create.assert_called_with(w.workflow, w.namespace)


def test_cwf_resume_with_defaults(ws):
    w = CronWorkflow('w', schedule="* * * * *", service=ws, labels={'foo': 'bar'}, namespace="test")
    w.service = Mock()
    w.resume()
    w.service.resume.assert_called_with(w.name, w.namespace)


def test_cwf_suspend_with_defaults(ws):
    w = CronWorkflow('w', schedule="* * * * *", service=ws, labels={'foo': 'bar'}, namespace="test")
    w.service = Mock()
    w.suspend()
    w.service.suspend.assert_called_with(w.name, w.namespace)

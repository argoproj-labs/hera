import pytest

from hera.v1.cron_workflow import CronWorkflow
from hera.v1.cron_workflow_service import CronWorkflowService
from hera.v1.empty_dir_volume import EmptyDirVolume
from hera.v1.existing_volume import ExistingVolume
from hera.v1.resources import Resources
from hera.v1.task import Task
from hera.v1.volume import Volume


@pytest.fixture
def cws():
    yield CronWorkflowService('abc.com', 'abc')


@pytest.fixture
def schedule():
    yield "* * * * *"


@pytest.fixture
def cw(cws, schedule):
    yield CronWorkflow('cw', schedule, service=cws)


def noop():
    pass


def test_wf_contains_specified_service_account(cws, schedule):
    w = CronWorkflow('w', schedule, service=cws, service_account_name='w-sa')

    expected_sa = 'w-sa'
    assert w.spec.service_account_name == expected_sa
    assert w.spec.templates[0].service_account_name == expected_sa


def test_wf_does_not_contain_sa_if_one_is_not_specified(cws, schedule):
    w = CronWorkflow('w', schedule, service=cws)

    expected_sa = None
    assert w.spec.service_account_name == expected_sa
    assert w.spec.templates[0].service_account_name == expected_sa


def test_cwf_does_not_add_empty_task(cw):
    t = None
    cw.add_task(t)

    assert not cw.dag_template.tasks


def test_cwf_adds_specified_tasks(cw):
    n = 3
    ts = [Task(f't{i}', noop) for i in range(n)]
    cw.add_tasks(*ts)

    assert len(cw.dag_template.tasks) == n
    for i, t in enumerate(cw.dag_template.tasks):
        assert ts[i].name == t.name


def test_cwf_adds_task_volume(cw):
    t = Task(
        't',
        noop,
        resources=Resources(volume=Volume(name='v', size='1Gi', mount_path='/', storage_class_name='custom')),
    )
    cw.add_task(t)

    claim = cw.spec.volume_claim_templates[0]
    assert claim.spec.access_modes == ['ReadWriteOnce']
    assert claim.spec.resources.requests['storage'] == '1Gi'
    assert claim.spec.storage_class_name == 'custom'
    assert claim.metadata.name == 'v'


def test_cwf_adds_task_existing_checkpoints_staging_volume(cw):
    t = Task('t', noop, resources=Resources(existing_volume=ExistingVolume(name='v', mount_path='/')))
    cw.add_task(t)

    vol = cw.spec.volumes[0]
    assert vol.name == 'v'
    assert vol.persistent_volume_claim.claim_name == 'v'


def test_cwf_adds_task_existing_checkpoints_prod_volume(cw):
    t = Task(
        't',
        noop,
        resources=Resources(existing_volume=ExistingVolume(name='vol', mount_path='/')),
    )
    cw.add_task(t)

    vol = cw.spec.volumes[0]
    assert vol.name == 'vol'
    assert vol.persistent_volume_claim.claim_name == 'vol'


def test_cwf_adds_task_empty_dir_volume(cw):
    t = Task('t', noop, resources=Resources(empty_dir_volume=EmptyDirVolume(name='v')))
    cw.add_task(t)

    vol = cw.spec.volumes[0]
    assert vol.name == 'v'
    assert not vol.empty_dir.size_limit
    assert vol.empty_dir.medium == 'Memory'


def test_cwf_adds_head(cw):
    t1 = Task('t1', noop)
    t2 = Task('t2', noop)
    t1.next(t2)
    cw.add_tasks(t1, t2)

    h = Task('head', noop)
    cw.add_head(h)

    assert t1.argo_task.dependencies == ['head']
    assert t2.argo_task.dependencies == ['t1', 'head']


def test_cwf_adds_tail(cw):
    t1 = Task('t1', noop)
    t2 = Task('t2', noop)
    t1.next(t2)
    cw.add_tasks(t1, t2)

    t = Task('tail', noop)
    cw.add_tail(t)

    assert not t1.argo_task.dependencies
    assert t2.argo_task.dependencies == ['t1']
    assert t.argo_task.dependencies == ['t2']


def test_cwf_overwrites_head_and_tail(cw):
    t1 = Task('t1', noop)
    t2 = Task('t2', noop)
    t1.next(t2)
    cw.add_tasks(t1, t2)

    h2 = Task('head2', noop)
    cw.add_head(h2)

    assert t1.argo_task.dependencies == ['head2']
    assert t2.argo_task.dependencies == ['t1', 'head2']

    h1 = Task('head1', noop)
    cw.add_head(h1)

    assert h2.argo_task.dependencies == ['head1']
    assert t1.argo_task.dependencies == ['head2', 'head1']
    assert t2.argo_task.dependencies == ['t1', 'head2', 'head1']


def test_cwf_valid_field_set(cws):
    cw = CronWorkflow('cw', "* * * * *", service=cws, parallelism=33)
    assert cw.schedule == "* * * * *"
    assert cw.service == cws
    assert cw.parallelism == 33

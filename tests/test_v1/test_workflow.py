from hera.v1.empty_dir_volume import EmptyDirVolume
from hera.v1.existing_volume import ExistingVolume
from hera.v1.resources import Resources
from hera.v1.task import Task
from hera.v1.volume import Volume
from hera.v1.workflow import Workflow
from hera.v1.workflow_service import WorkflowService


def noop():
    pass


def test_wf_does_not_add_empty_task():
    t = None
    ws = WorkflowService('abc.com', 'abc')
    w = Workflow('w', service=ws)
    w.add_task(t)

    assert not w.dag_template.tasks


def test_wf_adds_specified_tasks():
    n = 3
    ws = WorkflowService('abc.com', 'abc')
    w = Workflow('w', service=ws)
    ts = [Task(f't{i}', noop) for i in range(n)]
    w.add_tasks(*ts)

    assert len(w.dag_template.tasks) == n
    for i, t in enumerate(w.dag_template.tasks):
        assert ts[i].name == t.name


def test_wf_adds_task_volume():
    ws = WorkflowService('abc.com', 'abc')
    w = Workflow('w', service=ws)
    t = Task(
        't',
        noop,
        resources=Resources(volume=Volume(name='v', size='1Gi', mount_path='/', storage_class_name='custom')),
    )
    w.add_task(t)

    claim = w.spec.volume_claim_templates[0]
    assert claim.spec.access_modes == ['ReadWriteOnce']
    assert claim.spec.resources.requests['storage'] == '1Gi'
    assert claim.spec.storage_class_name == 'custom'
    assert claim.metadata.name == 'v'


def test_wf_adds_task_existing_checkpoints_staging_volume():
    ws = WorkflowService('abc.com', 'abc')
    w = Workflow('w', service=ws)
    t = Task('t', noop, resources=Resources(existing_volume=ExistingVolume(name='v', mount_path='/')))
    w.add_task(t)

    vol = w.spec.volumes[0]
    assert vol.name == 'v'
    assert vol.persistent_volume_claim.claim_name == 'v'


def test_wf_adds_task_existing_checkpoints_prod_volume():
    ws = WorkflowService('abc.com', 'abc')
    w = Workflow('w', service=ws)
    t = Task(
        't',
        noop,
        resources=Resources(existing_volume=ExistingVolume(name='vol', mount_path='/')),
    )
    w.add_task(t)

    vol = w.spec.volumes[0]
    assert vol.name == 'vol'
    assert vol.persistent_volume_claim.claim_name == 'vol'


def test_wf_adds_task_empty_dir_volume():
    ws = WorkflowService('abc.com', 'abc')
    w = Workflow('w', service=ws)
    t = Task('t', noop, resources=Resources(empty_dir_volume=EmptyDirVolume(name='v')))
    w.add_task(t)

    vol = w.spec.volumes[0]
    assert vol.name == 'v'
    assert not vol.empty_dir.size_limit
    assert vol.empty_dir.medium == 'Memory'


def test_wf_adds_head():
    ws = WorkflowService('abc.com', 'abc')
    w = Workflow('w', service=ws)
    t1 = Task('t1', noop)
    t2 = Task('t2', noop)
    t1.next(t2)
    w.add_tasks(t1, t2)

    h = Task('head', noop)
    w.add_head(h)

    assert t1.argo_task.dependencies == ['head']
    assert t2.argo_task.dependencies == ['t1', 'head']


def test_wf_adds_tail():
    ws = WorkflowService('abc.com', 'abc')
    w = Workflow('w', service=ws)
    t1 = Task('t1', noop)
    t2 = Task('t2', noop)
    t1.next(t2)
    w.add_tasks(t1, t2)

    t = Task('tail', noop)
    w.add_tail(t)

    assert not t1.argo_task.dependencies
    assert t2.argo_task.dependencies == ['t1']
    assert t.argo_task.dependencies == ['t2']


def test_wf_overwrites_head_and_tail():
    ws = WorkflowService('abc.com', 'abc')
    w = Workflow('w', service=ws)
    t1 = Task('t1', noop)
    t2 = Task('t2', noop)
    t1.next(t2)
    w.add_tasks(t1, t2)

    h2 = Task('head2', noop)
    w.add_head(h2)

    assert t1.argo_task.dependencies == ['head2']
    assert t2.argo_task.dependencies == ['t1', 'head2']

    h1 = Task('head1', noop)
    w.add_head(h1)

    assert h2.argo_task.dependencies == ['head1']
    assert t1.argo_task.dependencies == ['head2', 'head1']
    assert t2.argo_task.dependencies == ['t1', 'head2', 'head1']

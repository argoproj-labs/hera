"""This example showcases how clients can schedule tasks that provision independent volumes"""
from hera.resources import Resources
from hera.task import Task
from hera.volumes import Volume
from hera.workflow import Workflow
from hera.workflow_service import WorkflowService


def do():
    """
    The task will print the following output:

    This is a task that requires a lot of storage! Available storage:
    Filesystem      Size  Used Avail Use% Mounted on
    ...              95G  7.8G   87G   9% /
    ...              64M     0   64M   0% /dev
    ...             7.9G     0  7.9G   0% /sys/fs/cgroup
    /dev/sdb         49G   24K   49G   1% /vol
    ...
    """
    import os

    print(f'This is a task that requires a lot of storage! Available storage:\n{os.popen("df -h").read()}')


# TODO: replace the domain and token with your own
ws = WorkflowService(host='my-argo-server.com', token='my-auth-token')
w = Workflow('volume', ws)
d = Task('do', do, resources=Resources(volumes=[Volume(size='50Gi', mount_path='/vol')]))

w.add_task(d)
w.create()

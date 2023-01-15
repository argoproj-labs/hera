"""This example showcases how clients can schedule tasks that provision independent volumes"""

from hera import Task, Volume, Workflow


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


# assumes you used `hera.set_global_token` and `hera.set_global_host` so that the workflow can be submitted
with Workflow(
    "volume",
) as w:
    Task("do", do, volumes=[Volume(size="50Gi", mount_path="/vol")])

w.create()

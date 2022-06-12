"""
This task showcases how clients can request a particular number of GPUs to be available for a task and the specific
type of GPU to request. The task uses the Horovod image as it provides Python and NVIDIA SMI.
"""
from hera import GPUToleration, Resources, Task, Workflow, WorkflowService


def do():
    """
    The task will print the following output:

    This is a task that uses GPUs! CUDA info:
    Tue Sep 28 13:31:22 2021
    +-----------------------------------------------------------------------------+
    | NVIDIA-SMI 450.119.04   Driver Version: 450.119.04   CUDA Version: 11.0     |
    |-------------------------------+----------------------+----------------------+
    | GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
    | Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
    |                               |                      |               MIG M. |
    |===============================+======================+======================|
    |   0  Tesla K80           Off  | 00000000:00:05.0 Off |                    0 |
    | N/A   67C    P8    33W / 149W |      0MiB / 11441MiB |      0%      Default |
    |                               |                      |                  N/A |
    +-------------------------------+----------------------+----------------------+

    +-----------------------------------------------------------------------------+
    | Processes:                                                                  |
    |  GPU   GI   CI        PID   Type   Process name                  GPU Memory |
    |        ID   ID                                                   Usage      |
    |=============================================================================|
    |  No running processes found                                                 |
    +-----------------------------------------------------------------------------+
    """
    import os

    print(f'This is a task that uses GPUs! CUDA info:\n{os.popen("nvidia-smi").read()}')


# TODO: replace the domain and token with your own
ws = WorkflowService(host='https://my-argo-server.com', token='my-auth-token')
w = Workflow('gpu', ws)
gke_k80_gpu = {'cloud.google.com/gke-accelerator': 'nvidia-tesla-k80'}
d = Task(
    'do',
    do,
    image='horovod/horovod:0.22.1',
    resources=Resources(gpus=1),
    tolerations=[GPUToleration],
    node_selectors=gke_k80_gpu,
)

w.add_task(d)
w.create()

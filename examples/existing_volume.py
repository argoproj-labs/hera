"""
This example showcases how Hera supports mounting existing volumes. These volumes are expected to already be
provisioned and available as a persistent volume claim in the K8S cluster where Argo runs.
"""

from hera import ExistingVolume, Resources, Task, Workflow, WorkflowService


def download(path: str):
    # we can run this task asynchronously for downloading some big file to an existing volume!
    print(f"Would have downloaded from {path} to /vol")


with Workflow(
    "existing-volume", service=WorkflowService(host="https://my-argo-server.com", token="my-auth-token")
) as w:
    Task(
        "download",
        download,
        [{"path": "/whatever/path"}],
        resources=Resources(volumes=[ExistingVolume(name="my-vol-claim", mount_path="/vol")]),
    )

w.create()

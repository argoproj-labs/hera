"""
This example showcases how Hera supports mounting existing volumes. These volumes are expected to already be
provisioned and available as a persistent volume claim in the K8S cluster where Argo runs.
"""

from hera import ExistingVolume, Task, Workflow


def download(path: str):
    # we can run this task asynchronously for downloading some big file to an existing volume!
    print(f"Would have downloaded from {path} to /vol")


# assumes you used `hera.set_global_token` and `hera.set_global_host` so that the workflow can be submitted
with Workflow("existing-volume") as w:
    Task(
        "download",
        download,
        [{"path": "/whatever/path"}],
        volumes=[ExistingVolume(name="my-vol-claim", mount_path="/vol")],
    )

w.create()

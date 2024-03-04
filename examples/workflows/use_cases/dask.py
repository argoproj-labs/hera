"""This example showcases how to run Dask within a Hera submitted Argo workflow."""

from hera.workflows import (
    Steps,
    Workflow,
    script,
)


@script(image="ghcr.io/dask/dask:latest")
def dask_computation(namespace: str = "default", n_workers: int = 1) -> None:
    import subprocess

    # this is required for otherwise the dask distributed and kubernetes clients packages are not included by default
    # ideally, you'd have a package in your organization that takes care of the following cluster details :)
    subprocess.run(
        ["pip", "install", "dask-kubernetes", "dask[distributed]"], stdout=subprocess.PIPE, universal_newlines=True
    )

    import dask.array as da
    from dask.distributed import Client
    from dask_kubernetes.classic import KubeCluster, make_pod_spec

    cluster = KubeCluster(
        pod_template=make_pod_spec(
            image="ghcr.io/dask/dask:latest",
            memory_limit="4G",
            memory_request="2G",
            cpu_limit=1,
            cpu_request=1,
        ),
        namespace=namespace,
        n_workers=n_workers,
    )

    # once the `Client` is initialized all dask calls are actually implicitly performed against it
    client = Client(cluster)
    array = da.ones((1000, 1000, 1000))
    print("Array mean = {array_mean}, expected = 1.0".format(array_mean=array.mean().compute()))
    client.close()


with Workflow(generate_name="dask-", entrypoint="s") as w:
    with Steps(name="s"):
        dask_computation()

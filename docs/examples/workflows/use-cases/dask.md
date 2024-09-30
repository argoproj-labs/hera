# Dask



This example showcases how to run Dask within a Hera submitted Argo workflow.


=== "Hera"

    ```python linenums="1"
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
        from dask_kubernetes.operator import KubeCluster

        cluster = KubeCluster(
            image="ghcr.io/dask/dask:latest",
            resources={"requests": {"memory": "2G", "cpu": "1"}, "limits": {"memory": "4G", "cpu": "1"}},
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
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: dask-
    spec:
      entrypoint: s
      templates:
      - name: s
        steps:
        - - name: dask-computation
            template: dask-computation
      - inputs:
          parameters:
          - default: default
            name: namespace
          - default: '1'
            name: n_workers
        name: dask-computation
        script:
          command:
          - python
          image: ghcr.io/dask/dask:latest
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: n_workers = json.loads(r'''{{inputs.parameters.n_workers}}''')
            except: n_workers = r'''{{inputs.parameters.n_workers}}'''
            try: namespace = json.loads(r'''{{inputs.parameters.namespace}}''')
            except: namespace = r'''{{inputs.parameters.namespace}}'''

            import subprocess
            subprocess.run(['pip', 'install', 'dask-kubernetes', 'dask[distributed]'], stdout=subprocess.PIPE, universal_newlines=True)
            import dask.array as da
            from dask.distributed import Client
            from dask_kubernetes.operator import KubeCluster
            cluster = KubeCluster(image='ghcr.io/dask/dask:latest', resources={'requests': {'memory': '2G', 'cpu': '1'}, 'limits': {'memory': '4G', 'cpu': '1'}}, namespace=namespace, n_workers=n_workers)
            client = Client(cluster)
            array = da.ones((1000, 1000, 1000))
            print('Array mean = {array_mean}, expected = 1.0'.format(array_mean=array.mean().compute()))
            client.close()
    ```


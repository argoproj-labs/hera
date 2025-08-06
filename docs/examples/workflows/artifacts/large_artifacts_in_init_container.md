# Large Artifacts In Init Container



This example shows how to use `pod_spec_patch` to update the cpu/memory requests for the init container.

This is useful if you want to load a large artifact, but the init container does not have enough memory to load it. This
problem is described in the
[Argo Artifacts Walkthrough](https://argo-workflows.readthedocs.io/en/stable/walk-through/artifacts/).

In Hera, the `resources` field of the template only sets the `main` container resources. We can use a `pod_spec_patch`
to set the init container resources.


=== "Hera"

    ```python linenums="1"
    import json

    from hera.workflows import (
        Artifact,
        NoneArchiveStrategy,
        Resources,
        Steps,
        Workflow,
        script,
    )


    @script(
        outputs=Artifact(name="out-art", path="/tmp/file", archive=NoneArchiveStrategy()),
        resources=Resources(memory_request="2Gi"),
    )
    def writer():
        with open("/tmp/file", "w") as f:
            f.write("Hello, world!")


    @script(
        inputs=Artifact(name="in-art", path="/tmp/file"),
        resources=Resources(memory_request="2Gi"),
        pod_spec_patch=json.dumps({"initContainers": [{"name": "init", "resources": {"requests": {"memory": "2Gi"}}}]}),
    )
    def consumer():
        with open("/tmp/file", "r") as f:
            print(f.readlines())  # prints `Hello, world!` to `stdout`


    with Workflow(generate_name="artifact-", entrypoint="steps") as w:
        with Steps(name="steps"):
            w_ = writer()
            c = consumer(arguments={"in-art": w_.get_artifact("out-art")})
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: artifact-
    spec:
      entrypoint: steps
      templates:
      - name: steps
        steps:
        - - name: writer
            template: writer
        - - name: consumer
            template: consumer
            arguments:
              artifacts:
              - name: in-art
                from: '{{steps.writer.outputs.artifacts.out-art}}'
      - name: writer
        outputs:
          artifacts:
          - name: out-art
            path: /tmp/file
            archive:
              none: {}
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            with open('/tmp/file', 'w') as f:
                f.write('Hello, world!')
          command:
          - python
          resources:
            requests:
              memory: 2Gi
      - name: consumer
        podSpecPatch: '{"initContainers": [{"name": "init", "resources": {"requests":
          {"memory": "2Gi"}}}]}'
        inputs:
          artifacts:
          - name: in-art
            path: /tmp/file
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            with open('/tmp/file', 'r') as f:
                print(f.readlines())
          command:
          - python
          resources:
            requests:
              memory: 2Gi
    ```


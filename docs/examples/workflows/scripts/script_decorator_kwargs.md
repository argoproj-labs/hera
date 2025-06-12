# Script Decorator Kwargs



This example shows various kwarg parameters for the script decorator.


=== "Hera"

    ```python linenums="1"
    from hera.workflows import Resources, Workflow, script
    from hera.workflows.models import ImagePullPolicy


    @script(
        image_pull_policy=ImagePullPolicy.always,
        resources=Resources(memory_request="5Gi"),
        annotations={"my-annotation": "my-value"},
        labels={"my-label": "my-value"},
    )
    def script_with_kwargs():
        print("ok")


    with Workflow(generate_name="script-with-kwargs-", entrypoint="script-with-kwargs") as w:
        script_with_kwargs()
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: script-with-kwargs-
    spec:
      entrypoint: script-with-kwargs
      templates:
      - name: script-with-kwargs
        metadata:
          annotations:
            my-annotation: my-value
          labels:
            my-label: my-value
        script:
          image: python:3.9
          imagePullPolicy: Always
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            print('ok')
          command:
          - python
          resources:
            requests:
              memory: 5Gi
    ```


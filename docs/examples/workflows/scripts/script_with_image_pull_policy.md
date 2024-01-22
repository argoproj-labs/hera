# Script With Image Pull Policy






=== "Hera"

    ```python linenums="1"
    from hera.workflows import Workflow, script
    from hera.workflows.models import ImagePullPolicy


    @script(image_pull_policy=ImagePullPolicy.always)
    def task_with_image_pull_policy():
        print("ok")


    with Workflow(generate_name="script-with-image-pull-policy-", entrypoint="task-with-image-pull-policy") as w:
        task_with_image_pull_policy()
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: script-with-image-pull-policy-
    spec:
      entrypoint: task-with-image-pull-policy
      templates:
      - name: task-with-image-pull-policy
        script:
          command:
          - python
          image: python:3.8
          imagePullPolicy: Always
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            print('ok')
    ```


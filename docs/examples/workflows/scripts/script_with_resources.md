# Script With Resources






=== "Hera"

    ```python linenums="1"
    from hera.workflows import Resources, Workflow, script


    @script(resources=Resources(memory_request="5Gi"))
    def task_with_memory_request():
        print("ok")


    with Workflow(generate_name="script-with-resources-", entrypoint="task-with-memory-request") as w:
        task_with_memory_request()
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: script-with-resources-
    spec:
      entrypoint: task-with-memory-request
      templates:
      - name: task-with-memory-request
        script:
          command:
          - python
          image: python:3.9
          resources:
            requests:
              memory: 5Gi
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            print('ok')
    ```


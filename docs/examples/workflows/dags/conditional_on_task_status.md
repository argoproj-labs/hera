# Conditional On Task Status



This example showcases conditional execution on success, failure, and error


=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Workflow, script


    @script()
    def random():
        import random

        p = random.random()
        if p <= 0.5:
            raise Exception("failure")


    @script()
    def success():
        print("succeeded!")


    @script()
    def failure():
        print("failed!")


    with Workflow(generate_name="dag-conditional-on-task-status-", entrypoint="d") as w:
        with DAG(name="d"):
            r = random()

            r.on_success(success())
            r.on_failure(failure())
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: dag-conditional-on-task-status-
    spec:
      entrypoint: d
      templates:
      - name: d
        dag:
          tasks:
          - name: random
            template: random
          - name: success
            depends: random.Succeeded
            template: success
          - name: failure
            depends: random.Failed
            template: failure
      - name: random
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import random
            p = random.random()
            if p <= 0.5:
                raise Exception('failure')
          command:
          - python
      - name: success
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            print('succeeded!')
          command:
          - python
      - name: failure
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            print('failed!')
          command:
          - python
    ```


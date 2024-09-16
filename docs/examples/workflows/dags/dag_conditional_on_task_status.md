# Dag Conditional On Task Status






=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Workflow, script


    @script()
    def fail_or_succeed():
        import random

        if random.randint(0, 1) == 0:
            raise ValueError


    @script()
    def when_succeeded():
        print("It was a success")


    @script()
    def when_failed():
        print("It was a failure")


    with Workflow(generate_name="dag-conditional-on-task-status-", entrypoint="d") as w:
        with DAG(name="d") as s:
            t1 = fail_or_succeed()

            t1.on_failure(when_failed())
            t1.on_success(when_succeeded())
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
      - dag:
          tasks:
          - name: fail-or-succeed
            template: fail-or-succeed
          - depends: fail-or-succeed.Failed
            name: when-failed
            template: when-failed
          - depends: fail-or-succeed.Succeeded
            name: when-succeeded
            template: when-succeeded
        name: d
      - name: fail-or-succeed
        script:
          command:
          - python
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import random
            if random.randint(0, 1) == 0:
                raise ValueError
      - name: when-failed
        script:
          command:
          - python
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            print('It was a failure')
      - name: when-succeeded
        script:
          command:
          - python
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            print('It was a success')
    ```


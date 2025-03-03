# Conditional



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
        print("success")


    @script()
    def success():
        print("success")


    @script()
    def failure():
        print("failure")


    with Workflow(generate_name="conditional-", entrypoint="d") as w:
        with DAG(name="d"):
            r = random()
            s = success()
            f = failure()

            r.on_success(s)
            r.on_failure(f)
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: conditional-
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
            print('success')
          command:
          - python
      - name: success
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            print('success')
          command:
          - python
      - name: failure
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            print('failure')
          command:
          - python
    ```


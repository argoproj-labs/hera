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
      - dag:
          tasks:
          - name: random
            template: random
          - depends: random.Succeeded
            name: success
            template: success
          - depends: random.Failed
            name: failure
            template: failure
        name: d
      - name: random
        script:
          command:
          - python
          image: python:3.8
          source: "import os\nimport sys\nsys.path.append(os.getcwd())\nimport random\n\
            p = random.random()\nif (p <= 0.5):\n    raise Exception('failure')\nprint('success')"
      - name: success
        script:
          command:
          - python
          image: python:3.8
          source: 'import os

            import sys

            sys.path.append(os.getcwd())

            print(''success'')'
      - name: failure
        script:
          command:
          - python
          image: python:3.8
          source: 'import os

            import sys

            sys.path.append(os.getcwd())

            print(''failure'')'
    ```


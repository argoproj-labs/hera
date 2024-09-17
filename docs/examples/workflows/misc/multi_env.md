# Multi Env






=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Workflow, script


    @script(env={"a": 1, "b": 2, "c": 3})
    def env():
        import os

        # note that env params come in as strings
        assert os.environ["a"] == "1", os.environ["a"]
        assert os.environ["b"] == "2", os.environ["b"]
        assert os.environ["c"] == "3", os.environ["c"]


    with Workflow(generate_name="multi-env-", entrypoint="d") as w:
        with DAG(name="d"):
            env()
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: multi-env-
    spec:
      entrypoint: d
      templates:
      - dag:
          tasks:
          - name: env
            template: env
        name: d
      - name: env
        script:
          command:
          - python
          env:
          - name: a
            value: '1'
          - name: b
            value: '2'
          - name: c
            value: '3'
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import os
            assert os.environ['a'] == '1', os.environ['a']
            assert os.environ['b'] == '2', os.environ['b']
            assert os.environ['c'] == '3', os.environ['c']
    ```


# Complex Deps






=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Workflow, script


    @script()
    def foo(p):
        if p < 0.5:
            raise Exception(p)
        print(42)


    with Workflow(generate_name="complex-deps-", entrypoint="d") as w:
        with DAG(name="d"):
            A = foo(name="a", arguments={"p": 0.6})
            B = foo(name="b", arguments={"p": 0.3})
            C = foo(name="c", arguments={"p": 0.7})
            D = foo(name="d", arguments={"p": 0.9})
            # here, D depends on A, B, and C. If A succeeds and one of B or C fails, D still runs
            A >> [B, C], [A, (B | C)] >> D
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: complex-deps-
    spec:
      entrypoint: d
      templates:
      - dag:
          tasks:
          - arguments:
              parameters:
              - name: p
                value: '0.6'
            name: a
            template: foo
          - arguments:
              parameters:
              - name: p
                value: '0.3'
            depends: a
            name: b
            template: foo
          - arguments:
              parameters:
              - name: p
                value: '0.7'
            depends: a
            name: c
            template: foo
          - arguments:
              parameters:
              - name: p
                value: '0.9'
            depends: a && (b || c)
            name: d
            template: foo
        name: d
      - inputs:
          parameters:
          - name: p
        name: foo
        script:
          command:
          - python
          image: python:3.8
          source: "import os\nimport sys\nsys.path.append(os.getcwd())\nimport json\n\
            try: p = json.loads(r'''{{inputs.parameters.p}}''')\nexcept: p = r'''{{inputs.parameters.p}}'''\n\
            \nif (p < 0.5):\n    raise Exception(p)\nprint(42)"
    ```


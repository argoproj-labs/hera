# Any Success All Fail






=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Workflow, script


    @script()
    def foo(a):
        print(a)


    @script()
    def random_fail(a):
        import random

        random.seed(a)
        if random.random() < 0.5:
            raise Exception("Oh, no!")


    @script()
    def fail(a):
        raise Exception(a)


    with Workflow(generate_name="any-success-all-fail-", entrypoint="d") as w:
        with DAG(name="d"):
            t1 = random_fail(name="t1", with_param=[1, 2, 3])
            t2 = fail(name="t2", with_param=[1, 2, 3])
            t3 = foo(name="t3", with_param=[1, 2, 3])

            t1.when_any_succeeded(t2)
            t2.when_all_failed(t3)
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: any-success-all-fail-
    spec:
      entrypoint: d
      templates:
      - dag:
          tasks:
          - arguments:
              parameters:
              - name: a
                value: '{{item}}'
            name: t1
            template: random-fail
            withParam: '[1, 2, 3]'
          - arguments:
              parameters:
              - name: a
                value: '{{item}}'
            depends: t1.AnySucceeded
            name: t2
            template: fail
            withParam: '[1, 2, 3]'
          - arguments:
              parameters:
              - name: a
                value: '{{item}}'
            depends: t2.AllFailed
            name: t3
            template: foo
            withParam: '[1, 2, 3]'
        name: d
      - inputs:
          parameters:
          - name: a
        name: random-fail
        script:
          command:
          - python
          image: python:3.8
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: a = json.loads(r'''{{inputs.parameters.a}}''')
            except: a = r'''{{inputs.parameters.a}}'''

            import random
            random.seed(a)
            if random.random() < 0.5:
                raise Exception('Oh, no!')
      - inputs:
          parameters:
          - name: a
        name: fail
        script:
          command:
          - python
          image: python:3.8
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: a = json.loads(r'''{{inputs.parameters.a}}''')
            except: a = r'''{{inputs.parameters.a}}'''

            raise Exception(a)
      - inputs:
          parameters:
          - name: a
        name: foo
        script:
          command:
          - python
          image: python:3.8
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: a = json.loads(r'''{{inputs.parameters.a}}''')
            except: a = r'''{{inputs.parameters.a}}'''

            print(a)
    ```


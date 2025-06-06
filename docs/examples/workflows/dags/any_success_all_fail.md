# Any Success All Fail



This example shows how to run a task if "any succeed" or if "all fail" from a fan-out.


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
      - name: d
        dag:
          tasks:
          - name: t1
            template: random-fail
            withParam: '[1, 2, 3]'
            arguments:
              parameters:
              - name: a
                value: '{{item}}'
          - name: t2
            depends: t1.AnySucceeded
            template: fail
            withParam: '[1, 2, 3]'
            arguments:
              parameters:
              - name: a
                value: '{{item}}'
          - name: t3
            depends: t2.AllFailed
            template: foo
            withParam: '[1, 2, 3]'
            arguments:
              parameters:
              - name: a
                value: '{{item}}'
      - name: random-fail
        inputs:
          parameters:
          - name: a
        script:
          image: python:3.9
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
          command:
          - python
      - name: fail
        inputs:
          parameters:
          - name: a
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: a = json.loads(r'''{{inputs.parameters.a}}''')
            except: a = r'''{{inputs.parameters.a}}'''

            raise Exception(a)
          command:
          - python
      - name: foo
        inputs:
          parameters:
          - name: a
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: a = json.loads(r'''{{inputs.parameters.a}}''')
            except: a = r'''{{inputs.parameters.a}}'''

            print(a)
          command:
          - python
    ```


# With Sequence



This example showcases how to generate and parallelize generated sequences


=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Workflow, script
    from hera.workflows.models import Sequence


    @script()
    def gen_num():
        print(3)


    @script()
    def say(message: str):
        print(message)


    with Workflow(generate_name="with-sequence-example", entrypoint="d") as w:
        with DAG(name="d"):
            t1 = gen_num(name="t1")
            t2 = say(name="t2", with_sequence=Sequence(count=t1.result, start="0"), arguments={"message": "{{item}}"})
            t3 = say(
                name="t3",
                with_sequence=Sequence(start=t1.result, end="5", format="2020-05-%02X"),
                arguments={"message": "{{item}}"},
            )
            t1 >> [t2, t3]
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: with-sequence-example
    spec:
      entrypoint: d
      templates:
      - dag:
          tasks:
          - name: t1
            template: gen-num
          - arguments:
              parameters:
              - name: message
                value: '{{item}}'
            depends: t1
            name: t2
            template: say
            withSequence:
              count: '{{tasks.t1.outputs.result}}'
              start: '0'
          - arguments:
              parameters:
              - name: message
                value: '{{item}}'
            depends: t1
            name: t3
            template: say
            withSequence:
              end: '5'
              format: 2020-05-%02X
              start: '{{tasks.t1.outputs.result}}'
        name: d
      - name: gen-num
        script:
          command:
          - python
          image: python:3.8
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            print(3)
      - inputs:
          parameters:
          - name: message
        name: say
        script:
          command:
          - python
          image: python:3.8
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: message = json.loads(r'''{{inputs.parameters.message}}''')
            except: message = r'''{{inputs.parameters.message}}'''

            print(message)
    ```


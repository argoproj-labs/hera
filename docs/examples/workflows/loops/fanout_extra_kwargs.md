# Fanout Extra Kwargs



This example shows how to use a fan-out over one argument, while keeping the others the same.


=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Workflow, script


    @script()
    def generate():
        import json
        import sys

        # this can be anything! e.g fetch from some API, then in parallel process
        # all entities; chunk database records and process them in parallel, etc.
        json.dump([i for i in range(10)], sys.stdout)


    @script()
    def consume(value: int, extra_param1: str, extra_param2: int = 42):
        print(
            "Received value={value}, extra_param1={extra_param1}, extra_param2={extra_param2}!".format(
                value=value,
                extra_param1=extra_param1,
                extra_param2=extra_param2,
            )
        )


    with Workflow(generate_name="dynamic-fanout-", entrypoint="d") as w:
        with DAG(name="d"):
            g = generate()

            # We use `value` to fan-out over the values from `generate`, while the
            # other arguments remain the same for all fan-out tasks.
            # `extra_param1` is set here, while `extra_param1` has a default
            # value of 42 in the script
            c1 = consume(
                name="c1",
                with_param=g.result,
                arguments={
                    "value": "{{item}}",
                    "extra_param1": "hello world",
                },
            )

            # Here is the same fan-out, except we are also setting `extra_param2`
            c2 = consume(
                name="c2",
                with_param=g.result,
                arguments={
                    "value": "{{item}}",
                    "extra_param1": "hello world",
                    "extra_param2": "123",
                },
            )
            g >> [c1, c2]
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: dynamic-fanout-
    spec:
      entrypoint: d
      templates:
      - name: d
        dag:
          tasks:
          - name: generate
            template: generate
          - name: c1
            depends: generate
            template: consume
            withParam: '{{tasks.generate.outputs.result}}'
            arguments:
              parameters:
              - name: value
                value: '{{item}}'
              - name: extra_param1
                value: hello world
          - name: c2
            depends: generate
            template: consume
            withParam: '{{tasks.generate.outputs.result}}'
            arguments:
              parameters:
              - name: value
                value: '{{item}}'
              - name: extra_param1
                value: hello world
              - name: extra_param2
                value: '123'
      - name: generate
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            import sys
            json.dump([i for i in range(10)], sys.stdout)
          command:
          - python
      - name: consume
        inputs:
          parameters:
          - name: value
          - name: extra_param1
          - name: extra_param2
            default: '42'
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: extra_param1 = json.loads(r'''{{inputs.parameters.extra_param1}}''')
            except: extra_param1 = r'''{{inputs.parameters.extra_param1}}'''
            try: extra_param2 = json.loads(r'''{{inputs.parameters.extra_param2}}''')
            except: extra_param2 = r'''{{inputs.parameters.extra_param2}}'''
            try: value = json.loads(r'''{{inputs.parameters.value}}''')
            except: value = r'''{{inputs.parameters.value}}'''

            print('Received value={value}, extra_param1={extra_param1}, extra_param2={extra_param2}!'.format(value=value, extra_param1=extra_param1, extra_param2=extra_param2))
          command:
          - python
    ```


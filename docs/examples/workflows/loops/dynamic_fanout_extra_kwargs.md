# Dynamic Fanout Extra Kwargs



This example showcases how clients can use Hera to dynamically generate tasks that process outputs from one task in
parallel. This is useful for batch jobs and instances where clients do not know ahead of time how many tasks/entities
they may need to process. In addition to the fanout, this example showcases how one can set up extra parameters for
the job to dictate what the fanout should execute over.


=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Workflow, script


    @script()
    def generate():
        import json
        import sys

        # this can be anything! e.g fetch from some API, then in parallel process all entities; chunk database records
        # and process them in parallel, etc.
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


    # assumes you used `hera.set_global_token` and `hera.set_global_host` so that the workflow can be submitted
    with Workflow(generate_name="dynamic-fanout-", entrypoint="d") as w:
        with DAG(name="d"):
            g = generate()
            # the following fanout will occur over the items in the list that is returned from the generate script
            # the `extra_param1` will take the `hello world` value while `extra_param2` will hold the default value of 42
            c1 = consume(name="c1", with_param=g.result, arguments={"value": "{{item}}", "extra_param1": "hello world"})

            # the following fanout will occur over the items in the list that is returned from the generate script
            # the `extra_param1` will take the `hello world` value while `extra_param2` will hold the default value of 123
            c2 = consume(
                name="c2",
                with_param=g.result,
                arguments={"value": "{{item}}", "extra_param1": "hello world", "extra_param2": "123"},
            )
            g >> c1
            g >> c2
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
      - dag:
          tasks:
          - name: generate
            template: generate
          - arguments:
              parameters:
              - name: value
                value: '{{item}}'
              - name: extra_param1
                value: hello world
            depends: generate
            name: c1
            template: consume
            withParam: '{{tasks.generate.outputs.result}}'
          - arguments:
              parameters:
              - name: value
                value: '{{item}}'
              - name: extra_param1
                value: hello world
              - name: extra_param2
                value: '123'
            depends: generate
            name: c2
            template: consume
            withParam: '{{tasks.generate.outputs.result}}'
        name: d
      - name: generate
        script:
          command:
          - python
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            import sys
            json.dump([i for i in range(10)], sys.stdout)
      - inputs:
          parameters:
          - name: value
          - name: extra_param1
          - default: '42'
            name: extra_param2
        name: consume
        script:
          command:
          - python
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
    ```


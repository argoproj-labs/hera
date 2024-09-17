# Dynamic Fanout



This example showcases how clients can use Hera to dynamically generate tasks that process outputs from one task in
parallel. This is useful for batch jobs and instances where clients do not know ahead of time how many tasks/entities
they may need to process.


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
    def consume(value: int):
        print("Received value: {value}!".format(value=value))


    # assumes you used `hera.set_global_token` and `hera.set_global_host` so that the workflow can be submitted
    with Workflow(generate_name="dynamic-fanout-", entrypoint="d") as w:
        with DAG(name="d"):
            g = generate()
            c = consume(with_param=g.result)
            g >> c
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
            depends: generate
            name: consume
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
            try: value = json.loads(r'''{{inputs.parameters.value}}''')
            except: value = r'''{{inputs.parameters.value}}'''

            print('Received value: {value}!'.format(value=value))
    ```


# Dynamic Fanout Json Payload



This example showcases how clients can use Hera to dynamically generate tasks that process outputs from one task in
parallel. This is useful for batch jobs and instances where clients do not know ahead of time how many tasks/entities
they may need to process. The fanout occurs over independent JSON payloads coming from the generate script


=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Workflow, script


    @script()
    def generate():
        import json
        import sys

        # this can be anything! e.g fetch from some API, then in parallel process all entities; chunk database records
        # and process them in parallel, etc.
        json.dump([{"p1": i + 1, "p2": i + 2, "p3": i + 3} for i in range(10)], sys.stdout)


    @script()
    def consume(p1: str, p2: str, p3: str):
        print("Received p1={p1}, p2={p2}, p3={p3}".format(p1=p1, p2=p2, p3=p3))


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
              - name: p1
                value: '{{item.p1}}'
              - name: p2
                value: '{{item.p2}}'
              - name: p3
                value: '{{item.p3}}'
            depends: generate
            name: consume
            template: consume
            withParam: '{{tasks.generate.outputs.result}}'
        name: d
      - name: generate
        script:
          command:
          - python
          image: python:3.8
          source: 'import os

            import sys

            sys.path.append(os.getcwd())

            import json

            import sys

            json.dump([{''p1'': i + 1, ''p2'': i + 2, ''p3'': i + 3} for i in range(10)],
            sys.stdout)'
      - inputs:
          parameters:
          - name: p1
          - name: p2
          - name: p3
        name: consume
        script:
          command:
          - python
          image: python:3.8
          source: 'import os

            import sys

            sys.path.append(os.getcwd())

            import json

            try: p1 = json.loads(r''''''{{inputs.parameters.p1}}'''''')

            except: p1 = r''''''{{inputs.parameters.p1}}''''''

            try: p2 = json.loads(r''''''{{inputs.parameters.p2}}'''''')

            except: p2 = r''''''{{inputs.parameters.p2}}''''''

            try: p3 = json.loads(r''''''{{inputs.parameters.p3}}'''''')

            except: p3 = r''''''{{inputs.parameters.p3}}''''''


            print(''Received p1={p1}, p2={p2}, p3={p3}''.format(p1=p1, p2=p2, p3=p3))'
    ```


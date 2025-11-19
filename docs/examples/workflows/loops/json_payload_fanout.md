# Json Payload Fanout



This example shows how you can fan-out over a JSON payload (a JSON list of dicts), and let Hera match the arguments for you.


=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Workflow, script


    @script()
    def generate():
        import json
        import sys

        # this can be anything! e.g fetch from some API, then in parallel process
        # all entities; chunk database records and process them in parallel, etc.
        json.dump([{"p1": i + 1, "p2": i + 2, "p3": i + 3} for i in range(10)], sys.stdout)


    @script()
    def consume(p1: str, p2: str, p3: str):
        print("Received p1={p1}, p2={p2}, p3={p3}".format(p1=p1, p2=p2, p3=p3))


    with Workflow(generate_name="json-payload-fanout-", entrypoint="d") as w:
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
      generateName: json-payload-fanout-
    spec:
      entrypoint: d
      templates:
      - name: d
        dag:
          tasks:
          - name: generate
            template: generate
          - name: consume
            depends: generate
            template: consume
            withParam: '{{tasks.generate.outputs.result}}'
            arguments:
              parameters:
              - name: p1
                value: '{{item.p1}}'
              - name: p2
                value: '{{item.p2}}'
              - name: p3
                value: '{{item.p3}}'
      - name: generate
        script:
          image: python:3.10
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            import sys
            json.dump([{'p1': i + 1, 'p2': i + 2, 'p3': i + 3} for i in range(10)], sys.stdout)
          command:
          - python
      - name: consume
        inputs:
          parameters:
          - name: p1
          - name: p2
          - name: p3
        script:
          image: python:3.10
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: p1 = json.loads(r'''{{inputs.parameters.p1}}''')
            except: p1 = r'''{{inputs.parameters.p1}}'''
            try: p2 = json.loads(r'''{{inputs.parameters.p2}}''')
            except: p2 = r'''{{inputs.parameters.p2}}'''
            try: p3 = json.loads(r'''{{inputs.parameters.p3}}''')
            except: p3 = r'''{{inputs.parameters.p3}}'''

            print('Received p1={p1}, p2={p2}, p3={p3}'.format(p1=p1, p2=p2, p3=p3))
          command:
          - python
    ```


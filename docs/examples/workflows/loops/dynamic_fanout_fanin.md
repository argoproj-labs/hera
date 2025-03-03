# Dynamic Fanout Fanin






=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Parameter, Workflow, script
    from hera.workflows.models import ValueFrom


    @script()
    def generate():
        import json
        import sys

        json.dump([{"value": i} for i in range(10)], sys.stdout)


    @script(outputs=[Parameter(name="value", value_from=ValueFrom(path="/tmp/value"))])
    def fanout(object: dict):
        print("Received object: {object}!".format(object=object))
        # Output the content of the "value" key in the object
        value = object["value"]
        with open("/tmp/value", "w") as f:
            f.write(str(value))


    @script()
    def fanin(values: list):
        print("Received values: {values}!".format(values=values))


    # assumes you used `hera.set_global_token` and `hera.set_global_host` so that the workflow can be submitted
    with Workflow(generate_name="dynamic-fanout-fanin", entrypoint="d") as w:
        with DAG(name="d"):
            g = generate()
            fout = fanout(with_param=g.result)
            fin = fanin(arguments=fout.get_parameter("value").with_name("values"))
            g >> fout >> fin
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: dynamic-fanout-fanin
    spec:
      entrypoint: d
      templates:
      - name: d
        dag:
          tasks:
          - name: generate
            template: generate
          - name: fanout
            depends: generate
            template: fanout
            withParam: '{{tasks.generate.outputs.result}}'
            arguments:
              parameters:
              - name: object
                value: '{{item}}'
          - name: fanin
            depends: fanout
            template: fanin
            arguments:
              parameters:
              - name: values
                value: '{{tasks.fanout.outputs.parameters.value}}'
      - name: generate
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            import sys
            json.dump([{'value': i} for i in range(10)], sys.stdout)
          command:
          - python
      - name: fanout
        inputs:
          parameters:
          - name: object
        outputs:
          parameters:
          - name: value
            valueFrom:
              path: /tmp/value
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: object = json.loads(r'''{{inputs.parameters.object}}''')
            except: object = r'''{{inputs.parameters.object}}'''

            print('Received object: {object}!'.format(object=object))
            value = object['value']
            with open('/tmp/value', 'w') as f:
                f.write(str(value))
          command:
          - python
      - name: fanin
        inputs:
          parameters:
          - name: values
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: values = json.loads(r'''{{inputs.parameters.values}}''')
            except: values = r'''{{inputs.parameters.values}}'''

            print('Received values: {values}!'.format(values=values))
          command:
          - python
    ```


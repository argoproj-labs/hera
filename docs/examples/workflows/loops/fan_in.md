# Fan In



This example shows how to collect values in a "fan-in" task after the fan-out.

This also works for the `result` output parameter (as long as nothing else is in stdout!).


=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Parameter, Workflow, script
    from hera.workflows.models import ValueFrom


    @script()
    def generate():
        import json
        import sys

        json.dump([{"value": i} for i in range(10)], sys.stdout)


    @script(
        outputs=[
            Parameter(
                name="value",
                value_from=ValueFrom(path="/tmp/value"),
            )
        ]
    )
    def fanout(my_dict: dict):
        print("Received object: {my_dict}!".format(my_dict=my_dict))
        # Output the content of the "value" key in the dict
        value = my_dict["value"]
        with open("/tmp/value", "w") as f:
            f.write(str(value))


    @script()
    def fanin(values: list):
        print("Received values: {values}!".format(values=values))


    with Workflow(generate_name="fan-in-", entrypoint="d") as w:
        with DAG(name="d"):
            g = generate()
            fout = fanout(with_param=g.result)
            fin = fanin(arguments={"values": fout.get_parameter("value")})
            g >> fout >> fin
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: fan-in-
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
              - name: my_dict
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
          image: python:3.10
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
          - name: my_dict
        outputs:
          parameters:
          - name: value
            valueFrom:
              path: /tmp/value
        script:
          image: python:3.10
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: my_dict = json.loads(r'''{{inputs.parameters.my_dict}}''')
            except: my_dict = r'''{{inputs.parameters.my_dict}}'''

            print('Received object: {my_dict}!'.format(my_dict=my_dict))
            value = my_dict['value']
            with open('/tmp/value', 'w') as f:
                f.write(str(value))
          command:
          - python
      - name: fanin
        inputs:
          parameters:
          - name: values
        script:
          image: python:3.10
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


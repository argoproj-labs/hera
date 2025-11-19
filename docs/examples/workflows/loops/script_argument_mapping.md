# Script Argument Mapping



This example shows how Hera can automatically map the values in a `with_items` dictionary.

See how to do this dynamically in the [JSON payload fanout](json_payload_fanout.md) example.


=== "Hera"

    ```python linenums="1"
    from hera.workflows import Steps, Workflow, script


    @script()
    def test_key_mapping(key_1: str, key_2: str):
        print("{key_1}, {key_2}".format(key_1=key_1, key_2=key_2))


    with Workflow(
        generate_name="script-argument-mapping-",
        entrypoint="steps",
    ) as w:
        with Steps(name="steps"):
            test_key_mapping(
                with_items=[
                    {"key_1": "value:1-1", "key_2": "value:2-1"},
                    {"key_1": "value:1-2", "key_2": "value:2-2"},
                    {"key_1": "value:1-3", "key_2": "value:2-3"},
                    {"key_1": "value:1-4", "key_2": "value:2-4"},
                ],
            )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: script-argument-mapping-
    spec:
      entrypoint: steps
      templates:
      - name: steps
        steps:
        - - name: test-key-mapping
            template: test-key-mapping
            withItems:
            - key_1: value:1-1
              key_2: value:2-1
            - key_1: value:1-2
              key_2: value:2-2
            - key_1: value:1-3
              key_2: value:2-3
            - key_1: value:1-4
              key_2: value:2-4
            arguments:
              parameters:
              - name: key_1
                value: '{{item.key_1}}'
              - name: key_2
                value: '{{item.key_2}}'
      - name: test-key-mapping
        inputs:
          parameters:
          - name: key_1
          - name: key_2
        script:
          image: python:3.10
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: key_1 = json.loads(r'''{{inputs.parameters.key_1}}''')
            except: key_1 = r'''{{inputs.parameters.key_1}}'''
            try: key_2 = json.loads(r'''{{inputs.parameters.key_2}}''')
            except: key_2 = r'''{{inputs.parameters.key_2}}'''

            print('{key_1}, {key_2}'.format(key_1=key_1, key_2=key_2))
          command:
          - python
    ```


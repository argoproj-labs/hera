# Basic Fanout



This examples shows some basic hard-coded fan-outs.


=== "Hera"

    ```python linenums="1"
    from hera.shared.serialization import serialize
    from hera.workflows import Steps, Workflow, script


    @script()
    def print_message(message):
        print(message)


    with Workflow(generate_name="loops-", entrypoint="loop-example") as w:
        with Steps(name="loop-example"):
            # We can pass a list of values to `with_items`
            print_message(
                name="print-message-loop-with-items-list",
                arguments={"message": "{{item}}"},
                with_items=["hello world", "goodbye world"],
            )

            # Or we can skip the arguments kwarg and string templating
            # syntax by passing a list of dictionaries
            print_message(
                name="print-message-loop-with-items-dict",
                with_items=[
                    {"message": "hello world"},
                    {"message": "goodbye world"},
                ],
            )

            # We can still pass a list of dict values to `with_items`, but must
            # serialize them using Hera's `serialize` function
            print_message(
                name="print-message-loop-with-items-list-of-dicts",
                arguments={"message": "{{item}}"},
                with_items=[
                    serialize(item)
                    for item in [
                        {"my-key": "hello world"},
                        {"my-other-key": "goodbye world"},
                    ]
                ],
            )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: loops-
    spec:
      entrypoint: loop-example
      templates:
      - name: loop-example
        steps:
        - - name: print-message-loop-with-items-list
            template: print-message
            withItems:
            - hello world
            - goodbye world
            arguments:
              parameters:
              - name: message
                value: '{{item}}'
        - - name: print-message-loop-with-items-dict
            template: print-message
            withItems:
            - message: hello world
            - message: goodbye world
            arguments:
              parameters:
              - name: message
                value: '{{item}}'
        - - name: print-message-loop-with-items-list-of-dicts
            template: print-message
            withItems:
            - '{"my-key": "hello world"}'
            - '{"my-other-key": "goodbye world"}'
            arguments:
              parameters:
              - name: message
                value: '{{item}}'
      - name: print-message
        inputs:
          parameters:
          - name: message
        script:
          image: python:3.10
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: message = json.loads(r'''{{inputs.parameters.message}}''')
            except: message = r'''{{inputs.parameters.message}}'''

            print(message)
          command:
          - python
    ```


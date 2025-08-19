# Cron Hello World



This example shows a minimal `CronWorkflow`, based on the [Hello World example](hello_world.md).


=== "Hera"

    ```python linenums="1"
    from hera.workflows import CronWorkflow, script


    @script()
    def hello(s: str):
        print("Hello, {s}!".format(s=s))


    with CronWorkflow(
        name="hello-world-cron",
        entrypoint="hello",
        arguments={"s": "world"},
        schedules=[
            "*/2 * * * *",  # Run every 2 minutes
        ],
    ) as w:
        hello()
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: CronWorkflow
    metadata:
      name: hello-world-cron
    spec:
      schedules:
      - '*/2 * * * *'
      workflowSpec:
        entrypoint: hello
        templates:
        - name: hello
          inputs:
            parameters:
            - name: s
          script:
            image: python:3.9
            source: |-
              import os
              import sys
              sys.path.append(os.getcwd())
              import json
              try: s = json.loads(r'''{{inputs.parameters.s}}''')
              except: s = r'''{{inputs.parameters.s}}'''

              print('Hello, {s}!'.format(s=s))
            command:
            - python
        arguments:
          parameters:
          - name: s
            value: world
    ```


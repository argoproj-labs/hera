# Workflow With Global Params






=== "Hera"

    ```python linenums="1"
    from hera.workflows import Parameter, Script, WorkflowTemplate


    def foo(v):
        print(v)


    with WorkflowTemplate(
        generate_name="global-parameters-", entrypoint="s", arguments=Parameter(name="v", value="42")
    ) as w:
        Script(name="s", source=foo, inputs=[w.get_parameter("v")])
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: WorkflowTemplate
    metadata:
      generateName: global-parameters-
    spec:
      arguments:
        parameters:
        - name: v
          value: '42'
      entrypoint: s
      templates:
      - inputs:
          parameters:
          - name: v
            value: '{{workflow.parameters.v}}'
        name: s
        script:
          command:
          - python
          image: python:3.8
          source: 'import os

            import sys

            sys.path.append(os.getcwd())

            import json

            try: v = json.loads(r''''''{{inputs.parameters.v}}'''''')

            except: v = r''''''{{inputs.parameters.v}}''''''


            print(v)'
    ```


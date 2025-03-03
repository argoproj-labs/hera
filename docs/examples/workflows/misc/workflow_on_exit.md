# Workflow On Exit






=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Workflow, WorkflowStatus, script


    @script()
    def echo(s: str):
        print(s)


    with Workflow(generate_name="on-exit-", entrypoint="d") as w:
        with DAG(name="exit-procedure") as exit_procedure:
            (
                echo(name="t3", arguments={"s": 1}).on_workflow_status(WorkflowStatus.succeeded)
                >> echo(name="t4", arguments={"s": 2}).on_workflow_status(WorkflowStatus.succeeded)
            )

            (
                echo(name="t5", arguments={"s": "3"}).on_workflow_status(WorkflowStatus.error)
                >> echo(name="t6", arguments={"s": "4"}).on_workflow_status(WorkflowStatus.error)
            )

        with DAG(name="d"):
            echo(name="t1", arguments={"s": "a"}) >> echo(name="t2", arguments={"s": "b"})
        w.on_exit = exit_procedure
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: on-exit-
    spec:
      entrypoint: d
      onExit: exit-procedure
      templates:
      - name: exit-procedure
        dag:
          tasks:
          - name: t3
            template: echo
            when: '{{workflow.status}} == Succeeded'
            arguments:
              parameters:
              - name: s
                value: '1'
          - name: t4
            depends: t3
            template: echo
            when: '{{workflow.status}} == Succeeded'
            arguments:
              parameters:
              - name: s
                value: '2'
          - name: t5
            template: echo
            when: '{{workflow.status}} == Error'
            arguments:
              parameters:
              - name: s
                value: '3'
          - name: t6
            depends: t5
            template: echo
            when: '{{workflow.status}} == Error'
            arguments:
              parameters:
              - name: s
                value: '4'
      - name: echo
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

            print(s)
          command:
          - python
      - name: d
        dag:
          tasks:
          - name: t1
            template: echo
            arguments:
              parameters:
              - name: s
                value: a
          - name: t2
            depends: t1
            template: echo
            arguments:
              parameters:
              - name: s
                value: b
    ```


# Run Script On Task Exit



This example shows how to add an `on_exit` (aka an "exit handler") script template to a task.

You will need to use the `Script` class directly, instead of a `script`-decorated function.


=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Script, Workflow, script


    @script()
    def hello(s: str):
        print("Hello Hera, {s}".format(s=s))


    def bye():
        print("Bye Hera")


    with Workflow(generate_name="task-exit-handler-", entrypoint="d") as w:
        bye_ = Script(name="bye", source=bye)
        with DAG(name="d"):
            h1 = hello(name="s1", arguments={"s": "from Task1"})
            h1.on_exit = bye_
            h2 = hello(name="s2", arguments={"s": "from Task2"})

            h1 >> h2
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: task-exit-handler-
    spec:
      entrypoint: d
      templates:
      - name: bye
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            print('Bye Hera')
          command:
          - python
      - name: d
        dag:
          tasks:
          - name: s1
            onExit: bye
            template: hello
            arguments:
              parameters:
              - name: s
                value: from Task1
          - name: s2
            depends: s1
            template: hello
            arguments:
              parameters:
              - name: s
                value: from Task2
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

            print('Hello Hera, {s}'.format(s=s))
          command:
          - python
    ```


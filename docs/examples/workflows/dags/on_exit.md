# On Exit






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
          command:
          - python
          image: python:3.8
          source: 'import os

            import sys

            sys.path.append(os.getcwd())

            print(''Bye Hera'')'
      - dag:
          tasks:
          - arguments:
              parameters:
              - name: s
                value: from Task1
            name: s1
            onExit: bye
            template: hello
          - arguments:
              parameters:
              - name: s
                value: from Task2
            depends: s1
            name: s2
            template: hello
        name: d
      - inputs:
          parameters:
          - name: s
        name: hello
        script:
          command:
          - python
          image: python:3.8
          source: 'import os

            import sys

            sys.path.append(os.getcwd())

            import json

            try: s = json.loads(r''''''{{inputs.parameters.s}}'''''')

            except: s = r''''''{{inputs.parameters.s}}''''''


            print(''Hello Hera, {s}''.format(s=s))'
    ```


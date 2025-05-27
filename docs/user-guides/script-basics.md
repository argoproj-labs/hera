# Script Basics

The `script` decorator is an essential part of Hera's extension on top of Argo, enabling you to run any Python function
as a Kubernetes container.
[Script templates](https://argo-workflows.readthedocs.io/en/latest/walk-through/scripts-and-results/) can run other
scripting languages, but in Hera, running Python becomes the standard.

## Script Decorator

The `script` decorator can turn any user-defined function into a template for Argo. Call the function under a Hera
context manager such as a `Workflow` or `Steps`/`DAG` context to create templates or an individual `Step`/`Task`. The
function will still behave as normal outside of Hera contexts, meaning you can write unit tests on the given function.

When decorating a function, you should pass `Script` parameters to the `script` decorator. This includes values such as
the `image` to use, and `resources` to request. Your function's input arguments will automatically become input
parameters to the script template.

```py
from hera.workflows import Resources, script

@script(image="python:3.11", resources=Resources(memory_request="5Gi"))
def echo(message: str):
    print(message)
```

When calling the function under a `Steps` or `DAG` context, you should pass `Step` or `Task` kwargs, such as the `name`
of the `Step`/`Task`, a `when` clause, `arguments` for the function, or a `with_param` list to loop over a given
template.

=== "Hera"

    ```py
    with Workflow(generate_name="dag-diamond-", entrypoint="diamond") as w:
        with DAG(name="diamond"):
            A = echo(name="A", arguments={"message": "A"})
            B = echo(name="B", arguments={"message": "B"}, when=f"{A.result} == 'A'")
            C = echo(name="C", arguments={"message": "C"}, when=f"{A.result} != 'A'")
            D = echo(name="D", arguments={"message": "D"})
            A >> [B, C] >> D
    ```

=== "YAML"

    ```yaml
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: dag-diamond-
    spec:
      entrypoint: diamond
      templates:
      - name: diamond
        dag:
          tasks:
          - name: A
            template: echo
            arguments:
              parameters:
              - name: message
                value: A
          - name: B
            depends: A
            template: echo
            when: '{{tasks.A.outputs.result}} == ''A'''
            arguments:
              parameters:
              - name: message
                value: B
          - name: C
            depends: A
            template: echo
            when: '{{tasks.A.outputs.result}} != ''A'''
            arguments:
              parameters:
              - name: message
                value: C
          - name: D
            depends: B && C
            template: echo
            arguments:
              parameters:
              - name: message
                value: D
      - name: echo
        inputs:
          parameters:
          - name: message
        script:
          image: python:3.12
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

<details><summary><i>How it works</i></summary>

The <code>script</code> decorator function prepares a <code>Script</code> object so that, when your function is invoked
under a Hera context, the call is redirected to the <code>Script.__call__</code> function. This takes the kwargs of a
<code>Step</code> or <code>Task</code> depending on whether the context manager is a <code>Steps</code> or a
<code>DAG</code>. Under a Workflow itself, your function is not expected to take arguments, so the call will add the
function as a template.

</details>

This acts as syntactic sugar for the alternative of using `Script` and `Task` directly to construct the Workflow and
DAG:

=== "Hera"

    ```py
    def echo(message):
        print(message)

    with Workflow(generate_name="dag-diamond-", entrypoint="diamond") as w:
        echo_template = Script(name="echo", source=echo, image="python:3.11", resources=Resources(memory_request="5Gi"))
        with DAG(name="diamond"):
            A = Task(name="A", template=echo_template, arguments={"message": "A"})
            B = Task(name="B", template=echo_template, arguments={"message": "B"}, when=f"{A.result} == 'A'")
            C = Task(name="C", template=echo_template, arguments={"message": "C"}, when=f"{A.result} != 'A'")
            D = Task(name="D", template=echo_template, arguments={"message": "D"})
            A >> [B, C] >> D
    ```

=== "YAML"

    ```yaml
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: dag-diamond-
    spec:
      entrypoint: diamond
      templates:
      - name: echo
        inputs:
          parameters:
          - name: message
        script:
          image: python:3.11
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
          resources:
            requests:
              memory: 5Gi
      - name: diamond
        dag:
          tasks:
          - name: A
            template: echo
            arguments:
              parameters:
              - name: message
                value: A
          - name: B
            depends: A
            template: echo
            when: '{{tasks.A.outputs.result}} == ''A'''
            arguments:
              parameters:
              - name: message
                value: B
          - name: C
            depends: A
            template: echo
            when: '{{tasks.A.outputs.result}} != ''A'''
            arguments:
              parameters:
              - name: message
                value: C
          - name: D
            depends: B && C
            template: echo
            arguments:
              parameters:
              - name: message
                value: D
    ```

## Script Constructors

Script constructors transform a script function into the template seen in YAML. Hera offers two built-in constructors
for you to use and extend. Read about them in [Script Constructors](script-constructors.md).

# Dag Configurable Rshift



This example shows how to override the defaults for the "next" function to configure the rshift (`>>`) behaviour.

This is useful if you want `A >> B` to mean "run B _only if_ A succeeded", otherwise the
[default depends logic](https://argo-workflows.readthedocs.io/en/latest/enhanced-depends-logic/) means `A >> B` is
equivalent to "B depends on `A.Succeeded || A.Skipped || A.Daemoned`".

By setting the values in `Task.set_next_defaults`, we can configure the rshift behaviour to use a different operator
and TaskResult. Then, the following

```py
with Task.set_next_defaults(operator=Operator.or_, on=TaskResult.succeeded):
    A >> [B, C] >> D
```

is equivalent to

```py
A.next(B, on=TaskResult.succeeded)
A.next(C, on=TaskResult.succeeded)
B.next(D, on=TaskResult.succeeded)
C.next(D, operator=Operator.or_, on=TaskResult.succeeded)
```

> Note the `Operator.or_` for D's `depends` is set when calling `C.next` which can also be confusing! This is because we
> use `next` to describe the forward relationships, while the Argo field is `depends` which describes the backward
> relationships.

Or, described using the backward relationship of `depends` (which only accepts strings):
```py
B.depends = "A.Succeeded"
C.depends = "A.Succeeded"
D.depends = "B.Succeeded || C.Succeeded"
```


=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Task, TaskResult, Workflow, script
    from hera.workflows.operator import Operator


    @script(image="python:3.12")
    def echo(message):
        print(message)


    with Workflow(generate_name="dag-configurable-rshift-", entrypoint="diamond") as w:
        with DAG(name="diamond"):
            A = echo(name="A", arguments={"message": "A"})
            B = echo(name="B", arguments={"message": "B"})
            C = echo(name="C", arguments={"message": "C"})
            D = echo(name="D", arguments={"message": "D"})

            with Task.set_next_defaults(operator=Operator.or_, on=TaskResult.succeeded):
                A >> [B, C] >> D
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: dag-configurable-rshift-
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
            depends: A.Succeeded
            template: echo
            arguments:
              parameters:
              - name: message
                value: B
          - name: C
            depends: A.Succeeded
            template: echo
            arguments:
              parameters:
              - name: message
                value: C
          - name: D
            depends: B.Succeeded || C.Succeeded
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


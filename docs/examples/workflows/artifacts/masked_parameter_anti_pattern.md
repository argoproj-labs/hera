# Masked Parameter Anti Pattern



This example shows an anti-pattern.

The example uses a parameter name that is the same as an input Artifact. This approach in inline scripts will generally
cause confusion, but it can be useful for testing the function, as you can pass a value for the Artifact directly to the
function (but you still cannot `return` a value). The Hera Runner is the more complete and recommended solution.

## Anti-Pattern Explanation

Firstly, the name of the Artifact is not programatically linked to the function parameter name. One is a string, while
the other is a variable symbol, changing one (through an IDE refactor) will not affect the other:

```py
@script(inputs=Artifact(name="i", path="/tmp/i"))
def consume(i):
```

At runtime on Argo Workflows, the function parameter has no value.

```py
@script(inputs=Artifact(name="i", path="/tmp/i"))
def consume(i):
    print(i) # -> `None`
```

You must load from a file:

```py
    with open("/tmp/i", "rb") as f:
```

And use `None`-checking code in the function to allow usage on Argo and locally:

```py
    with open("/tmp/i", "rb") as f:
        i = i or pickle.load(f)
    print(i)
```

Plus, for local testing, you cannot actually `return` a value due to Argo Workflows limitations, so can only print or
write to a file.

Instead, it is recommended to use the Hera Runner,
[see the Artifact example using the Hera Runner](../hera-runner/runner_artifacts.md).


=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Artifact, Workflow, script


    @script(outputs=Artifact(name="result-art", path="/tmp/result"))
    def produce():
        import pickle

        result = "foo testing"
        with open("/tmp/result", "wb") as f:
            pickle.dump(result, f)


    @script(inputs=Artifact(name="i", path="/tmp/i"))
    def consume(i):  # Note that the parameter name is the same as the input Artifact name
        import pickle

        with open("/tmp/i", "rb") as f:
            i = pickle.load(f)
        print(i)


    with Workflow(generate_name="masked-parameter-", entrypoint="d") as w:
        with DAG(name="d"):
            p = produce()
            c = consume(arguments={"i": p.get_artifact("result-art")})
            p >> c
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: masked-parameter-
    spec:
      entrypoint: d
      templates:
      - name: d
        dag:
          tasks:
          - name: produce
            template: produce
          - name: consume
            depends: produce
            template: consume
            arguments:
              artifacts:
              - name: i
                from: '{{tasks.produce.outputs.artifacts.result-art}}'
      - name: produce
        outputs:
          artifacts:
          - name: result-art
            path: /tmp/result
        script:
          image: python:3.10
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import pickle
            result = 'foo testing'
            with open('/tmp/result', 'wb') as f:
                pickle.dump(result, f)
          command:
          - python
      - name: consume
        inputs:
          artifacts:
          - name: i
            path: /tmp/i
        script:
          image: python:3.10
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import pickle
            with open('/tmp/i', 'rb') as f:
                i = pickle.load(f)
            print(i)
          command:
          - python
    ```


# Script Auto Infer






=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Artifact, Workflow, script


    @script(outputs=Artifact(name="result", path="/tmp/result"))
    def produce():
        import pickle

        result = "foo testing"
        with open("/tmp/result", "wb") as f:
            pickle.dump(result, f)


    @script(inputs=Artifact(name="i", path="/tmp/i"))
    def consume(i):
        import pickle

        with open("/tmp/i", "rb") as f:
            i = pickle.load(f)
        print(i)


    with Workflow(generate_name="fv-test-", entrypoint="d") as w:
        with DAG(name="d"):
            p = produce()
            c = consume(arguments=Artifact(name="i", from_="{{tasks.produce.outputs.artifacts.result}}"))
            p >> c
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: fv-test-
    spec:
      entrypoint: d
      templates:
      - dag:
          tasks:
          - name: produce
            template: produce
          - arguments:
              artifacts:
              - from: '{{tasks.produce.outputs.artifacts.result}}'
                name: i
            depends: produce
            name: consume
            template: consume
        name: d
      - name: produce
        outputs:
          artifacts:
          - name: result
            path: /tmp/result
        script:
          command:
          - python
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import pickle
            result = 'foo testing'
            with open('/tmp/result', 'wb') as f:
                pickle.dump(result, f)
      - inputs:
          artifacts:
          - name: i
            path: /tmp/i
        name: consume
        script:
          command:
          - python
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import pickle
            with open('/tmp/i', 'rb') as f:
                i = pickle.load(f)
            print(i)
    ```


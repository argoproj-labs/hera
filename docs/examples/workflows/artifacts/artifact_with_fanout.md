# Artifact With Fanout






=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Artifact, NoneArchiveStrategy, Workflow, script


    @script(outputs=Artifact(name="out-art", path="/tmp/file", archive=NoneArchiveStrategy()))
    def writer():
        import json

        with open("/tmp/file", "w+") as f:
            for i in range(10):
                f.write(json.dumps(i) + "\n")


    @script(inputs=Artifact(name="in-art", path="/tmp/file"))
    def fanout():
        import json
        import sys

        indices = []
        with open("/tmp/file", "r") as f:
            for line in f.readlines():
                indices.append(line.strip())
        json.dump(indices, sys.stdout)


    @script()
    def consumer(i: int):
        print(i)


    with Workflow(generate_name="artifact-with-fanout-", entrypoint="d") as w:
        with DAG(name="d"):
            w_ = writer()
            f = fanout(arguments=w_.get_artifact("out-art").with_name("in-art"))
            c = consumer(with_param=f.result)
            w_ >> f >> c
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: artifact-with-fanout-
    spec:
      entrypoint: d
      templates:
      - name: d
        dag:
          tasks:
          - name: writer
            template: writer
          - name: fanout
            depends: writer
            template: fanout
            arguments:
              artifacts:
              - name: in-art
                from: '{{tasks.writer.outputs.artifacts.out-art}}'
          - name: consumer
            depends: fanout
            template: consumer
            withParam: '{{tasks.fanout.outputs.result}}'
            arguments:
              parameters:
              - name: i
                value: '{{item}}'
      - name: writer
        outputs:
          artifacts:
          - name: out-art
            path: /tmp/file
            archive:
              none: {}
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            with open('/tmp/file', 'w+') as f:
                for i in range(10):
                    f.write(json.dumps(i) + '\n')
          command:
          - python
      - name: fanout
        inputs:
          artifacts:
          - name: in-art
            path: /tmp/file
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            import sys
            indices = []
            with open('/tmp/file', 'r') as f:
                for line in f.readlines():
                    indices.append(line.strip())
            json.dump(indices, sys.stdout)
          command:
          - python
      - name: consumer
        inputs:
          parameters:
          - name: i
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: i = json.loads(r'''{{inputs.parameters.i}}''')
            except: i = r'''{{inputs.parameters.i}}'''

            print(i)
          command:
          - python
    ```


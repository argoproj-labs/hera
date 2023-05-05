# Artifact With Fanout






=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Artifact, Workflow, script


    @script(outputs=Artifact(name="test", path="/file"))
    def writer():
        import json

        with open("/file", "w+") as f:
            for i in range(10):
                f.write(f"{json.dumps(i)}\n")


    @script(inputs=Artifact(name="test", path="/file"))
    def fanout():
        import json
        import sys

        indices = []
        with open("/file", "r") as f:
            for line in f.readlines():
                indices.append(line.strip())
        json.dump(indices, sys.stdout)


    @script()
    def consumer(i: int):
        print(i)


    # assumes you used `hera.set_global_token` and `hera.set_global_host` so that the workflow can be submitted
    with Workflow(generate_name="artifact-with-fanout-", entrypoint="d") as w:
        with DAG(name="d"):
            w_ = writer()
            f = fanout(arguments=w_.get_artifact("test"))
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
      - dag:
          tasks:
          - name: writer
            template: writer
          - arguments:
              artifacts:
              - from: '{{tasks.writer.outputs.artifacts.test}}'
                name: test
                path: /file
            depends: writer
            name: fanout
            template: fanout
          - arguments:
              parameters:
              - name: i
                value: '{{item}}'
            depends: fanout
            name: consumer
            template: consumer
            withParam: '{{tasks.fanout.outputs.result}}'
        name: d
      - name: writer
        outputs:
          artifacts:
          - name: test
            path: /file
        script:
          command:
          - python
          image: python:3.8
          source: "import os\nimport sys\nsys.path.append(os.getcwd())\n    import json\n\
            \    with open('/file', 'w+') as f:\n        for i in range(10):\n       \
            \     f.write(f'''{json.dumps(i)}\n''')"
      - inputs:
          artifacts:
          - name: test
            path: /file
        name: fanout
        script:
          command:
          - python
          image: python:3.8
          source: "import os\nimport sys\nsys.path.append(os.getcwd())\nimport json\n\
            import sys\nindices = []\nwith open('/file', 'r') as f:\n    for line in f.readlines():\n\
            \        indices.append(line.strip())\njson.dump(indices, sys.stdout)"
      - inputs:
          parameters:
          - name: i
        name: consumer
        script:
          command:
          - python
          image: python:3.8
          source: 'import os

            import sys

            sys.path.append(os.getcwd())

            import json

            try: i = json.loads(r''''''{{inputs.parameters.i}}'''''')

            except: i = r''''''{{inputs.parameters.i}}''''''


            print(i)'
    ```


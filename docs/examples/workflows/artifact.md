# Artifact



This example showcases a simple artifact passing mechanism between two tasks.
The first task, writer, creates a file located at `/file` containing a message. The second
task, consumer, takes this artifact, places it at its own `/file` path, and print out the content.


=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Artifact, Workflow, script


    @script(outputs=Artifact(name="test", path="/file"))
    def writer():
        with open("/file", "w+") as f:
            f.write("Hello, world!")


    @script(inputs=Artifact(name="test", path="/file"))
    def consumer():
        with open("/file", "r") as f:
            print(f.readlines())  # prints `Hello, world!` to `stdout`


    with Workflow(generate_name="artifact-", entrypoint="d") as w:
        with DAG(name="d"):
            w_ = writer()
            c = consumer(arguments={"test": w_.get_artifact("test")})
            w_ >> c
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: artifact-
    spec:
      entrypoint: d
      templates:
      - dag:
          tasks:
          - name: writer
            template: writer
          - arguments:
              parameters:
              - name: test
                value: '{"name": "test", "archive": null, "archive_logs": null, "artifact_gc":
                  null, "deleted": null, "from_": "{{tasks.writer.outputs.artifacts.test}}",
                  "from_expression": null, "global_name": null, "mode": null, "path":
                  "/file", "recurse_mode": null, "sub_path": null}'
            depends: writer
            name: consumer
            template: consumer
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
          source: "import os\nimport sys\nsys.path.append(os.getcwd())\nwith open('/file',\
            \ 'w+') as f:\n    f.write('Hello, world!')"
      - inputs:
          artifacts:
          - name: test
            path: /file
        name: consumer
        script:
          command:
          - python
          image: python:3.8
          source: "import os\nimport sys\nsys.path.append(os.getcwd())\nwith open('/file',\
            \ 'r') as f:\n    print(f.readlines())"
    ```


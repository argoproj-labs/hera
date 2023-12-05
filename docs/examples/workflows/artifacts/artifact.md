# Artifact



This example showcases a simple artifact passing mechanism between two tasks.
The first task, writer, creates a file located at `/file` containing a message. The second
task, consumer, takes this artifact, places it at its own `/file` path, and print out the content.


=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Artifact, NoneArchiveStrategy, Workflow, script


    @script(outputs=Artifact(name="out-art", path="/tmp/file", archive=NoneArchiveStrategy()))
    def writer():
        with open("/tmp/file", "w+") as f:
            f.write("Hello, world!")


    @script(inputs=Artifact(name="in-art", path="/tmp/file"))
    def consumer():
        with open("/tmp/file", "r") as f:
            print(f.readlines())  # prints `Hello, world!` to `stdout`


    with Workflow(generate_name="artifact-", entrypoint="d") as w:
        with DAG(name="d"):
            w_ = writer()
            c = consumer(arguments=w_.get_artifact("out-art").with_name("in-art"))
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
              artifacts:
              - from: '{{tasks.writer.outputs.artifacts.out-art}}'
                name: in-art
            depends: writer
            name: consumer
            template: consumer
        name: d
      - name: writer
        outputs:
          artifacts:
          - archive:
              none: {}
            name: out-art
            path: /tmp/file
        script:
          command:
          - python
          image: python:3.8
          source: "import os\nimport sys\nsys.path.append(os.getcwd())\nwith open('/tmp/file',\
            \ 'w+') as f:\n    f.write('Hello, world!')"
      - inputs:
          artifacts:
          - name: in-art
            path: /tmp/file
        name: consumer
        script:
          command:
          - python
          image: python:3.8
          source: "import os\nimport sys\nsys.path.append(os.getcwd())\nwith open('/tmp/file',\
            \ 'r') as f:\n    print(f.readlines())"
    ```


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
      - name: d
        dag:
          tasks:
          - name: writer
            template: writer
          - name: consumer
            depends: writer
            template: consumer
            arguments:
              artifacts:
              - name: in-art
                from: '{{tasks.writer.outputs.artifacts.out-art}}'
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
            with open('/tmp/file', 'w+') as f:
                f.write('Hello, world!')
          command:
          - python
      - name: consumer
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
            with open('/tmp/file', 'r') as f:
                print(f.readlines())
          command:
          - python
    ```


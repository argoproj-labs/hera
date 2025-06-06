# Script Artifact Passing






=== "Hera"

    ```python linenums="1"
    from hera.workflows import Artifact, Steps, Workflow, script


    @script(outputs=Artifact(name="hello-art", path="/tmp/hello_world.txt"))
    def whalesay():
        with open("/tmp/hello_world.txt", "w") as f:
            f.write("hello world")


    @script(inputs=Artifact(name="message", path="/tmp/message"))
    def print_message():
        with open("/tmp/message", "r") as f:
            message = f.readline()
        print(message)


    with Workflow(generate_name="artifact-passing-", entrypoint="artifact-example") as w:
        with Steps(name="artifact-example") as s:
            whale_step = whalesay(name="generate-artifact")
            print_message(
                name="consume-artifact",
                arguments=whale_step.get_artifact("hello-art").with_name("message"),
            )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: artifact-passing-
    spec:
      entrypoint: artifact-example
      templates:
      - name: artifact-example
        steps:
        - - name: generate-artifact
            template: whalesay
        - - name: consume-artifact
            template: print-message
            arguments:
              artifacts:
              - name: message
                from: '{{steps.generate-artifact.outputs.artifacts.hello-art}}'
      - name: whalesay
        outputs:
          artifacts:
          - name: hello-art
            path: /tmp/hello_world.txt
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            with open('/tmp/hello_world.txt', 'w') as f:
                f.write('hello world')
          command:
          - python
      - name: print-message
        inputs:
          artifacts:
          - name: message
            path: /tmp/message
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            with open('/tmp/message', 'r') as f:
                message = f.readline()
            print(message)
          command:
          - python
    ```


# Script Artifact Passing






=== "Hera"

    ```python linenums="1"
    from hera.workflows import Artifact, Steps, Workflow, script


    @script(outputs=Artifact(name="hello-art", path="/tmp/hello_world.txt"))
    def whalesay():
        with open("/tmp/hello_world.txt", "wb") as f:
            f.write("hello world")


    @script(inputs=Artifact(name="message", path="/tmp/message"))
    def print_message():
        with open("//tmp/message", "rb") as f:
            message = f.readline()
        print(message)


    with Workflow(generate_name="artifact-passing-", entrypoint="artifact-example") as w:
        with Steps(name="artifact-example") as s:
            whalesay(name="generate-artifact")
            print_message(
                name="consume-artifact",
                arguments=[Artifact(name="message", from_="{{steps.generate-artifact.outputs.artifacts.hello-art}}")],
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
        - - arguments:
              artifacts:
              - from: '{{steps.generate-artifact.outputs.artifacts.hello-art}}'
                name: message
            name: consume-artifact
            template: print-message
      - name: whalesay
        outputs:
          artifacts:
          - name: hello-art
            path: /tmp/hello_world.txt
        script:
          command:
          - python
          image: python:3.8
          source: "import os\nimport sys\nsys.path.append(os.getcwd())\nwith open('/tmp/hello_world.txt',\
            \ 'wb') as f:\n    f.write('hello world')"
      - inputs:
          artifacts:
          - name: message
            path: /tmp/message
        name: print-message
        script:
          command:
          - python
          image: python:3.8
          source: "import os\nimport sys\nsys.path.append(os.getcwd())\nwith open('//tmp/message',\
            \ 'rb') as f:\n    message = f.readline()\nprint(message)"
    ```


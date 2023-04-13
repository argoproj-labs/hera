# Exit Handler With Artifacts

> Note: This example is a replication of an Argo Workflow example in Hera. The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/exit-handler-with-artifacts.yaml).

apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: exit-handler-with-artifacts-
  labels:
    workflows.argoproj.io/test: "true"
  annotations:
    workflows.argoproj.io/description: |
      onExitTemplate enables workflow to pass the arguments (parameters/Artifacts) to exit handler template.
    workflows.argoproj.io/version: '>= 3.1.0'
spec:
  entrypoint: main
  templates:
    - name: main
      steps:
        - - name: step-1
            template: output
            hooks:
              exit:
                template: exit
                arguments:
                  artifacts:
                    - name: message
                      from: "{{steps.step-1.outputs.artifacts.result}}"

    - name: output
      script:
        image: python:alpine3.6
        command: [ python ]
        source: |
          with open("result.txt", "w") as f:
            f.write("Welcome")
      outputs:
        artifacts:
          - name: result
            path: /result.txt

    - name: exit
      inputs:
        artifacts:
          - name: message
            path: /tmp/message
      container:
        image: python:alpine3.6
        command: [sh, -c]
        args: ["cat /tmp/message"]


=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        Artifact,
        Container,
        Script,
        Step,
        Steps,
        Workflow,
        models as m,
    )


    def _output():
        with open("result.txt", "w") as f:
            f.write("Welcome")


    with Workflow(
        generate_name="exit-handler-with-artifacts-",
        entrypoint="main",
        labels={"workflows.argoproj.io/test": "true"},
        annotations={
            "workflows.argoproj.io/description": "onExitTemplate enables workflow to pass the arguments "
            "(parameters/Artifacts) to exit handler template.",
            "workflows.argoproj.io/version": ">= 3.1.0",
        },
    ) as w:
        output = Script(
            name="output",
            image="python:alpine3.6",
            command=["python"],
            source=_output,
            outputs=[Artifact(name="result", path="/result.txt")],
            add_cwd_to_sys_path=False,
        )
        exit_ = Container(
            name="exit",
            image="python:alpine3.6",
            command=["sh", "-c"],
            args=["cat /tmp/message"],
            inputs=[Artifact(name="message", path="/tmp/message")],
        )
        with Steps(name="main"):
            Step(
                name="step-1",
                template=output,
                hooks={
                    "exit": m.LifecycleHook(
                        template="exit",
                        arguments=m.Arguments(
                            artifacts=[
                                m.Artifact(
                                    name="message",
                                    from_="{{steps.step-1.outputs.artifacts.result}}",
                                )
                            ],
                        ),
                    )
                },
            )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      annotations:
        workflows.argoproj.io/description: onExitTemplate enables workflow to pass the
          arguments (parameters/Artifacts) to exit handler template.
        workflows.argoproj.io/version: '>= 3.1.0'
      generateName: exit-handler-with-artifacts-
      labels:
        workflows.argoproj.io/test: 'true'
    spec:
      entrypoint: main
      templates:
      - name: output
        outputs:
          artifacts:
          - name: result
            path: /result.txt
        script:
          command:
          - python
          image: python:alpine3.6
          source: "with open('result.txt', 'w') as f:\n    f.write('Welcome')"
      - container:
          args:
          - cat /tmp/message
          command:
          - sh
          - -c
          image: python:alpine3.6
        inputs:
          artifacts:
          - name: message
            path: /tmp/message
        name: exit
      - name: main
        steps:
        - - hooks:
              exit:
                arguments:
                  artifacts:
                  - from: '{{steps.step-1.outputs.artifacts.result}}'
                    name: message
                template: exit
            name: step-1
            template: output
    ```


# Steps Types






=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        Container,
        Parameter,
        Step,
        Steps,
        Workflow,
        models as m,
    )

    my_step = Step(
        name="manually-adding-my-step",
        template="whalesay",
        arguments=[Parameter(name="message", value="hello1")],
    )


    my_steps = [
        Step(
            name="list-of-step-1",
            template="whalesay",
            arguments=[Parameter(name="message", value="hello1")],
        ),
        Step(
            name="list-of-step-2",
            template="whalesay",
            arguments=[Parameter(name="message", value="hello1")],
        ),
    ]

    with Workflow(
        generate_name="steps-",
        entrypoint="hello-hello-hello",
    ) as w:
        whalesay = Container(
            name="whalesay",
            inputs=[Parameter(name="message")],
            image="docker/whalesay",
            command=["cowsay"],
            args=["{{inputs.parameters.message}}"],
        )

        with Steps(name="hello-hello-hello") as s:
            # Manually add a step defined elsewhere
            s.sub_steps.append(my_step)

            # Manually add a list of steps defined elsewhere as sequential steps
            s.sub_steps.extend(my_steps)

            # Manually add a list of steps defined elsewhere as parallel steps
            s.sub_steps.append(my_steps)

            # Add a step to s implicitly through init
            Step(
                name="implicitly-adding-step-on-init",
                template="whalesay",
                arguments=[Parameter(name="message", value="hello1")],
            )

            # Manually add a model WorkflowStep to s
            s.sub_steps.append(
                m.WorkflowStep(
                    name="model-workflow-step",
                    template="whalesay",
                    arguments=m.Arguments(parameters=[m.Parameter(name="message", value="hello-model1")]),
                )
            )

            with s.parallel() as ps:
                # Add a step to ps implicitly through init
                Step(
                    name="parallel-step-1",
                    template="whalesay",
                    arguments=[Parameter(name="message", value="hello2a")],
                )

                # Manually add a model WorkflowStep to ps
                ps.sub_steps.append(
                    m.WorkflowStep(
                        name="parallel-step-2-model-workflow-step",
                        template="whalesay",
                        arguments=m.Arguments(parameters=[m.Parameter(name="message", value="hello-model2b")]),
                    )
                )

        # Fully falling back to add a model Template containing a model WorkflowStep
        w.templates.append(
            m.Template(
                name="my-model-template",
                steps=[
                    [
                        m.WorkflowStep(
                            name="model-template-workflow-step",
                            template="whalesay",
                            arguments=m.Arguments(parameters=[m.Parameter(name="message", value="hello-model-template")]),
                        )
                    ]
                ],
            )
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: steps-
    spec:
      entrypoint: hello-hello-hello
      templates:
      - name: whalesay
        container:
          image: docker/whalesay
          args:
          - '{{inputs.parameters.message}}'
          command:
          - cowsay
        inputs:
          parameters:
          - name: message
      - name: hello-hello-hello
        steps:
        - - name: manually-adding-my-step
            template: whalesay
            arguments:
              parameters:
              - name: message
                value: hello1
        - - name: list-of-step-1
            template: whalesay
            arguments:
              parameters:
              - name: message
                value: hello1
        - - name: list-of-step-2
            template: whalesay
            arguments:
              parameters:
              - name: message
                value: hello1
        - - name: list-of-step-1
            template: whalesay
            arguments:
              parameters:
              - name: message
                value: hello1
          - name: list-of-step-2
            template: whalesay
            arguments:
              parameters:
              - name: message
                value: hello1
        - - name: implicitly-adding-step-on-init
            template: whalesay
            arguments:
              parameters:
              - name: message
                value: hello1
        - - name: model-workflow-step
            template: whalesay
            arguments:
              parameters:
              - name: message
                value: hello-model1
        - - name: parallel-step-1
            template: whalesay
            arguments:
              parameters:
              - name: message
                value: hello2a
          - name: parallel-step-2-model-workflow-step
            template: whalesay
            arguments:
              parameters:
              - name: message
                value: hello-model2b
      - name: my-model-template
        steps:
        - - name: model-template-workflow-step
            template: whalesay
            arguments:
              parameters:
              - name: message
                value: hello-model-template
    ```


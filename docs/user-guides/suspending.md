# Suspending Workflows

A user can pause execution of a Workflow at any time through the Argo UI, or the Argo CLI using `argo suspend`, and
resume the Workflow in the UI or with `argo resume`.

In Hera, you can suspend a Workflow at specific points using `Suspend` templates, making it easy to set up
human-in-the-loop workflows.

## Basic `Suspend` Usage

Use a `Suspend` template to pause the Workflow at any point in a `Steps` or `DAG` context. This Workflow will wait until
a user manually resumes the Workflow (in the UI or CLI):

=== "Hera"

    ```py
    @script()
    def echo(message: str):
        print(message)


    with Workflow(
        generate_name="suspending-workflow-",
        entrypoint="steps",
    ) as w:

        suspend_template = Suspend(name="wait-for-resume")

        with Steps(name="steps"):
            echo(name="s1", arguments={"message": "The next node waits until you resume the workflow"})
            suspend_template(name="suspend")
            echo(name="s2", arguments={"message": "Finished waiting!"})
    ```

=== "YAML"

    ```yaml
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: suspending-workflow-
    spec:
      entrypoint: steps
      templates:
      - name: wait-for-resume
        suspend: {}
      - name: steps
        steps:
        - - name: s1
            template: echo
            arguments:
              parameters:
              - name: message
                value: The next node waits until you resume the workflow
        - - name: suspend
            template: wait-for-resume
        - - name: s2
            template: echo
            arguments:
              parameters:
              - name: message
                value: Finished waiting!
      - name: echo
        inputs:
          parameters:
          - name: message
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: message = json.loads(r'''{{inputs.parameters.message}}''')
            except: message = r'''{{inputs.parameters.message}}'''

            print(message)
          command:
          - python
    ```

## Timed `Suspend` Usage

To pause the Workflow for a specific length of time, pass a value to the `Suspend` template's `duration` variable. A
user can still manually resume the Workflow before the time is up:

=== "Hera"

    ```py
    @script()
    def echo(message: str):
        print(message)


    with Workflow(
        generate_name="suspending-workflow-",
        entrypoint="steps",
    ) as w:

        suspend_template = Suspend(name="wait-10-seconds", duration=10)

        with Steps(name="steps"):
            echo(name="s1", arguments={"message": "The next node will wait for 10 seconds"})
            suspend_template(name="suspend")
            echo(name="s2", arguments={"message": "Finished waiting!"})
    ```

=== "YAML"

    ```yaml
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: suspending-workflow-
    spec:
      entrypoint: steps
      templates:
      - name: wait-10-seconds
        suspend:
          duration: '10'
      - name: steps
        steps:
        - - name: s1
            template: echo
            arguments:
              parameters:
              - name: message
                value: The next node will wait for 10 seconds
        - - name: suspend
            template: wait-10-seconds
        - - name: s2
            template: echo
            arguments:
              parameters:
              - name: message
                value: Finished waiting!
      - name: echo
        inputs:
          parameters:
          - name: message
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: message = json.loads(r'''{{inputs.parameters.message}}''')
            except: message = r'''{{inputs.parameters.message}}'''

            print(message)
          command:
          - python
    ```

## Intermediate Parameters

[Intermediate Parameters](https://argoproj.github.io/argo-workflows/intermediate-inputs/) are an Argo UI feature that
pause a Workflow to wait for user input values.

This Workflow suspends indefinitely, waiting for user input, and echoes the user's input in the next `Step`:

=== "Hera"

    ```py
    @script()
    def echo(message: str):
        print(message)


    with Workflow(
        generate_name="intermediate-parameter-workflow-",
        entrypoint="steps",
    ) as w:

        suspend_template = Suspend(
            name="suspend-with-intermediate-param",
            intermediate_parameters=[Parameter(name="my-message", default="")],
        )

        with Steps(name="steps"):
            suspend_step = suspend_template(name="suspend")
            echo(arguments={"message": suspend_step.get_parameter("my-message")})
    ```

=== "YAML"

    ```yaml
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: intermediate-parameter-workflow-
    spec:
      entrypoint: steps
      templates:
      - name: suspend-with-intermediate-param
        inputs:
          parameters:
          - name: my-message
            default: ''
        outputs:
          parameters:
          - name: my-message
            valueFrom:
              supplied: {}
        suspend: {}
      - name: steps
        steps:
        - - name: suspend
            template: suspend-with-intermediate-param
        - - name: echo
            template: echo
            arguments:
              parameters:
              - name: message
                value: '{{steps.suspend.outputs.parameters.my-message}}'
      - name: echo
        inputs:
          parameters:
          - name: message
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import json
            try: message = json.loads(r'''{{inputs.parameters.message}}''')
            except: message = r'''{{inputs.parameters.message}}'''

            print(message)
          command:
          - python
    ```

We can also
* restrict input options using a list of values passed to `enum`
* set a pre-selected default
* and set a duration to effectively time-out on the user input (using a suitable `when` expression):

=== "Hera"

    ```py
    @script()
    def deploy():
        print("Deploying!")


    with Workflow(
        generate_name="approval-workflow-",
        entrypoint="steps",
    ) as w:

        approval_template = Suspend(
            name="approval",
            intermediate_parameters=[Parameter(name="approve", default="NO", enum=["YES", "NO"])],
            duration="4h",
        )

        with Steps(name="steps"):
            approval = approval_template(name="suspend")
            deploy(when=f'{approval.get_parameter("approve")} == "YES"')
    ```

=== "YAML"

    ```yaml
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: approval-workflow-
    spec:
      entrypoint: steps
      templates:
      - name: approval
        inputs:
          parameters:
          - name: approve
            default: 'NO'
            enum:
            - 'YES'
            - 'NO'
        outputs:
          parameters:
          - name: approve
            valueFrom:
              supplied: {}
        suspend:
          duration: 4h
      - name: steps
        steps:
        - - name: suspend
            template: approval
        - - name: deploy
            template: deploy
            when: '{{steps.suspend.outputs.parameters.approve}} == "YES"'
      - name: deploy
        script:
          image: python:3.9
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            print('Deploying!')
          command:
          - python
    ```

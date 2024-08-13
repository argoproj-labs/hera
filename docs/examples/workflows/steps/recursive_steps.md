# Recursive Steps






=== "Hera"

    ```python linenums="1"
    from hera.workflows import Step, Steps, WorkflowTemplate, script


    @script(constructor="inline")
    def random_roll():
        import random

        return random.randint(0, 2)


    with WorkflowTemplate(name="my-workflow", entrypoint="steps") as w:
        with Steps(name="sub-steps") as sub_steps:
            random_number = random_roll()
            Step(
                name="recurse",
                arguments={"input-num": random_number.result},
                template=sub_steps,
                when=f"{random_number.result} != 0",
            )

        with Steps(name="steps"):
            sub_steps()
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: WorkflowTemplate
    metadata:
      name: my-workflow
    spec:
      entrypoint: steps
      templates:
      - name: sub-steps
        steps:
        - - name: random-roll
            template: random-roll
        - - arguments:
              parameters:
              - name: input-num
                value: '{{steps.random-roll.outputs.result}}'
            name: recurse
            template: sub-steps
            when: '{{steps.random-roll.outputs.result}} != 0'
      - name: random-roll
        script:
          command:
          - python
          image: python:3.8
          source: |-
            import os
            import sys
            sys.path.append(os.getcwd())
            import random
            return random.randint(0, 2)
      - name: steps
        steps:
        - - name: sub-steps
            template: sub-steps
    ```


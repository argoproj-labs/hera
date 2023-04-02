# Callable Coinflip






=== "Hera"

    ```python linenums="1"
    import random

    from hera.shared import global_config
    from hera.workflows import DAG, Script, Workflow, script

    # Note, setting constructor to runner is only possible if the source code is available
    # along with dependencies include hera in the image.
    # Callable is a robust mode that allows you to run any python function
    # and is compatible with pydantic. It automatically parses the input
    # and serializes the output.
    global_config.image = "my-image-with-python-source-code-and-dependencies"
    global_config.set_class_defaults(Script, constructor="runner")


    @script()
    def flip():
        return "heads" if random.randint(0, 1) == 0 else "tails"


    @script()
    def heads():
        return "it was heads"


    @script()
    def tails():
        return "it was tails"


    with Workflow(generate_name="coinflip-", entrypoint="d") as w:
        with DAG(name="d") as s:
            f = flip()
            heads().on_other_result(f, "heads")
            tails().on_other_result(f, "tails")
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: coinflip-
    spec:
      entrypoint: d
      templates:
      - dag:
          tasks:
          - name: flip
            template: flip
          - depends: flip
            name: heads
            template: heads
            when: '{{tasks.flip.outputs.result}} == heads'
          - depends: flip
            name: tails
            template: tails
            when: '{{tasks.flip.outputs.result}} == tails'
        name: d
      - name: flip
        script:
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.callable_coinflip:flip
          command:
          - python
          image: my-image-with-python-source-code-and-dependencies
          source: '{{inputs.parameters}}'
      - name: heads
        script:
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.callable_coinflip:heads
          command:
          - python
          image: my-image-with-python-source-code-and-dependencies
          source: '{{inputs.parameters}}'
      - name: tails
        script:
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.callable_coinflip:tails
          command:
          - python
          image: my-image-with-python-source-code-and-dependencies
          source: '{{inputs.parameters}}'
    ```


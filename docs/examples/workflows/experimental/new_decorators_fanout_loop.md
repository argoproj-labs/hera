# New Decorators Fanout Loop



This example shows how to pass extra Step/Task kwargs when calling a function.

This lets you perform fanouts using `with_items`, set conditions using `when` and more.


=== "Hera"

    ```python linenums="1"
    from hera.shared import global_config
    from hera.workflows import Input, Workflow

    global_config.experimental_features["decorator_syntax"] = True


    w = Workflow(
        generate_name="fanout-workflow-",
    )


    class PrintMessageInput(Input):
        message: str


    @w.script()
    def print_message(inputs: PrintMessageInput):
        print(inputs.message)


    @w.set_entrypoint
    @w.steps()
    def loop_example():
        print_message(
            PrintMessageInput(message="{{item}}"),
            name="print-message-loop-with-items",
            with_items=["hello world", "goodbye world"],
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: fanout-workflow-
    spec:
      entrypoint: loop-example
      templates:
      - name: print-message
        inputs:
          parameters:
          - name: message
        script:
          image: python:3.9
          source: '{{inputs.parameters}}'
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.experimental.new_decorators_fanout_loop:print_message
          command:
          - python
          env:
          - name: hera__script_pydantic_io
            value: ''
      - name: loop-example
        steps:
        - - name: print-message-loop-with-items
            template: print-message
            withItems:
            - hello world
            - goodbye world
            arguments:
              parameters:
              - name: message
                value: '{{item}}'
    ```


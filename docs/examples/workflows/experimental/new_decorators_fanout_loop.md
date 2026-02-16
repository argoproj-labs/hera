# New Decorators Fanout Loop



This example shows how to pass extra Step/Task kwargs when calling a function.

This lets you perform fanouts using `with_items`, set conditions using `when` and more.

!!! warning

    These features are not compatible with local-running of dags and steps, please see
    <https://github.com/argoproj-labs/hera/issues/1492>.


=== "Hera"

    ```python linenums="1"
    from hera.shared import global_config
    from hera.workflows import Input, Workflow

    global_config.experimental_features["decorator_syntax"] = True


    w = Workflow(
        generate_name="fanout-workflow-",
    )


    class PrintMessageInput(Input):
        message: str = ""
        an_int: int = 42


    @w.script()
    def print_message(inputs: PrintMessageInput):
        print(inputs.message)


    @w.script()
    def print_int(inputs: PrintMessageInput):
        print(inputs.an_int)


    @w.set_entrypoint
    @w.steps()
    def loop_example():
        print_message(
            PrintMessageInput(message="{{item}}"),
            name="print-str-message-loop-with-items",
            with_items=["hello world", "goodbye world"],
        )
        # For general use of loops in decorator functions, you will need to
        # use `.model_construct` to pass the `"{{item}}"` string.
        print_int(
            PrintMessageInput.model_construct(an_int="{{item}}"),
            name="print-int-loop-with-items",
            with_items=[42, 123, 321],
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
            default: ''
          - name: an_int
            default: '42'
        script:
          image: python:3.10
          source: '{{inputs.parameters}}'
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.experimental.new_decorators_fanout_loop:print_message
          command:
          - python
      - name: print-int
        inputs:
          parameters:
          - name: message
            default: ''
          - name: an_int
            default: '42'
        script:
          image: python:3.10
          source: '{{inputs.parameters}}'
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.experimental.new_decorators_fanout_loop:print_int
          command:
          - python
      - name: loop-example
        steps:
        - - name: print-str-message-loop-with-items
            template: print-message
            withItems:
            - hello world
            - goodbye world
            arguments:
              parameters:
              - name: message
                value: '{{item}}'
              - name: an_int
                value: '42'
        - - name: print-int-loop-with-items
            template: print-int
            withItems:
            - 42
            - 123
            - 321
            arguments:
              parameters:
              - name: message
                value: ''
              - name: an_int
                value: '{{item}}'
    ```


# Callable Script V1






=== "Hera"

    ```python linenums="1"
    from typing import Annotated, List, Union

    try:
        from pydantic.v1 import BaseModel
    except (ImportError, ModuleNotFoundError):
        from pydantic import BaseModel

    from hera.shared import global_config
    from hera.shared.serialization import serialize
    from hera.workflows import Parameter, RunnerScriptConstructor, Script, Steps, Workflow, script

    # Note, setting constructor to runner is only possible if the source code is available
    # along with dependencies include hera in the image.
    # Callable is a robust mode that allows you to run any python function
    # and is compatible with pydantic. It automatically parses the input
    # and serializes the output.
    global_config.image = "my-image-with-python-source-code-and-dependencies"
    global_config.set_class_defaults(Script, constructor=RunnerScriptConstructor(pydantic_mode=1))
    # Script annotations is still an experimental feature and we need to explicitly opt in to it
    # Note that experimental features are subject to breaking changes in future releases of the same major version
    global_config.experimental_features["script_annotations"] = True


    # An optional pydantic input type
    # hera can automatically de-serialize argo
    # arguments into types denoted by your function's signature
    # as long as they are de-serializable by pydantic
    # This provides auto-magic input parsing with validation
    # provided by pydantic.
    class Input(BaseModel):
        a: int
        b: str = "foo"
        c: Union[str, int, float]

        class Config:
            smart_union = True


    # An optional pydantic output type
    # hera can automatically serialize the output
    # of your function into a json string
    # as long as they are serializable by pydantic or json serializable
    # This provides auto-magic output serialization with validation
    # provided by pydantic.
    class Output(BaseModel):
        output: List[Input]


    @script()
    def my_function(input: Input) -> Output:
        return Output(output=[input])


    # Note that the input type is a list of Input
    # hera can also automatically de-serialize
    # composite types like lists and dicts
    @script()
    def another_function(inputs: List[Input]) -> Output:
        return Output(output=inputs)


    # it also works with raw json strings
    # but those must be explicitly marked as
    # a string type
    @script()
    def str_function(input: str) -> Output:
        # Example function to ensure we are not json parsing
        # string types before passing it to the function
        return Output(output=[Input.parse_raw(input)])


    # Use the script_annotations feature to seamlessly enable aliased kebab-case names
    # as your template interface, while using regular snake_case in the Python code
    @script()
    def function_kebab(
        a_but_kebab: Annotated[int, Parameter(name="a-but-kebab")] = 2,
        b_but_kebab: Annotated[str, Parameter(name="b-but-kebab")] = "foo",
        c_but_kebab: Annotated[float, Parameter(name="c-but-kebab")] = 42.0,
    ) -> Output:
        return Output(output=[Input(a=a_but_kebab, b=b_but_kebab, c=c_but_kebab)])


    @script()
    def function_kebab_object(annotated_input_value: Annotated[Input, Parameter(name="input-value")]) -> Output:
        return Output(output=[annotated_input_value])


    with Workflow(name="my-workflow", entrypoint="my-steps") as w:
        with Steps(name="my-steps") as s:
            my_function(arguments={"input": Input(a=2, b="bar", c=42)})
            str_function(arguments={"input": serialize(Input(a=2, b="bar", c=42))})
            another_function(arguments={"inputs": [Input(a=2, b="bar", c=42), Input(a=2, b="bar", c=42.0)]})
            function_kebab(arguments={"a-but-kebab": 3, "b-but-kebab": "bar"})
            function_kebab_object(arguments={"input-value": Input(a=3, b="bar", c="42")})
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      name: my-workflow
    spec:
      entrypoint: my-steps
      templates:
      - name: my-steps
        steps:
        - - arguments:
              parameters:
              - name: input
                value: '{"a": 2, "b": "bar", "c": 42}'
            name: my-function
            template: my-function
        - - arguments:
              parameters:
              - name: input
                value: '{"a": 2, "b": "bar", "c": 42}'
            name: str-function
            template: str-function
        - - arguments:
              parameters:
              - name: inputs
                value: '[{"a": 2, "b": "bar", "c": 42}, {"a": 2, "b": "bar", "c": 42.0}]'
            name: another-function
            template: another-function
        - - arguments:
              parameters:
              - name: a-but-kebab
                value: '3'
              - name: b-but-kebab
                value: bar
            name: function-kebab
            template: function-kebab
        - - arguments:
              parameters:
              - name: input-value
                value: '{"a": 3, "b": "bar", "c": "42"}'
            name: function-kebab-object
            template: function-kebab-object
      - inputs:
          parameters:
          - name: input
        name: my-function
        script:
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.scripts.callable_script_v1:my_function
          command:
          - python
          env:
          - name: hera__script_annotations
            value: ''
          - name: hera__pydantic_mode
            value: '1'
          image: my-image-with-python-source-code-and-dependencies
          source: '{{inputs.parameters}}'
      - inputs:
          parameters:
          - name: input
        name: str-function
        script:
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.scripts.callable_script_v1:str_function
          command:
          - python
          env:
          - name: hera__script_annotations
            value: ''
          - name: hera__pydantic_mode
            value: '1'
          image: my-image-with-python-source-code-and-dependencies
          source: '{{inputs.parameters}}'
      - inputs:
          parameters:
          - name: inputs
        name: another-function
        script:
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.scripts.callable_script_v1:another_function
          command:
          - python
          env:
          - name: hera__script_annotations
            value: ''
          - name: hera__pydantic_mode
            value: '1'
          image: my-image-with-python-source-code-and-dependencies
          source: '{{inputs.parameters}}'
      - inputs:
          parameters:
          - default: '2'
            name: a-but-kebab
          - default: foo
            name: b-but-kebab
          - default: '42.0'
            name: c-but-kebab
        name: function-kebab
        script:
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.scripts.callable_script_v1:function_kebab
          command:
          - python
          env:
          - name: hera__script_annotations
            value: ''
          - name: hera__pydantic_mode
            value: '1'
          image: my-image-with-python-source-code-and-dependencies
          source: '{{inputs.parameters}}'
      - inputs:
          parameters:
          - name: input-value
        name: function-kebab-object
        script:
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.scripts.callable_script_v1:function_kebab_object
          command:
          - python
          env:
          - name: hera__script_annotations
            value: ''
          - name: hera__pydantic_mode
            value: '1'
          image: my-image-with-python-source-code-and-dependencies
          source: '{{inputs.parameters}}'
    ```


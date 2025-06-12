# Typed Script Input Output



This example shows the various forms of IO available to Script Template functions.

Pydantic classes, as well as JSON types (and any combination of them), are usable as inputs and
outputs in script template functions, as the Hera Runner understands Pydantic classes, so can
serialise and deserialise them.

If you need the Pydantic V1 BaseModel when V2 is installed, use this import block:

```py
try:
    from pydantic.v1 import BaseModel
except (ImportError, ModuleNotFoundError):
    from pydantic import BaseModel
```


=== "Hera"

    ```python linenums="1"
    from typing import Annotated, List, Union

    from pydantic import BaseModel

    from hera.shared import global_config
    from hera.shared.serialization import serialize
    from hera.workflows import Parameter, Script, Steps, Workflow, script

    # Note, you must build an image to use the Hera Runner
    global_config.image = "my-image-with-python-source-code-and-dependencies"
    global_config.set_class_defaults(Script, constructor="runner")


    # Create a BaseModel sub-class to use a JSON input with any shape.
    # It will be validated by Pydantic at runtime.
    class MyInput(BaseModel):
        a: int
        b: str = "foo"
        c: Union[str, int, float]

        class Config:
            smart_union = True


    # Create a BaseModel sub-class to use a JSON output with any shape.
    # It will be validated by Pydantic at runtime.
    class MyOutput(BaseModel):
        output: List[MyInput]


    @script()
    def my_function(input: MyInput) -> MyOutput:
        return MyOutput(output=[input])


    # You can use lists (or dictionaries) of your custom type as input
    @script()
    def another_function(inputs: List[MyInput]) -> MyOutput:
        return MyOutput(output=inputs)


    # Raw json strings must be explicitly marked as a string type to ensure
    # the Hera Runner does not parse it for you.
    @script()
    def str_function(input: str) -> MyOutput:
        # Example function to ensure string type is not auto-parsed by Hera
        return MyOutput(output=[MyInput.parse_raw(input)])


    # Use Script Annotations to seamlessly aliase names for your template interface,
    # in particular, you can use "snake_case" code with a "kebab-case" interface:
    @script()
    def function_kebab(
        a_snake: Annotated[int, Parameter(name="a-but-kebab")] = 2,
        b_snake: Annotated[str, Parameter(name="b-but-kebab")] = "foo",
        c_snake: Annotated[float, Parameter(name="c-but-kebab")] = 42.0,
    ) -> MyOutput:
        return MyOutput(output=[MyInput(a=a_snake, b=b_snake, c=c_snake)])


    @script()
    def function_kebab_object(annotated_input_value: Annotated[MyInput, Parameter(name="input-value")]) -> MyOutput:
        return MyOutput(output=[annotated_input_value])


    with Workflow(name="my-workflow", entrypoint="my-steps") as w:
        with Steps(name="my-steps") as s:
            my_function(arguments={"input": MyInput(a=2, b="bar", c=42)})
            str_function(arguments={"input": serialize(MyInput(a=2, b="bar", c=42))})
            another_function(arguments={"inputs": [MyInput(a=2, b="bar", c=42), MyInput(a=2, b="bar", c=42.0)]})
            function_kebab(arguments={"a-but-kebab": 3, "b-but-kebab": "bar"})
            function_kebab_object(arguments={"input-value": MyInput(a=3, b="bar", c="42")})
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
        - - name: my-function
            template: my-function
            arguments:
              parameters:
              - name: input
                value: '{"a": 2, "b": "bar", "c": 42}'
        - - name: str-function
            template: str-function
            arguments:
              parameters:
              - name: input
                value: '{"a": 2, "b": "bar", "c": 42}'
        - - name: another-function
            template: another-function
            arguments:
              parameters:
              - name: inputs
                value: '[{"a": 2, "b": "bar", "c": 42}, {"a": 2, "b": "bar", "c": 42.0}]'
        - - name: function-kebab
            template: function-kebab
            arguments:
              parameters:
              - name: a-but-kebab
                value: '3'
              - name: b-but-kebab
                value: bar
        - - name: function-kebab-object
            template: function-kebab-object
            arguments:
              parameters:
              - name: input-value
                value: '{"a": 3, "b": "bar", "c": "42"}'
      - name: my-function
        inputs:
          parameters:
          - name: input
        script:
          image: my-image-with-python-source-code-and-dependencies
          source: '{{inputs.parameters}}'
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.hera_runner.typed_script_input_output:my_function
          command:
          - python
      - name: str-function
        inputs:
          parameters:
          - name: input
        script:
          image: my-image-with-python-source-code-and-dependencies
          source: '{{inputs.parameters}}'
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.hera_runner.typed_script_input_output:str_function
          command:
          - python
      - name: another-function
        inputs:
          parameters:
          - name: inputs
        script:
          image: my-image-with-python-source-code-and-dependencies
          source: '{{inputs.parameters}}'
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.hera_runner.typed_script_input_output:another_function
          command:
          - python
      - name: function-kebab
        inputs:
          parameters:
          - name: a-but-kebab
            default: '2'
          - name: b-but-kebab
            default: foo
          - name: c-but-kebab
            default: '42.0'
        script:
          image: my-image-with-python-source-code-and-dependencies
          source: '{{inputs.parameters}}'
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.hera_runner.typed_script_input_output:function_kebab
          command:
          - python
      - name: function-kebab-object
        inputs:
          parameters:
          - name: input-value
        script:
          image: my-image-with-python-source-code-and-dependencies
          source: '{{inputs.parameters}}'
          args:
          - -m
          - hera.workflows.runner
          - -e
          - examples.workflows.hera_runner.typed_script_input_output:function_kebab_object
          command:
          - python
    ```


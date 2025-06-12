"""This example shows how to use input and output for a DAG.

The example uses an "inner" dag which has a `my-dag-input` parameter, which can be referenced using `get_parameter`.
It also has the `my-dag-output` parameter, which "hoists" the task output to be a DAG output.
"""

from typing_extensions import Annotated

from hera.workflows import DAG, Parameter, Workflow, script


@script(constructor="runner")
def hello_with_output(name: str) -> Annotated[str, Parameter(name="output-message")]:
    return "Hello, {name}!".format(name=name)


with Workflow(
    generate_name="callable-dag-",
    entrypoint="calling-dag",
) as w:
    with DAG(
        name="my-dag-with-outputs",
        inputs=Parameter(name="my-dag-input"),
        outputs=Parameter(
            name="my-dag-output",
            value_from={"parameter": "{{tasks.hello.outputs.parameters.output-message}}"},
        ),
    ) as my_dag:
        # Here, get_parameter gets the *input* parameter of my_dag
        hello_with_output(name="hello", arguments={"name": f"hello {my_dag.get_parameter('my-dag-input')}"})

    with DAG(name="calling-dag") as d:
        t1 = my_dag(name="call-1", arguments={"my-dag-input": "call-1"})
        # Here, t1 is a Task from the called dag, so get_parameter is called on the Task to get the *output* parameter! 🚀
        t2 = my_dag(name="call-2", arguments={"my-dag-input": t1.get_parameter("my-dag-output")})
        t1 >> t2

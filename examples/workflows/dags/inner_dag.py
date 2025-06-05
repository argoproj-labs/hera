"""This example shows how to use a DAG within another DAG."""

from hera.workflows import DAG, Parameter, Workflow, script


@script()
def hello(name: str):
    print("Hello, {name}!".format(name=name))


with Workflow(
    generate_name="callable-dag-",
    entrypoint="calling-dag",
) as w:
    with DAG(name="my-dag", inputs=Parameter(name="my-dag-input")) as my_dag:
        hello(name="hello-1", arguments={"name": "hello-1-{{inputs.parameters.my-dag-input}}"})
        hello(name="hello-2", arguments={"name": "hello-2-{{inputs.parameters.my-dag-input}}"})

    with DAG(name="calling-dag") as d:
        t1 = my_dag(name="call-1", arguments={"my-dag-input": "call-1"})
        t2 = my_dag(name="call-2", arguments={"my-dag-input": "call-2"})
        t1 >> t2

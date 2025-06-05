"""This example shows how to use artifacts as inputs and outputs of DAGs."""

from hera.workflows import DAG, Artifact, Container, Workflow

with Workflow(
    generate_name="artifacts-in-dags-",
    entrypoint="runner-dag",
) as w:
    hello_world_to_file = Container(
        name="hello-world-to-file",
        image="busybox",
        command=["sh", "-c"],
        args=["sleep 1; echo hello world | tee /tmp/hello_world.txt"],
        outputs=[Artifact(name="hello-art", path="/tmp/hello_world.txt")],
    )
    print_message_from_file = Container(
        name="print-message-from-file",
        image="alpine:latest",
        command=["sh", "-c"],
        args=["cat /tmp/message"],
        inputs=[Artifact(name="message", path="/tmp/message")],
    )

    # First DAG generates an artifact from a task, and "lifts" it out as an output of the DAG template itself
    with DAG(
        name="generate-artifact-dag",
        outputs=[Artifact(name="hello-file", from_="{{tasks.hello-world-to-file.outputs.artifacts.hello-art}}")],
    ) as d1:
        hello_world_to_file()

    # Second DAG takes an artifact input, and the task references it using `get_artifact`
    with DAG(name="consume-artifact-dag", inputs=[Artifact(name="hello-file-input")]) as d2:
        print_message_from_file(
            arguments={"message": d2.get_artifact("hello-file-input")},
        )

    # Third DAG orchestrates the first two, by creating tasks by "calling" the objects
    with DAG(name="runner-dag"):
        generator_dag = d1()
        consumer_dag = d2(arguments={"hello-file-input": generator_dag.get_artifact("hello-file")})

        generator_dag >> consumer_dag

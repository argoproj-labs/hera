from hera.workflows import DAG, Container, S3Artifact, Task, Workflow

with Workflow(generate_name="key-only-artifacts-", entrypoint="main") as w:
    generate = Container(
        name="generate",
        image="argoproj/argosay:v2",
        args=["echo", "hello", "/mnt/file"],
        outputs=[
            S3Artifact(
                name="file",
                path="/mnt/file",
                key="my-file",
            ),
        ],
    )
    consume = Container(
        name="consume",
        image="argoproj/argosay:v2",
        args=["cat", "/tmp/file"],
        inputs=[
            S3Artifact(
                name="file",
                path="/tmp/file",
                key="my-file",
            )
        ],
    )

    with DAG(name="main"):
        Task(name="generate", template=generate) >> Task(name="consume", template=consume)

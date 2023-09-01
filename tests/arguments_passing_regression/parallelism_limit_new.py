from hera.workflows import Container, Steps, Workflow

with Workflow(
    generate_name="parallelism-limit-",
    entrypoint="parallelism-limit",
    parallelism=2,
) as w:
    sleep = Container(name="sleep", image="alpine:latest", command=["sh", "-c", "sleep 10"], directly_callable=True)

    with Steps(name="parallelism-limit") as steps:
        sleep().with_(
            with_items=["this", "workflow", "should", "take", "at", "least", 60, "seconds", "to", "complete"]
        )

from hera.workflows import Container, Steps, Workflow

with Workflow(
    generate_name="parallelism-template-limit-",
    entrypoint="parallelism-template-limit",
) as w:
    sleep = Container(
        name="sleep",
        image="alpine:latest",
        command=["sh", "-c", "sleep 10"],
    )
    with Steps(name="parallelism-template-limit", parallelism=2):
        sleep(
            with_items=[
                "this",
                "workflow",
                "should",
                "take",
                "at",
                "least",
                60,
                "seconds",
                "to",
                "complete",
            ]
        )

print(w.to_yaml())

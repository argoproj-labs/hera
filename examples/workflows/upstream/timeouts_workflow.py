from hera.workflows import Container, Steps, Workflow

with Workflow(generate_name="timeouts-workflow-", entrypoint="bunch-of-sleeps", active_deadline_seconds=30) as w:
    sleep = Container(
        name="sleep",
        image="debian:9.5-slim",
        command=["sleep", "1d"],
    )
    unschedule = Container(
        name="unschedulable",
        image="alpine:latest",
        node_selector={"beta.kubernetes.io/arch": "no-such-arch"},
    )
    with Steps(name="bunch-of-sleeps") as s:
        with s.parallel():
            sleep(name="sleep-one-day", with_items=[1, 2, 3])
            unschedule(with_items=[1, 2, 3])

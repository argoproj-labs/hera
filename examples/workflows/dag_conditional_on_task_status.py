from hera.workflows import DAG, Workflow, script


@script()
def fail_or_succeed():
    import random

    if random.randint(0, 1) == 0:
        raise ValueError


@script()
def when_succeeded():
    print("It was a success")


@script()
def when_failed():
    print("It was a failure")


with Workflow(generate_name="dag-conditional-on-task-status-", entrypoint="d") as w:
    with DAG(name="d") as s:
        t1 = fail_or_succeed()

        t1.on_failure(when_failed())
        t1.on_success(when_succeeded())

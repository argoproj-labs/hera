"""This example showcases conditional execution on success, failure, and error"""

from hera.workflows import DAG, Workflow, script


@script()
def random():
    import random

    p = random.random()
    if p <= 0.5:
        raise Exception("failure")


@script()
def success():
    print("succeeded!")


@script()
def failure():
    print("failed!")


with Workflow(generate_name="dag-conditional-on-task-status-", entrypoint="d") as w:
    with DAG(name="d"):
        r = random()

        r.on_success(success())
        r.on_failure(failure())

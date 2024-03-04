"""This example showcases conditional execution on success, failure, and error"""

from hera.workflows import DAG, Workflow, script


@script()
def random():
    import random

    p = random.random()
    if p <= 0.5:
        raise Exception("failure")
    print("success")


@script()
def success():
    print("success")


@script()
def failure():
    print("failure")


with Workflow(generate_name="conditional-", entrypoint="d") as w:
    with DAG(name="d"):
        r = random()
        s = success()
        f = failure()

        r.on_success(s)
        r.on_failure(f)

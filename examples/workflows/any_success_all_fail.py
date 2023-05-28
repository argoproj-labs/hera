from hera.workflows import DAG, Workflow, script


@script()
def foo(a):
    print(a)


@script()
def random_fail(a):
    import random

    random.seed(a)
    if random.random() < 0.5:
        raise Exception("Oh, no!")


@script()
def fail(a):
    raise Exception(a)


with Workflow(generate_name="any-success-all-fail-", entrypoint="d") as w:
    with DAG(name="d"):
        t1 = random_fail(name="t1", with_param=[1, 2, 3])
        t2 = fail(name="t2", with_param=[1, 2, 3])
        t3 = foo(name="t3", with_param=[1, 2, 3])

        t1.when_any_succeeded(t2)
        t2.when_all_failed(t3)

from hera.workflows import Task, Workflow


def foo(a):
    print(a)


def random_fail(a):
    import random

    random.seed(a)
    if random.random() < 0.5:
        raise Exception("Oh, no!")


def fail(a):
    raise Exception(a)


# assumes you used `hera.set_global_token` and `hera.set_global_host` so that the workflow can be submitted
with Workflow("any-success-all-fail") as w:
    t1 = Task("t1", random_fail, [1, 2, 3])
    t2 = Task("t2", fail, [1, 2, 3])
    t3 = Task("t3", foo, [1, 2, 3])

    t1.when_any_succeeded(t2)
    t2.when_all_failed(t3)

w.create()

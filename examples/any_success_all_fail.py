from hera import Task, Workflow, WorkflowService


def foo(a):
    print(a)


def random_fail(a):
    import random

    random.seed(a)
    if random.random() < 0.5:
        raise Exception('Oh, no!')


def fail(a):
    raise Exception(a)


with Workflow(
    'any-success-all-fail', service=WorkflowService(host='https://my-argo-server.com', token='my-auth-token')
) as w:
    t1 = Task('t1', random_fail, [{'a': 1}, {'a': 2}, {'a': 3}])
    t2 = Task('t2', fail, [{'a': 1}, {'a': 2}, {'a': 3}])
    t3 = Task('t3', foo, [{'a': 1}, {'a': 2}, {'a': 3}])

    t1.when_any_succeeded(t2)
    t2.when_all_failed(t3)

w.create()

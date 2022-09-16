from hera import Task, Workflow


def hello(s: str):
    print(f"Hello Hera, {s}")


def bye():
    print("Bye Hera")


# assumes you used `hera.set_global_token` and `hera.set_global_host` so that the workflow can be submitted
with Workflow("task-exit-handler") as w:
    t1 = Task("t1", hello, [{"s": "from Task1"}]).on_exit(Task("running", bye))
    t1 >> Task("t2", hello, [{"s": "from Task2"}])

w.create()

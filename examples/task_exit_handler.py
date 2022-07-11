from hera import Task, Workflow, WorkflowService


def bye():
    print("Bye Hera")


def hello(s: str):
    print(f"Hello Hera, {s}")


with Workflow("task-exit-handler", service=WorkflowService(host="my-argo-server.com", token="my-token")) as w:
    t1 = Task("t1", hello, [{"s": "from Task1"}]).on_exit(Task("running", bye))
    t1 >> Task("t2", hello, [{"s": "from Task2"}])

w.create()

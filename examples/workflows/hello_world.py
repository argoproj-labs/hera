from hera.workflows import Workflow, script


@script()
def hello(s: str):
    print("Hello, {s}!".format(s=s))


with Workflow(generate_name="task-exit-handler-", entrypoint="s") as w:
    hello(s="hello")

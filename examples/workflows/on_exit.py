from hera.workflows import DAG, Script, Workflow, script


@script()
def hello(s: str):
    print(f"Hello Hera, {s}")


def bye():
    print("Bye Hera")


with Workflow(generate_name="task-exit-handler-", entrypoint="d") as w:
    bye = Script(name="bye", source=bye)
    with DAG(name="d"):
        h1 = hello(name="s1", arguments={"s": "from Task1"})
        h1.on_exit = "bye"
        h2 = hello(name="s2", arguments={"s": "from Task2"})

        h1 >> h2

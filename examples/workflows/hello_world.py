from hera.workflows import Script, Workflow


def hello(s: str):
    print(f"Hello, {s}!")


with Workflow(generate_name="task-exit-handler-", entrypoint="s") as w:
    Script(name="s", source=hello, inputs={"s": "world"})

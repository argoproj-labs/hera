from hera.workflows import DAG, Script, Workflow, script


@script(use_func_params_in_call=True)
def hello(s: str):
    print("Hello Hera, {s}".format(s=s))


def bye():
    print("Bye Hera")


with Workflow(generate_name="task-exit-handler-", entrypoint="d") as w:
    bye_ = Script(name="bye", source=bye)
    with DAG(name="d"):
        h1 = hello("from Task1").with_(name="s1")
        h1.on_exit = bye_
        h2 = hello("from Task2").with_(name="s2")

        h1 >> h2

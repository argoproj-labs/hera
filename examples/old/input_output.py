from hera import Parameter, Task, ValueFrom, Workflow


def produce():
    with open("/test.txt", "w") as f:
        f.write("Hello, world!")


def consume(msg: str):
    print(f"Message was: {msg}")


# assumes you used `hera.set_global_token` and `hera.set_global_host` so that the workflow can be submitted
with Workflow("io") as w:
    t1 = Task("p", produce, outputs=[Parameter("msg", value_from=ValueFrom(path="/test.txt"))])
    t2 = Task("c", consume, inputs=[t1.get_parameter("msg")])
    t1 >> t2

w.create()

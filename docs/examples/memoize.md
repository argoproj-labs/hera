# Memoize

```python
from hera import Memoize, Parameter, Task, ValueFrom, Workflow


def generate():
    with open("/out", "w") as f:
        f.write("42")


def consume(value):
    print(f"Received value: {value}")


# assumes you used `hera.set_global_token` and `hera.set_global_host` so that the workflow can be submitted
with Workflow("memoize") as w:
    g = Task("g", generate, outputs=[Parameter("out", value_from=ValueFrom(path="/out"))])
    c = Task("c", consume, inputs=[g.get_parameter("out")], memoize=Memoize("value", "memoize", "c"))
    g >> c

w.create()

```
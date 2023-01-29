# Coin Flip

This example showcases the classic conditional workflow coin-flip.

```python
from hera import Task, Workflow


def random_code():
    import random

    res = "heads" if random.randint(0, 1) == 0 else "tails"
    print(res)


def heads():
    print("it was heads")


def tails():
    print("it was tails")


# assumes you used `hera.set_global_token` and `hera.set_global_host` so that the workflow can be submitted
with Workflow(generate_name="coin-flip-") as w:
    r = Task("r", random_code)
    h = Task("h", heads)
    t = Task("t", tails)

    h.on_other_result(r, "heads")
    t.on_other_result(r, "tails")

w.create()
```

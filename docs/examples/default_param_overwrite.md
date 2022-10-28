# Default param overwrite

This example showcases how a Python source can be scheduled with default parameters as kwargs but overwritten
conditionally.

```python
from hera import Task, Workflow


def generator():
    print("Another message for the world!")


def consumer(message: str = "Hello, world!"):
    print(message)


with Workflow("default-param-overwrite") as w:
    generator_ = Task("generator", generator)

    # will print `Hello, world!`
    consumer_default = Task("consumer-default", consumer)
    # will print `Another message for the world!`
    consumer_param = Task("consumer-parameter", consumer, inputs=[generator_.get_result_as("message")])

    generator_ >> [consumer_default, consumer_param]
w.create()
```
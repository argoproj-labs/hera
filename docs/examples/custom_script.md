# Custom Script

This example showcases how to run a custom script rather than a python function in Hera

```python
from hera import Parameter, Task, Workflow

# If the source function of a task has a return type of "str" in its annotation,
# the task will resolve the function before creation.


def script(message: str) -> str:  # <---- '-> str:' here is important!
    return f"""
            echo ----------
            echo {message}
            echo ----------
            """


# Alternatively, the script can also be a pure string
# script = """
#          echo ----------
#          echo {{inputs.parameters.message}}
#          echo ----------
#          """

with Workflow(generate_name="custom-script-") as wf:
    Task("message", script, command=["sh"], inputs=[Parameter(name="message", value="Magic!")])

wf.create()
```

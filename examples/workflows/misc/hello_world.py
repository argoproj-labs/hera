"""This example shows a minimal "Hello World" example."""

from hera.workflows import Workflow, script


@script()
def hello(s: str):
    print("Hello, {s}!".format(s=s))


with Workflow(
    generate_name="hello-world-",
    entrypoint="hello",
    arguments={"s": "world"},
) as w:
    hello()

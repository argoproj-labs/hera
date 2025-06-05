"""This example shows script function default parameters.

Script functions parameters mirror Python's behaviour:

* use the caller argument value if provided
* otherwise use the default if provided
* otherwise error as no value provided (and a value is always required in Argo Workflows)
"""

from hera.workflows import DAG, Workflow, script


@script()
def generator():
    print("Another message for the world!")


@script()
def consumer(message: str = "Hello, world!", foo: int = 42):
    print(message)
    print(foo)


with Workflow(generate_name="default-param-overwrite-", entrypoint="d") as w:
    with DAG(name="d"):
        g = generator()
        c_default = consumer(name="consume-default")
        c_arg = consumer(name="consume-argument", arguments={"message": g.result})
        g >> [c_default, c_arg]

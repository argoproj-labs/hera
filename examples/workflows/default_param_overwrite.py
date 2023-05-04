"""
This example showcases how a Python source can be scheduled with default parameters as kwargs but overwritten
conditionally.
"""

from hera.workflows import DAG, Workflow, script


@script()
def generator():
    print("Another message for the world!")


@script()
def consumer(message: str = "Hello, world!"):
    print(message)


with Workflow(generate_name="default-param-overwrite-", entrypoint="d") as w:
    with DAG(name="d"):
        g = generator()
        c_default = consumer(name="consumer-default")
        c_param = consumer(name="consumer-param", arguments={"message": g.get_result_as("message")})
        g >> [c_default, c_param]

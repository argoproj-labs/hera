"""
This example showcases how a Python source can be scheduled with default parameters as kwargs but overwritten
conditionally.
"""

from hera.workflows import DAG, Workflow, script


@script()
def generator():
    print("Another message for the world!")


@script(use_func_params_in_call=True)
def consumer(message: str = "Hello, world!"):
    print(message)


with Workflow(generate_name="default-param-overwrite-", entrypoint="d") as w:
    with DAG(name="d"):
        g = generator()
        c_default = consumer().with_(name="consumer-default")
        c_param = consumer(g.get_result_as("message")).with_(name="consumer-param")
        g >> [c_default, c_param]

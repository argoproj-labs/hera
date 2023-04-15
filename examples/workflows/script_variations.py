from hera.workflows import Workflow, script


@script()
def hello_world():  # pragma: no cover
    print("Hello World!")


@script()
def multiline_function(
    test: str,
    another_test: str,
) -> str:  # pragma: no cover
    print("Hello World!")


with Workflow(generate_name="fv-test-", entrypoint="d") as w:
    hello_world()
    multiline_function()

from hera.workflows import Workflow, script


@script(constructor="runner")
def hello():
    pass


with Workflow(
    generate_name="runner-workflow-",
    entrypoint="hello",
) as w:
    hello()

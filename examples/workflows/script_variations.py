from hera.workflows import DAG, Workflow, script


@script()
def hello_world():  # pragma: no cover
    print("Hello World!")


@script()
def multiline_function(test: str, another_test: str):  # pragma: no cover
    print(test)
    print(another_test)


with Workflow(generate_name="fv-test-", entrypoint="d") as w:
    with DAG(name="d"):
        hello_world()
        multiline_function(arguments={"test": "test string", "another_test": "another test string"})

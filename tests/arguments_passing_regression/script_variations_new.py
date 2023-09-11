from hera.workflows import DAG, Workflow, script


@script()
def hello_world():  # pragma: no cover
    print("Hello World!")


@script(use_func_params_in_call=True)
def multiline_function(test: str, another_test: str):  # pragma: no cover
    print(test)
    print(another_test)


with Workflow(generate_name="fv-test-", entrypoint="d") as w:
    with DAG(name="d"):
        hello_world()
        multiline_function("test string", "another test string")

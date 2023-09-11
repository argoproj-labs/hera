from hera.workflows import DAG, Parameter, Workflow, script


@script(use_func_params_in_call=True)
def hello(name: str):
    print("Hello, {name}!".format(name=name))


with Workflow(
    generate_name="callable-dag-",
    entrypoint="calling-dag",
) as w:
    with DAG(name="my-dag", inputs=Parameter(name="my-dag-input"), use_func_params_in_call=True) as my_dag:
        hello("hello-1-{{inputs.parameters.my-dag-input}}").with_(name="hello-1")
        hello("hello-2-{{inputs.parameters.my-dag-input}}").with_(name="hello-2")

    with DAG(name="calling-dag") as d:
        t1 = my_dag("call-1").with_(name="call-1")
        t2 = my_dag("call-2").with_(name="call-2")
        t1 >> t2

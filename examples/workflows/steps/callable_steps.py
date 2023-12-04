from hera.workflows import Parameter, Steps, Workflow, script


@script()
def hello(name: str):
    print("Hello, {name}!".format(name=name))


with Workflow(
    generate_name="callable-steps-",
    entrypoint="calling-steps",
) as w:
    with Steps(name="my-steps", inputs=Parameter(name="my-step-input")) as my_steps:
        hello(name="hello-1", arguments={"name": "hello-1-{{inputs.parameters.my-step-input}}"})
        hello(name="hello-2", arguments={"name": "hello-2-{{inputs.parameters.my-step-input}}"})

    with Steps(name="calling-steps") as s:
        my_steps(name="call-1", arguments={"my-step-input": "call-1"})
        my_steps(name="call-2", arguments={"my-step-input": "call-2"})

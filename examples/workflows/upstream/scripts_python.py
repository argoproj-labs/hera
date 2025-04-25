from hera.workflows import Container, Parameter, Script, Step, Steps, Workflow

with Workflow(
    generate_name="scripts-python-",
    entrypoint="python-script-example",
) as w:
    gen_random_int = Script(
        name="gen-random-int",
        image="python:alpine3.6",
        command=["python"],
        source="""
import random
i = random.randint(1, 100)
print(i)""",
    )

    print_message = Container(
        name="print-message",
        image="alpine:latest",
        command=["sh", "-c"],
        args=["echo result was: {{inputs.parameters.message}}"],
        inputs=[Parameter(name="message")],
    )

    with Steps(name="python-script-example") as s:
        Step(
            name="generate",
            template="gen-random-int",
        )
        Step(
            name="print",
            template="print-message",
            arguments={"message": "{{steps.generate.outputs.result}}"},
        )

from hera.workflows import Step, Steps, WorkflowTemplate, script


@script(constructor="inline")
def random_roll():
    import random

    return random.randint(0, 2)


with WorkflowTemplate(name="my-workflow", entrypoint="steps") as w:
    with Steps(name="sub-steps") as sub_steps:
        random_number = random_roll()
        Step(
            name="recurse",
            arguments={"input-num": random_number.result},
            template=sub_steps,
            when=f"{random_number.result} != 0",
        )

    with Steps(name="steps"):
        sub_steps()

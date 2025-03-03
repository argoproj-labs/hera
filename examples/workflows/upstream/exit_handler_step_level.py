from hera.workflows import Container, Parameter, Steps, Workflow
from hera.workflows.models import LifecycleHook

with Workflow(
    generate_name="exit-handler-step-level-",
    entrypoint="main",
) as w:
    exit_ = Container(
        name="exit",
        image="busybox",
        command=["echo"],
        args=["step cleanup"],
    )
    print_message = Container(
        name="print-message",
        inputs=[Parameter(name="message")],
        image="busybox",
        command=["echo"],
        args=["{{inputs.parameters.message}}"],
    )
    with Steps(name="main") as s:
        print_message(
            name="hello1",
            arguments=[Parameter(name="message", value="hello1")],
            hooks={"exit": LifecycleHook(template=exit_.name)},
        )
        with s.parallel():
            print_message(
                name="hello2a",
                arguments=[Parameter(name="message", value="hello2a")],
                hooks={"exit": LifecycleHook(template=exit_.name)},
            )
            print_message(
                name="hello2b",
                arguments=[Parameter(name="message", value="hello2b")],
                hooks={"exit": LifecycleHook(template=exit_.name)},
            )

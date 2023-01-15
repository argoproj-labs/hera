"""This example showcases how to use a `suspend` template with Hera"""

from hera import SuspendTemplate, Task, Workflow

# assumes you have set a global token and host
with Workflow(generate_name="suspend-template-") as w:
    (
        Task("build", image="docker/whalesay", command=["cowsay"], args=["hello world"])
        >> Task("approve", suspend=SuspendTemplate())
        >> Task("delay", suspend=SuspendTemplate(duration="20"))
        >> Task("release", image="docker/whalesay", command=["cowsay"], args=["hello world"])
    )

w.create()

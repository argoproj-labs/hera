"""This example showcases how to use a `suspend` template with Hera"""

from hera.workflows import Suspend, Task, Workflow

# assumes you have set a global token and host
with Workflow("suspend-template-", generate_name=True) as w:
    (
        Task("build", image="docker/whalesay", command=["cowsay"], args=["hello world"])
        >> Task("approve", suspend=Suspend())
        >> Task("delay", suspend=Suspend(duration="20"))
        >> Task("release", image="docker/whalesay", command=["cowsay"], args=["hello world"])
    )

w.create()

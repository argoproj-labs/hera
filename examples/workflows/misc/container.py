"""This example showcases how to run a container, rather than a Python, function, as the payload of a task in Hera"""

from hera.workflows import Container, Workflow

with Workflow(generate_name="container-", entrypoint="cowsay") as w:
    Container(name="cowsay", image="argoproj/argosay:v2", command=["cowsay", "foo"])

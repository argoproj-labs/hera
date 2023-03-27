from hera.workflows import Workflow, Container

with Workflow(generate_name="hello-world-", image_pull_secrets="docker-registry-secret", entrypoint="whalesay") as w:
    Container(name="whalesay", image="docker/whalesay:latest", command=["cowsay"], args=["hello world"])
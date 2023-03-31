from hera.shared import global_config
from hera.workflows import Container, Workflow, script

global_config.api_version = "argoproj.io/v0beta9000"
global_config.namespace = "argo-namespace"
global_config.service_account_name = "argo-account"
global_config.image = "image-say"


@script()
def say():
    print("hello")


with Workflow(generate_name="global-config-", entrypoint="whalesay") as w:
    whalesay = Container(image="docker/whalesay:latest", command=["cowsay"])
    say()

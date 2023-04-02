from hera.shared import global_config
from hera.workflows import Container, Workflow, script

global_config.api_version = "argoproj.io/v0beta9000"
global_config.namespace = "argo-namespace"
global_config.service_account_name = "argo-account"
global_config.image = "image-say"
global_config.script_command = ["python3"]
global_config.set_class_defaults(Container, active_deadline_seconds=100, command=["cowsay"])


@script()
def say():
    print("hello")


with Workflow(generate_name="global-config-", entrypoint="whalesay") as w:
    whalesay = Container(image="docker/whalesay:latest")
    say()

from hera.workflows import Container, Workflow
from hera.workflows.models import RetryStrategy

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    generate_name="retry-to-completion-",
    entrypoint="retry-to-completion",
) as w:
    Container(
        name="retry-to-completion",
        retry_strategy=RetryStrategy(),
        args=["import random; import sys; exit_code = random.choice(range(0, 5)); sys.exit(exit_code)"],
        command=["python", "-c"],
        image="python",
    )

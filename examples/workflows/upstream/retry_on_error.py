from hera.workflows import Container, Workflow
from hera.workflows.models import IntOrString, RetryStrategy

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    generate_name="retry-on-error-",
    entrypoint="error-container",
) as w:
    Container(
        name="error-container",
        retry_strategy=RetryStrategy(
            limit=IntOrString(
                root="2",
            ),
            retry_policy="Always",
        ),
        args=["import random; import sys; exit_code = random.choice(range(0, 5)); sys.exit(exit_code)"],
        command=["python", "-c"],
        image="python",
    )

from hera.workflows import Container, Step, Steps, Workflow
from hera.workflows.models import PodGC

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    generate_name="pod-gc-strategy-",
    entrypoint="pod-gc-strategy",
    pod_gc=PodGC(
        delete_delay_duration="30s",
        strategy="OnPodSuccess",
    ),
) as w:
    with Steps(
        name="pod-gc-strategy",
    ) as invocator:
        with invocator.parallel():
            Step(
                name="fail",
                template="fail",
            )
            Step(
                name="succeed",
                template="succeed",
            )
    Container(
        name="fail",
        args=["exit 1"],
        command=["sh", "-c"],
        image="alpine:3.7",
    )
    Container(
        name="succeed",
        args=["exit 0"],
        command=["sh", "-c"],
        image="alpine:3.7",
    )

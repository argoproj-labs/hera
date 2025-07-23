from hera.workflows import Container, Workflow
from hera.workflows.models import PodDNSConfig, PodDNSConfigOption, Quantity, ResourceRequirements

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    generate_name="test-dns-config-",
    dns_config=PodDNSConfig(
        nameservers=["1.2.3.4"],
        options=[
            PodDNSConfigOption(
                name="ndots",
                value="2",
            )
        ],
    ),
    entrypoint="hello-world",
) as w:
    Container(
        name="hello-world",
        args=["hello world"],
        command=["echo"],
        image="busybox",
        resources=ResourceRequirements(
            limits={
                "memory": Quantity(
                    __root__="32Mi",
                ),
                "cpu": Quantity(
                    __root__="100m",
                ),
            },
        ),
    )

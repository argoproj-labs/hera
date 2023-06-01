from hera.workflows import (
    Container,
    Workflow,
    models as m,
)

with Workflow(
    generate_name="default-pdb-support-",
    entrypoint="pdbcreate",
    service_account_name="default",
    pod_disruption_budget=m.PodDisruptionBudgetSpec(min_available=9999),
) as w:
    Container(
        name="pdbcreate",
        image="alpine:latest",
        command=["sh", "-c"],
        args=["sleep 10"],
    )

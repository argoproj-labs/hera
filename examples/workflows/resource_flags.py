from hera.workflows.models import ContinueOn
from hera.workflows.resource import Resource
from hera.workflows.steps import Step, Steps
from hera.workflows.workflow import Workflow

with Workflow(
    generate_name="resource-validate-",
    entrypoint="resource-validate-example",
) as w:
    create_route = Resource(
        name="create-route",
        action="create",
        manifest="apiVersion: route.openshift.io/v1\nkind: Route\nmetadata:\n  name: host-route\n"
        "spec:\n  to:\n    kind: Service\n    name: service-name\n",
    )

    create_route_without_validation = Resource(
        name="create-route-without-validation",
        action="create",
        flags=[
            "--validate=false",
        ],
        manifest="apiVersion: route.openshift.io/v1\nkind: Route\nmetadata:\n  name: host-route\n"
        "spec:\n  to:\n    kind: Service\n    name: service-name\n",
    )

    with Steps(name="resource-validate-example") as s:
        Step(name="submit-resource", template=create_route.name, continue_on=ContinueOn(failed=True))
        Step(
            name="submit-resource-without-validation",
            template=create_route_without_validation.name,
            when="{{steps.submit-resource.status}} == Failed",
        )

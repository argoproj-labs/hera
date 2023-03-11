from hera.workflows.models import ContinueOn
from hera.workflows.v5.resource import Resource
from hera.workflows.v5.steps import Step, Steps
from hera.workflows.v5.workflow import Workflow

create_route = Resource(
    name="create-route",
    action="create",
    manifest="""apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: host-route
spec:
  to:
    kind: Service
    name: service-name
""",
)
create_route_without_validation = Resource(
    name="create-route-without-validation",
    action="create",
    flags=[
        "--validate=false",
    ],
    manifest="""apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: host-route
spec:
  to:
    kind: Service
    name: service-name
""",
)

with Workflow(
    generate_name="resource-validate-",
    templates=[create_route, create_route_without_validation],
    entrypoint="resource-validate-example",
) as w:
    with Steps(name="resource-validate-example") as s:
        Step(name="submit-resource", template=create_route.name, continue_on=ContinueOn(failed=True))
        Step(
            name="submit-resource-without-validation",
            template=create_route_without_validation.name,
            when="{{steps.submit-resource.status}} == Failed",
        )

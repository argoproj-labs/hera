from hera.shared import global_config
from hera.workflows import DAG, RunnerScriptConstructor, Script, Workflow, WorkflowsService, script

try:
    from pydantic.v1 import BaseModel
except ImportError:
    from pydantic import BaseModel

global_config.set_class_defaults(Script, constructor=RunnerScriptConstructor())


class Rectangle(BaseModel):
    length: float
    width: float

    def area(self) -> float:
        return self.length * self.width


@script(constructor="runner", image="my-built-python-image")
def calculate_area_of_rectangle(rectangle: Rectangle) -> float:
    return rectangle.area()


with Workflow(
    generate_name="dag-",
    entrypoint="dag",
    namespace="argo",
    workflows_service=WorkflowsService(host="https://localhost:2746"),
) as w:
    with DAG(name="dag"):
        A = calculate_area_of_rectangle(
            name="rectangle-1", arguments={"rectangle": Rectangle(length=1.2, width=3.4).json()}
        )
        B = calculate_area_of_rectangle(
            name="rectangle-2", arguments={"rectangle": Rectangle(length=4.3, width=2.1).json()}
        )
        A >> B


def test_calculate_area_of_rectangle():
    r = Rectangle(length=2.0, width=3.0)
    assert calculate_area_of_rectangle(r) == 6.0


def test_create_workflow():
    model_workflow = w.create(wait=True)
    assert model_workflow.status and model_workflow.status.phase == "Succeeded"

    echo_node = next(
        filter(
            lambda n: n.display_name == "echo",
            model_workflow.status.nodes.values(),
        )
    )
    assert echo_node.outputs.parameters[0].value == "my value"

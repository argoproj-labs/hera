from typing_extensions import Annotated

from hera.shared import global_config
from hera.workflows import Artifact, Input, Output, Parameter, Workflow

global_config.experimental_features["script_annotations"] = True
global_config.experimental_features["script_pydantic_io"] = True
global_config.experimental_features["decorator_syntax"] = True


w = Workflow(generate_name="my-workflow-")


class WorkerInput(Input):
    basic_input_parameter: str
    annotated_parameter: Annotated[str, Parameter(name="my-input-param")]
    an_artifact: Annotated[str, Artifact(name="my-input-artifact")]


class WorkerOutput(Output):
    basic_output_parameter: str
    annotated_parameter: Annotated[str, Parameter(name="my-output-param")]
    an_artifact: Annotated[str, Artifact(name="my-output-artifact")]


@w.set_entrypoint
@w.dag()
def dummy_worker(_: WorkerInput) -> WorkerOutput:
    pass

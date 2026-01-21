from typing import Annotated

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


@w.script()
def dummy_task(_: WorkerInput) -> WorkerOutput:
    pass


@w.set_entrypoint
@w.dag()
def dummy_dag(dag_input: WorkerInput) -> WorkerOutput:
    a_task = dummy_task(
        WorkerInput(
            basic_input_parameter=dag_input.basic_input_parameter,
            annotated_parameter=dag_input.annotated_parameter,
            an_artifact=dag_input.an_artifact,
        )
    )

    return WorkerOutput(
        basic_output_parameter=a_task.basic_output_parameter,
        annotated_parameter=a_task.annotated_parameter,
        an_artifact=a_task.an_artifact,
    )

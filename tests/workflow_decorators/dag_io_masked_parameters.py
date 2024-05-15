from hera.shared import global_config
from hera.workflows import Input, Output, Workflow

global_config.experimental_features["script_annotations"] = True
global_config.experimental_features["script_pydantic_io"] = True
global_config.experimental_features["decorator_syntax"] = True


w = Workflow(generate_name="my-workflow-")


class WorkerInput(Input):
    name: str  # Masking task attribute
    hooks: bool  # Masking task attribute
    target: str  # Some DAG attribute (not being masked)


class WorkerOutput(Output):
    name: str  # Masking task attribute
    hooks: bool  # Masking task attribute
    target: str  # Some DAG attribute (not being masked)


@w.script()
def dummy_task(_: WorkerInput) -> WorkerOutput:
    pass


@w.set_entrypoint
@w.dag()
def dummy_dag(dag_input: WorkerInput) -> WorkerOutput:
    task_a = dummy_task(
        WorkerInput(
            name=dag_input.name,
            hooks=dag_input.hooks,
            target=dag_input.target,
        )
    )
    task_b = dummy_task(
        WorkerInput(
            name=task_a.name,
            hooks=task_a.hooks,
            target=dag_input.target,
        )
    )

    return WorkerOutput(
        name=task_a.name,
        hooks=task_b.hooks,
        target=dag_input.target,
    )

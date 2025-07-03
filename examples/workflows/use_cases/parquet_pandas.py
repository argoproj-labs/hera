"""This example shows how to use the custom serialisation features for third party libraries like Pandas. It also shows
how we can easily use big file formats like parquet through Hera Artifact annotations.

!!! note
    This example requires `pandas`, `pyarrow` and `hera` itself to run. You will need to provide an image containing
    these dependencies.
"""

import io
from pathlib import Path
from typing import Annotated

from pandas import DataFrame, read_parquet

from hera.workflows import (
    DAG,
    Artifact,
    NoneArchiveStrategy,
    Task,
    Workflow,
    script,
)


@script(constructor="runner")
def create_dataframe() -> Annotated[
    DataFrame,
    Artifact(
        name="dataset",
        dumpb=lambda df: df.to_parquet(),
        archive=NoneArchiveStrategy(),
    ),
]:
    # Here, we create some dummy data, and return it as a DataFrame.
    # The `dumpb` function from the `Artifact` annotation handles
    # the conversion to parquet format!
    data = {
        "age": [23, 19, 43, 65, 72],
        "height": [1.63, 1.82, 1.77, 1.59, 1.61],
    }
    return DataFrame(data)


@script(constructor="runner")
def loadb_dataframe(
    dataframe: Annotated[
        DataFrame,
        Artifact(name="dataset", loadb=lambda bytes_: read_parquet(io.BytesIO(bytes_))),
    ],
):
    # Using a `loadb` function here is possible but not very clear
    # as we have to create a buffered reader for `read_parquet`
    print(dataframe)


@script(constructor="runner")
def load_dataframe_from_path(
    dataframe_path: Annotated[
        Path,
        Artifact(name="dataset"),
    ],
):
    # Instead, we can read the parquet file from a path, which is easier to understand. Hera
    # automatically loads the `Path` of an Artifact to your function argument, so you can
    # read the contents of the Artifact file however you want!
    dataframe = read_parquet(dataframe_path)
    print(dataframe)


with Workflow(generate_name="pandas-example-", entrypoint="d", service_account_name="argo") as w:
    with DAG(name="d"):
        create_task: Task = create_dataframe()
        consume_task_1 = loadb_dataframe(
            arguments={
                "dataset": create_task.get_artifact("dataset"),
            },
        )
        consume_task_2 = load_dataframe_from_path(
            arguments={
                "dataset": create_task.get_artifact("dataset"),
            },
        )

        create_task >> [consume_task_1, consume_task_2]

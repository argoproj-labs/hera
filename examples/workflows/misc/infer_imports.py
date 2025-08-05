# SOME_IMPORTED_GLOBAL = "TO BE SHADOWED BY IMPORT"  # needs to maintain ordering to be before imports

import pandas as pd

# from tests.helper import ARTIFACT_PATH as SOME_IMPORTED_GLOBAL
from hera.workflows import InlineScriptConstructor, Workflow, script

# GLOBAL_PARAM = "test"
# MY_ADAPTED_PARAM = SOME_IMPORTED_GLOBAL + "/longer/path"


@script(
    image="my-image-with-pandas",
    constructor=InlineScriptConstructor(infer_imports=True),
)
def hello_inferred(s: str):
    df = pd.DataFrame({s: 1, "b": 2})
    print(df)


@script(
    image="python:3.12",
    constructor=InlineScriptConstructor(packages_to_install=["pandas"]),
)
def hello_install_at_runtime(s: str):
    import pandas as pd

    df = pd.DataFrame({s: 1, "b": 2})
    print(df)


with Workflow(
    generate_name="hello-world-",
    entrypoint="hello-inferred",
    arguments={"s": "world"},
) as w:
    hello_inferred()
    hello_install_at_runtime()

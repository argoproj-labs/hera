import random

from hera.shared import global_config
from hera.workflows import DAG, Script, Workflow, script

# Note, setting constructor to runner is only possible if the source code is available
# along with dependencies include hera in the image.
# Callable is a robust mode that allows you to run any python function
# and is compatible with pydantic. It automatically parses the input
# and serializes the output.
global_config.image = "my-image-with-python-source-code-and-dependencies"
global_config.set_class_defaults(Script, constructor="runner")
# Runner script constructor is still and experimental feature and we need to explicitly opt in to it
# Note that experimental features are subject to breaking changes in future releases of the same major version
global_config.experimental_features["script_runner"] = True


@script()
def flip():
    return "heads" if random.randint(0, 1) == 0 else "tails"


@script()
def heads():
    return "it was heads"


@script()
def tails():
    return "it was tails"


with Workflow(generate_name="coinflip-", entrypoint="d") as w:
    with DAG(name="d") as s:
        f = flip()
        heads().on_other_result(f, "heads")
        tails().on_other_result(f, "tails")

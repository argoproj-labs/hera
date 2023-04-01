import random

from examples.workflows import global_config
from hera.workflows import DAG, Workflow, script

# Note, callable mode is only possible if the source code is available
# along with dependencies include hera in the image.
# Callable is a robust mode that allows you to run any python function
# and is compatible with pydantic. It automatically parses the input
# and serializes the output.
global_config.image = "my-image-with-python-source-code-and-dependencies"


@script(callable=True)
def flip():
    return "heads" if random.randint(0, 1) == 0 else "tails"


@script(callable=True)
def heads():
    return "it was heads"


@script(callable=True)
def tails():
    return "it was tails"


with Workflow(generate_name="coinflip-", entrypoint="d") as w:
    with DAG(name="d") as s:
        f = flip()
        heads().on_other_result(f, "heads")
        tails().on_other_result(f, "tails")

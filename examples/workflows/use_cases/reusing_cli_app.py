"""This example shows how a CLI application built with [Cappa](https://github.com/DanCardin/cappa) can also be used as a `script` function.

!!! Warning
    Using the `script` decorator is not possible with other CLI libraries like [`click`](https://click.palletsprojects.com/en/stable/), and will require use of the `Script` class and setting `source=function_name`.
    [See this issue discussion](https://github.com/argoproj-labs/hera/issues/1530#issuecomment-3616082722) for more details.
"""

import cappa

from hera.workflows import Workflow, script


@script()
def hello(count: int, name: str):
    """Simple program that greets NAME for a total of COUNT times."""
    for _ in range(count):
        print(f"Hello {name}!")


with Workflow(
    generate_name="cli-example-",
    entrypoint="hello",
    arguments={"count": 3, "name": "Hera"},
) as w:
    hello()


if __name__ == "__main__":
    cappa.invoke(hello)

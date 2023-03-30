from hera.workflows import Env, Workflow, script


@script(image="python:3.7", add_cwd_to_sys_path=False, env=[Env(name="PYTHONUNBUFFERED", value="1")])
def whalesay():
    import time  # noqa: I001
    import random

    messages = [
        "No Color",
        "\x1b[30m%s\x1b[0m" % "FG Black",
        "\x1b[32m%s\x1b[0m" % "FG Green",
        "\x1b[34m%s\x1b[0m" % "FG Blue",
        "\x1b[36m%s\x1b[0m" % "FG Cyan",
        "\x1b[41m%s\x1b[0m" % "BG Red",
        "\x1b[43m%s\x1b[0m" % "BG Yellow",
        "\x1b[45m%s\x1b[0m" % "BG Magenta",
    ]
    for i in range(1, 100):
        print(random.choice(messages))
        time.sleep(1)


with Workflow(generate_name="colored-logs-", entrypoint="whalesay") as w:
    whalesay(name="whalesay")

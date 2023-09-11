"""
This example showcases how clients can use Hera to dynamically generate tasks that process outputs from one task in
parallel. This is useful for batch jobs and instances where clients do not know ahead of time how many tasks/entities
they may need to process. In addition to the fanout, this example showcases how one can set up extra parameters for
the job to dictate what the fanout should execute over.
"""
from hera.workflows import DAG, Workflow, script


@script()
def generate():
    import json
    import sys

    # this can be anything! e.g fetch from some API, then in parallel process all entities; chunk database records
    # and process them in parallel, etc.
    json.dump([i for i in range(10)], sys.stdout)


@script(use_func_params_in_call=True)
def consume(value: int, extra_param1: str, extra_param2: int = 42):
    print(
        "Received value={value}, extra_param1={extra_param1}, extra_param2={extra_param2}!".format(
            value=value,
            extra_param1=extra_param1,
            extra_param2=extra_param2,
        )
    )


# assumes you used `hera.set_global_token` and `hera.set_global_host` so that the workflow can be submitted
with Workflow(generate_name="dynamic-fanout-", entrypoint="d") as w:
    with DAG(name="d"):
        g = generate()
        # the following fanout will occur over the items in the list that is returned from the generate script
        # the `extra_param1` will take the `hello world` value while `extra_param2` will hold the default value of 42
        c1 = consume("{{item}}", "hello world").with_(name="c1", with_param=g.result)

        # the following fanout will occur over the items in the list that is returned from the generate script
        # the `extra_param1` will take the `hello world` value while `extra_param2` will hold the default value of 123
        c2 = consume("{{item}}", "hello world", "123").with_(
            name="c2",
            with_param=g.result,
        )
        g >> c1
        g >> c2

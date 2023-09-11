from hera.workflows import Container, Parameter, Steps, Workflow, script


@script(image="python:alpine3.6", command=["python"], add_cwd_to_sys_path=False, use_func_params_in_call=True)
def gen_number_list():
    import json
    import sys

    json.dump([i for i in range(20, 31)], sys.stdout)


with Workflow(
    generate_name="loops-param-result-",
    entrypoint="loop-param-result-example",
) as w:
    sleep_n_sec = Container(
        name="sleep-n-sec",
        inputs=Parameter(name="seconds"),
        image="alpine:latest",
        command=["sh", "-c"],
        args=[
            "echo sleeping for {{inputs.parameters.seconds}} seconds; sleep {{inputs.parameters.seconds}}; echo done"
        ],
        use_func_params_in_call=True,
    )

    with Steps(name="loop-param-result-example"):
        g = gen_number_list().with_(name="generate")
        sleep_n_sec(
            "{{item}}",
        ).with_(
            name="sleep",
            with_param=g.result,
        )

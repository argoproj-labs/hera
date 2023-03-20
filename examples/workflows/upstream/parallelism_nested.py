from hera.workflows import Container, Parameter, Step, Steps, Workflow

with Workflow(
    generate_name="parallelism-nested-",
    entrypoint="parallel-worker",
    arguments=[
        Parameter(name="seq-list", value='["a","b","c","d"]\n'),
        Parameter(name="parallel-list", value="[1,2,3,4]\n"),
    ],
) as w:
    one_job = Container(
        name="one-job",
        image="alpine",
        command=["/bin/sh", "-c"],
        args=["echo {{inputs.parameters.parallel-id}} {{inputs.parameters.seq-id}}; sleep 10"],
        inputs=[Parameter(name="seq-id"), Parameter(name="parallel-id")],
    )

    with Steps(
        name="seq-worker", parallelism=1, inputs=[Parameter(name="seq-list"), Parameter(name="parallel-id")]
    ) as seq_worker:
        with seq_worker.parallel():
            one_job(
                name="seq-step",
                arguments=[
                    Parameter(name="parallel-id", value="{{inputs.parameters.parallel-id}}"),
                    Parameter(name="seq-id", value="{{item}}"),
                ],
                with_param="{{inputs.parameters.seq-list}}",
            )

    with Steps(
        name="parallel-worker", inputs=[Parameter(name="seq-list"), Parameter(name="parallel-list")]
    ) as parallel_worker:
        Step(
            name="parallel-worker",
            template=seq_worker,
            arguments=[
                Parameter(name="seq-list", value="{{inputs.parameters.seq-list}}"),
                Parameter(name="parallel-id", value="{{item}}"),
            ],
            with_param="{{inputs.parameters.parallel-list}}",
        )

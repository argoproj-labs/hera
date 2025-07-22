from hera.workflows import Script, Step, Steps, Workflow
from hera.workflows.models import Arguments, Inputs, Item, Parameter

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    generate_name="parameter-aggregation-script-",
    entrypoint="parameter-aggregation",
) as w:
    with Steps(
        name="parameter-aggregation",
    ) as invocator:
        Step(
            with_items=[
                Item(
                    __root__=1,
                ),
                Item(
                    __root__=2,
                ),
                Item(
                    __root__=3,
                ),
                Item(
                    __root__=4,
                ),
            ],
            arguments=Arguments(
                parameters=[
                    Parameter(
                        name="num",
                        value="{{item}}",
                    )
                ],
            ),
            name="odd-or-even",
            template="odd-or-even",
        )
        Step(
            with_param="{{steps.odd-or-even.outputs.result}}",
            arguments=Arguments(
                parameters=[
                    Parameter(
                        name="num",
                        value="{{item.num}}",
                    )
                ],
            ),
            name="divide-by-2",
            template="divide-by-2",
            when="{{item.evenness}} == even",
        )
    Script(
        inputs=Inputs(
            parameters=[
                Parameter(
                    name="num",
                )
            ],
        ),
        name="odd-or-even",
        command=["python"],
        image="python:alpine3.6",
        source='import json\ni = {{inputs.parameters.num}}\nres = {\n  "num": i,\n  "evenness": "even" if i % 2 == 0 else "odd"\n}\nprint(json.dumps(res))\n',
    )
    Script(
        inputs=Inputs(
            parameters=[
                Parameter(
                    name="num",
                )
            ],
        ),
        name="divide-by-2",
        command=["sh", "-x"],
        image="alpine:latest",
        source="echo $(({{inputs.parameters.num}}/2))\n",
    )

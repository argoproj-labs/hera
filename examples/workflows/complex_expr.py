"""This example showcases how to string together complex expressions.

This example is a python replica of
https://github.com/argoproj/argo-workflows/blob/master/examples/expression-reusing-verbose-snippets.yaml
"""
import base64
import json

from hera.expr import C, g, it, sprig
from hera.workflows import Container, Env, Parameter, Workflow


def base64_encode(input: str) -> str:
    return base64.b64encode(input.encode()).decode()


data = json.dumps({"temps": [34, 27, 15, 57, 46]})
encoded_data = json.dumps({"weekWeather": base64_encode(data)})


def construct_weekly_temps():
    weather = g.workflow.parameters.weather
    week_weather = sprig.b64dec(weather.jsonpath("$.weekWeather"))
    temps = C([week_weather.jsonpath("$.temps")])
    iterators = [it[i] for i in range(5)]
    return temps.map(
        C(
            {
                "avg": sprig.add(*iterators) / 5,
                "min": sprig.min(*iterators),
                "max": sprig.max(*iterators),
            }
        ).to_json()
    )[0]


with Workflow(generate_name="expression-reusing-verbose-snippets-", entrypoint="c") as w:
    w.arguments = [Parameter(name="weather", value=encoded_data)]
    week_temps = construct_weekly_temps()
    week_temps_jsonpath = g.inputs.parameters["week-temps"].jsonpath
    c = Container(
        name="c",
        inputs=[Parameter(name="week-temps", value=f"{week_temps:=}")],
        env=[
            Env(name="MIN", value=f"{week_temps_jsonpath('$.min'):=}"),
            Env(name="MAX", value=f"{week_temps_jsonpath('$.max'):=}"),
            Env(name="AVG", value=f"{week_temps_jsonpath('$.avg'):=}"),
        ],
        command=["echo", "The week's average temperature was $AVG with a minimum of $MIN and a maximum of $MAX."],
        image="alpine:3.7",
    )

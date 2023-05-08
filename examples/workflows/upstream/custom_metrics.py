from hera.workflows import (
    Container,
    Gauge,
    Histogram,
Counter,
    Label,
    Parameter,
    Steps,
    Workflow,
    models as m,
)

random_int = Container(
    name="random-int",
    image="alpine:latest",
    command=["sh", "-c"],
    args=["RAND_INT=$((1 + RANDOM % 10)); echo $RAND_INT; echo $RAND_INT > /tmp/rand_int.txt"],
    metrics=[
        Histogram(
            name="random_int_step_histogram",
            help="Value of the int emitted by random-int at step level",
            when="{{status}} == Succeeded",
            buckets=[2.01, 4.01, 6.01, 8.01, 10.01],
            value="{{outputs.parameters.rand-int-value}}",
        ),
        Gauge(
            name="duration_gauge",
            labels=Label(key="name", value="random-int"),
            help="Duration gauge by name",
            realtime=True,
            value="{{duration}}",
        ),
    ],
    outputs=Parameter(
        name="rand-int-value", global_name="rand-int-value", value_from=m.ValueFrom(path="/tmp/rand_int.txt")
    ),
)
flakey = Container(
    name="flakey",
    image="python:alpine3.6",
    command=["python", "-c"],
    args=["import random; import sys; exit_code = random.choice([0, 1, 1]); sys.exit(exit_code)"],
    metrics=Counter(
        name="result_counter",
        labels=[Label(key="name", value="flakey"), Label(key="status", value="{{status}}")],
        help="Count of step execution by result status",
        value="1",
    ),
)

with Workflow(
    generate_name="hello-world-",
    entrypoint="steps",
    metrics=Gauge(
        name="duration_gauge",
        labels=Label(key="name", value="workflow"),
        help="Duration gauge by name",
        realtime=True,
        value="{{workflow.duration}}",
    ),
) as w:
    with Steps(
        name="steps",
        metrics=Gauge(
            name="duration_gauge",
            labels=Label(key="name", value="steps"),
            help="Duration gauge by name",
            realtime=True,
            value="{{duration}}",
        ),
    ):
        random_int()
        flakey()

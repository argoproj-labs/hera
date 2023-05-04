"""
This example showcases how to generate and parallelize generated sequences
"""
from hera.workflows import DAG, Workflow, script
from hera.workflows.models import Sequence


@script()
def gen_num():
    print(3)


@script()
def say(message: str):
    print(message)


with Workflow(generate_name="with-sequence-example", entrypoint="d") as w:
    with DAG(name="d"):
        t1 = gen_num(name="t1")
        t2 = say(name="t2", with_sequence=Sequence(count=t1.result, start=0), arguments={"message": "{{item}}"})
        t3 = say(
            name="t3",
            with_sequence=Sequence(start=t1.result, end=5, format="2020-05-%02X"),
            arguments={"message": "{{item}}"},
        )
        t1 >> [t2, t3]

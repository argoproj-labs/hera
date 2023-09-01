"""
This example showcases how to generate and parallelize generated sequences
"""
from hera.workflows import DAG, Workflow, script
from hera.workflows.models import Sequence


@script(directly_callable=True)
def gen_num():
    print(3)


@script(directly_callable=True)
def say(message: str):
    print(message)


with Workflow(generate_name="with-sequence-example", entrypoint="d") as w:
    with DAG(name="d"):
        t1 = gen_num().with_(name="t1")
        t2 = say("{{item}}").with_(name="t2", with_sequence=Sequence(count=t1.result, start="0"))
        t3 = say("{{item}}").with_(
            name="t3",
            with_sequence=Sequence(start=t1.result, end="5", format="2020-05-%02X"),
        )
        t1 >> [t2, t3]

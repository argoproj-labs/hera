"""
This example showcases how to generate and parallelize generated sequences
"""
from hera import Sequence, Task, Workflow


def gen_num():
    print(3)


def say(message: str):
    print(message)


# assumes you used `hera.set_global_token` and `hera.set_global_host` so that the workflow can be submitted
with Workflow(generate_name="with-sequence-") as w:
    t1 = Task("gen-num", gen_num)
    t2 = Task("count", say, with_sequence=Sequence(count=t1.get_result(), start=0))
    t3 = Task("date", say, with_sequence=Sequence(start=t1.get_result(), end=5, format="2020-05-%02X"))

    t1 >> [t2, t3]

w.create()

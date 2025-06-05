"""This example shows how you can (carefully!) recurse on a DAG template."""

from hera.workflows import DAG, Task, Workflow, script


@script()
def random_roll():
    import random

    print(random.randint(1, 6))


with Workflow(generate_name="recursive-dag-", entrypoint="dag") as w:
    with DAG(name="dag") as dag:
        random_number = random_roll(name="roll")
        recurse = Task(
            name="recurse-if-not-six",
            template=dag,
            when=f"{random_number.result} != 6",
        )
        random_number >> recurse

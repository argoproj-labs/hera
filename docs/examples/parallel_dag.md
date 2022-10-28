# Parallel DAG

This example showcases how one can schedule a workflow with a parallel DAG task through Hera

```python
from hera import DAG, Parameter, Task, Workflow


def produce(instruction: str):
    instruction_map = {"a": "x", "b": "y", "c": "z"}
    print(instruction_map[instruction])


def wrap(product: str):
    print(f"({product})")


def gather(products: str):
    print(products)


# assumes you used `hera.set_global_token` and `hera.set_global_host` so that the workflow can be submitted
with Workflow("parallel-dag") as wf:
    with DAG("pipeline", inputs=[Parameter("instruction")], outputs=[Parameter("instruction")]) as pipeline:
        t1 = Task("create", produce, inputs=[pipeline.get_parameter("instruction")])
        t2 = Task("wrap", wrap, inputs=[t1.get_result_as("product")])
        t1 >> t2
        pipeline.outputs = [t2.get_result_as("output")]

    t1 = Task("parallel-pipelines", dag=pipeline, with_param=["a", "b", "c"])
    t2 = Task("gather-results", gather, inputs=[t1.get_parameters_as("products")])
    t1 >> t2

wf.create()

```
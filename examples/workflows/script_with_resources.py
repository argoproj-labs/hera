from hera.workflows import Resources, Workflow, script


@script(resources=Resources(memory_request="5Gi"))
def task_with_memory_request():
    print("ok")


with Workflow(generate_name="script-with-resources-", entrypoint="task-with-memory-request") as w:
    task_with_memory_request()

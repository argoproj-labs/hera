from hera.workflows import DAG, Workflow, WorkflowStatus, script


@script()
def echo(s: str):
    print(s)


with Workflow(generate_name="on-exit-", entrypoint="d") as w:
    with DAG(name="exit-procedure") as exit_procedure:
        (
            echo(name="t3", s=1).on_workflow_status(WorkflowStatus.succeeded)
            >> echo(name="t4", s=2).on_workflow_status(WorkflowStatus.succeeded)
        )

        (
            echo(name="t5", s="3").on_workflow_status(WorkflowStatus.error)
            >> echo(name="t6", s="4").on_workflow_status(WorkflowStatus.error)
        )

    with DAG(name="d"):
        echo(name="t1", s="a") >> echo(name="t2", s="b")
    w.on_exit = exit_procedure

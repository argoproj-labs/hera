from hera.workflows import DAG, Workflow, WorkflowStatus, script


@script(directly_callable=True)
def echo(s: str):
    print(s)


with Workflow(generate_name="on-exit-", entrypoint="d") as w:
    with DAG(name="exit-procedure") as exit_procedure:
        (
            echo(1).with_(name="t3").on_workflow_status(WorkflowStatus.succeeded)
            >> echo(2).with_(name="t4").on_workflow_status(WorkflowStatus.succeeded)
        )

        (
            echo("3").with_(name="t5").on_workflow_status(WorkflowStatus.error)
            >> echo("4").with_(name="t6").on_workflow_status(WorkflowStatus.error)
        )

    with DAG(name="d"):
        echo("a").with_(name="t1") >> echo("b").with_(name="t2")
    w.on_exit = exit_procedure

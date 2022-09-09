from hera import DAG, Operator, Task, Workflow, WorkflowService, WorkflowStatus


def echo(s: str):
    print(s)


with Workflow("on-exit1", service=WorkflowService(host="my-argo-server.com", token="my-auth-token")) as w:
    Task("t1", echo, [{"s": "a"}]) >> Task("t2", echo, [{"s": "b"}])

    with DAG("exit-procedure") as exit_procedure:
        t3 = Task("t3", echo, [{"s": "1"}]).on_workflow_status(Operator.Equals, WorkflowStatus.Succeeded)
        t4 = Task("t4", echo, [{"s": "2"}]).on_workflow_status(Operator.Equals, WorkflowStatus.Succeeded)
        t3 >> t4

        t5 = Task("t5", echo, [{"s": "3"}]).on_workflow_status(Operator.Equals, WorkflowStatus.Error)
        t6 = Task("t6", echo, [{"s": "4"}]).on_workflow_status(Operator.Equals, WorkflowStatus.Error)
        t5 >> t6

    w.on_exit(exit_procedure)
w.create()

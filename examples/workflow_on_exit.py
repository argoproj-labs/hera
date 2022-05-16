from hera import Operator, Task, Workflow, WorkflowService, WorkflowStatus


def echo(s: str):
    print(s)


ws = WorkflowService(host='https://my-argo-server.com', token='my-auth-token')
w = Workflow('on-exit1', ws)
t1 = Task('t1', echo, [{'s': 'a'}])
t2 = Task('t2', echo, [{'s': 'b'}])
t1 >> t2
w.add_tasks(t1, t2)

exit_w = Workflow('exit-handler', ws)
t3 = Task('t3', echo, [{'s': '1'}])
t4 = Task('t4', echo, [{'s': '2'}])
exit_w.add_tasks(t3, t4)

w.on_exit(exit_w, Operator.equals, WorkflowStatus.Succeeded)
w.create()

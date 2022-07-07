from hera import ExitTask, Task, Workflow, WorkflowService


def bye():
    print('Bye Hera')


def echo(s: str):
    print(f'Hello Hera, {s}')


# TODO: replace the domain, token with your own
ws = WorkflowService(host='', token='')
w = Workflow('task-exit-handler', ws)
exit_hook = ExitTask('running', bye)
t1 = Task('t1', echo, [{'s': 'from Task1'}])
t1.on_exit(exit_hook)
t2 = Task('t2', echo, [{'s': 'from Task2'}])
t1 >> t2
w.add_tasks(t1, t2, exit_hook)
w.create(namespace='argo')

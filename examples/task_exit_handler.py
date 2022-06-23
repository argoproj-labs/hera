from hera import Task, Workflow, WorkflowService


def on_exit():
    print('Bye Hera')


def echo(s: str):
    print(f'Hello Hera, {s}')


# TODO: replace the domain, token with your own
ws = WorkflowService(host='', token='')
w = Workflow('task-exit-handler-', ws)
exit_hook = Task('running', on_exit)
t1 = Task('t1', echo, [{'s': 'from Task1'}], exit_hook=exit_hook)
t2 = Task('t2', echo, [{'s': 'from Task2'}])
t1 >> t2
w.add_tasks(t1, t2)
w.create(namespace='argo')

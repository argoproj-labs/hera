from hera import InputParameter, OutputPathParameter, Task, Workflow, WorkflowService


def produce():
    with open('/test.txt', 'w') as f:
        f.write('Hello, world!')


def consume(msg: str):
    print(f'Message was: {msg}')


p = Task('p', produce, outputs=[OutputPathParameter('msg', '/test.txt')])
c = Task('c', consume, inputs=[InputParameter('msg', p.name, 'msg')])
p >> c

ws = WorkflowService(host='https://my-argo-server.com', token='token')
w = Workflow('io')
w.add_tasks(p, c)
w.create()

from hera import InputParameter, OutputPathParameter, Task, Workflow, WorkflowService


def produce():
    with open('/test.txt', 'w') as f:
        f.write('Hello, world!')


def consume(msg: str):
    print(f'Message was: {msg}')


with Workflow('io', service=WorkflowService(host='https://my-argo-server.com', token='my-auth-token')) as w:
    (
        Task('p', produce, outputs=[OutputPathParameter('msg', '/test.txt')])
        >> Task('c', consume, inputs=[InputParameter('msg', p.name, 'msg')])
    )

w.create()

from hera import (
    InputFrom,
    MultiInput,
    OutputPathParameter,
    Task,
    Workflow,
    WorkflowService,
)


def generate():
    import json
    import sys

    # this can be anything! e.g fetch from some API, then in parallel process all entities; chunk database records
    # and process them in parallel, etc.
    json.dump([{'value': i} for i in range(10)], sys.stdout)


def fanout(value: int):
    print(f'Received value: {value}!')
    with open('/tmp/number', 'w') as f:
        f.write(str(value))


def fanin(values: list):
    print(f'Received values: {values}!')


# TODO: replace the domain and token with your own
ws = WorkflowService(host='https://my-argo-server.com', token='my-auth-token')
w = Workflow('dynamic-fanout', ws)
generate_task = Task('generate', generate)
fanout_task = Task(
    'fanout',
    fanout,
    input_from=InputFrom('generate', ['value']),
    outputs=[OutputPathParameter('fanout', '/tmp/number')],
)
fanin_task = Task('fanin', fanin, inputs=[MultiInput('values', fanout_task.name)])

generate_task >> fanout_task >> fanin_task

w.add_tasks(generate_task, fanout_task, fanin_task)
w.create()

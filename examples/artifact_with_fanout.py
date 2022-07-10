from hera import (
    InputArtifact,
    InputFrom,
    OutputArtifact,
    Task,
    Workflow,
    WorkflowService,
)


def writer():
    import json

    with open('/file', 'w+') as f:
        for i in range(10):
            f.write(f'{json.dumps(i)}\n')


def fanout():
    import json
    import sys

    indices = []
    with open('/file', 'r') as f:
        for line in f.readlines():
            indices.append({'i': line})
    json.dump(indices, sys.stdout)


def consumer(i: int):
    print(i)


with Workflow(
    'artifact-with-fanout',
    service=WorkflowService(host='https://my-argo-server.com', token='my-auth-token'),
) as w:
    w_t = Task('writer', writer, output_artifacts=[OutputArtifact('test', '/file')])
    f_t = Task(
        'fanout',
        fanout,
        input_artifacts=[InputArtifact('test', '/file', 'writer', 'test')],
    )
    c_t = Task('consumer', consumer, input_from=InputFrom(name='fanout', parameters=['i']))
    w_t >> f_t >> c_t

w.create()

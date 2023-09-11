from hera.workflows import DAG, Artifact, Workflow, script


@script(outputs=Artifact(name="result", path="/tmp/result"))
def produce():
    import pickle

    result = "foo testing"
    with open("/tmp/result", "wb") as f:
        pickle.dump(result, f)


@script(inputs=Artifact(name="i", path="/tmp/i"))
def consume(i):
    import pickle

    with open("/tmp/i", "rb") as f:
        i = pickle.load(f)
    print(i)


with Workflow(generate_name="fv-test-", entrypoint="d") as w:
    with DAG(name="d"):
        p = produce()
        c = consume(arguments=Artifact(name="i", from_="{{tasks.produce.outputs.artifacts.result}}"))
        p >> c

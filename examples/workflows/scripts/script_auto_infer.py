"""This example shows an anti-pattern.

It is not recommended to use a parameter name that is the same as an input Artifact. This will generally cause confusion
but can be useful for testing the function directly. Instead, it is recommended to use the Hera Runner,
[see the Artifact example using the Hera Runner](../hera-runner/basic_artifacts.md).
"""

from hera.workflows import DAG, Artifact, Workflow, script


@script(outputs=Artifact(name="result-art", path="/tmp/result"))
def produce():
    import pickle

    result = "foo testing"
    with open("/tmp/result", "wb") as f:
        pickle.dump(result, f)


@script(inputs=Artifact(name="i", path="/tmp/i"))
def consume(i):  # Note that the parameter name is the same as the input Artifact name
    import pickle

    with open("/tmp/i", "rb") as f:
        i = pickle.load(f)
    print(i)


with Workflow(generate_name="masked-parameter-", entrypoint="d") as w:
    with DAG(name="d"):
        p = produce()
        c = consume(arguments={"i": p.get_artifact("result-art")})
        p >> c

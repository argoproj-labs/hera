"""Example derived from: https://medium.com/@corvin/dynamic-fan-out-and-fan-in-in-argo-workflows-d731e144e2fd"""
from hera import Artifact, GCSArtifact, Task, Workflow


def generate():
    import json
    import os
    import sys

    files = []
    # Don't output directly in /tmp/ as it could contain other files
    output_folder = "/tmp/output-files"
    os.makedirs(output_folder)
    for i in range(1, 4):
        filename = f"file{i}.txt"
        files.append(filename)
        with open(os.path.join(output_folder, filename), "w") as f:
            f.write(f"hello {i}")
    # Writing a JSON-compliant array of filenames to the output
    json.dump(files, sys.stdout)


def fanout_print():
    with open("input-file", "r") as f:
        file_content = f.read()
    print(f"file content: {file_content}")


# assumes you used `hera.set_global_token` and `hera.set_global_host` so that the workflow can be submitted
with Workflow(generate_name="artifact-test-") as wf:
    t1 = Task(
        "generate",
        generate,
        outputs=[
            Artifact(
                name="artifact-files",
                path="/tmp/output-files/",
                gcs=GCSArtifact(
                    bucket="<your bucket name>",
                    key=f"fanout-{wf.get_name()}",
                ),
            ),
        ],
    )

    t2 = Task(
        "fanout-print",
        fanout_print,
        with_param=t1.get_result(),
        inputs=[  # {{item}} refers to each element (file) in t1.get_result()
            t1.get_artifact("artifact-files").to_path("input-file", sub_path="{{item}}")
        ],
    )

    t3 = Task(
        "fanin",
        image="alpine:latest",
        command=["sh", "-c"],
        args=["ls /tmp/output-files/"],
        inputs=[t1.get_artifact("artifact-files")],
    )

    t1 >> t2 >> t3

wf.create()

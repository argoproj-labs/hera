from hera.workflows import (
    Artifact,
    Container,
    Parameter,
    RawArtifact,
    Workflow,
    models as m,
)

with Workflow(
    generate_name="artifact-path-placeholders-",
    entrypoint="head-lines",
    arguments=[Parameter(name="lines-count", value=3), RawArtifact(name="text", data="1\n2\n3\n4\n5\n")],
) as w:
    Container(
        name="head-lines",
        image="busybox",
        command=[
            "sh",
            "-c",
            'mkdir -p "$(dirname "{{outputs.artifacts.text.path}}")" '
            '"$(dirname "{{outputs.parameters.actual-lines-count.path}}")" ; '
            'head -n {{inputs.parameters.lines-count}} < "{{inputs.artifacts.text.path}}" '
            '| tee "{{outputs.artifacts.text.path}}" | wc -l > "{{outputs.parameters.actual-lines-count.path}}"',
        ],
        inputs=[
            Parameter(name="lines-count"),
            Artifact(name="text", path="/inputs/text/data"),
        ],
        outputs=[
            Parameter(name="actual-lines-count", value_from=m.ValueFrom(path="/outputs/actual-lines-count/data")),
            Artifact(name="text", path="/outputs/text/data"),
        ],
    )

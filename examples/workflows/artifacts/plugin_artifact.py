"""This example showcases an output artifact written via an artifact-driver plugin.

Argo Workflows v4+ exposes a `plugin` driver on `Artifact`, which lets the controller
delegate artifact storage to a named plugin (e.g. `oras` for OCI registries) rather than
one of the built-in drivers (S3, GCS, Git, ...). The `configuration` field carries the
plugin-defined YAML payload as a string.
"""

from hera.workflows import NoneArchiveStrategy, PluginArtifact, Steps, Workflow, script


@script(
    outputs=PluginArtifact(
        name="image-sbom",
        path="/tmp/sbom.json",
        plugin_name="oras",
        key="sbom",
        configuration="image: registry.example.com/my-image:latest",
        archive=NoneArchiveStrategy(),
    )
)
def emit_sbom():
    with open("/tmp/sbom.json", "w") as f:
        f.write('{"format": "spdx"}')


with Workflow(generate_name="plugin-artifact-", entrypoint="steps") as w:
    with Steps(name="steps"):
        emit_sbom()

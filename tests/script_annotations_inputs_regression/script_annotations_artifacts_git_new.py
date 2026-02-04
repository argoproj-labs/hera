"""Regression test: compare the new Annotated style inputs declaration with the old version."""

from typing import Annotated

import hera.workflows.models as m
from hera.shared import global_config
from hera.workflows import Workflow, script
from hera.workflows.artifact import Artifact, GitArtifact
from hera.workflows.steps import Steps

global_config.experimental_features["script_annotations"] = True


@script()
def read_artifact(
    my_artifact: Annotated[
        str,
        GitArtifact(
            name="my_artifact",
            path="/tmp/file",
            branch="my-branch",
            depth=1,
            disable_submodules=True,
            fetch=["refs/meta/*"],
            insecure_ignore_host_key=True,
            password_secret=m.SecretKeySelector.validate({"name": "github-creds", "key": "password"}),
            repo="https://github.com/argoproj/argo-workflows.git",
            revision="v2.1.1",
            single_branch=True,
            ssh_private_key_secret=m.SecretKeySelector.validate({"name": "github-creds", "key": "ssh-private-key"}),
            username_secret=m.SecretKeySelector.validate({"name": "github-creds", "key": "username"}),
        ),
    ],
) -> str:
    return my_artifact


with Workflow(generate_name="test-artifacts-", entrypoint="my-steps") as w:
    with Steps(name="my-steps") as s:
        read_artifact(arguments=[Artifact(name="my_artifact", from_="somewhere")])

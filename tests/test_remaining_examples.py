import os
import pkgutil
from pathlib import Path
from typing import List

import examples.workflows.upstream as hera_upstream_examples
import pytest
import requests
import yaml

from hera.workflows import ClusterWorkflowTemplate, CronWorkflow, Workflow, WorkflowTemplate
from tests.test_examples import CI_MODE, HERA_REGENERATE

ARGO_REPO_URL = "https://raw.githubusercontent.com/argoproj/argo-workflows/main/examples"
GITHUB_API_ARGO = "https://api.github.com/repos/argoproj/argo-workflows/git/trees/main?recursive=1"
UPSTREAM_EXAMPLES_FOLDER = Path("examples/workflows/upstream")
# A subset of the upstream examples are known to fail, but a majority pass. We'll
# selectively xfail these examples rather than all until they can be fixed.
UPSTREAM_EXAMPLE_XFAIL_FILES = [
    "cluster-workflow-template__clustertemplates.upstream.yaml",
    "cron-backfill.upstream.yaml",
    "memoize-simple.upstream.yaml",
    "pod-gc-strategy-with-label-selector.upstream.yaml",
    "pod-gc-strategy.upstream.yaml",
    "webhdfs-input-output-artifacts.upstream.yaml",
    "workflow-template__templates.upstream.yaml",
    "synchronization-wf-level.upstream.yaml",
    "synchronization-mutex-tmpl-level.upstream.yaml",
    "synchronization-mutex-wf-level.upstream.yaml",
    "synchronization-tmpl-level.upstream.yaml",
    "cron-when.upstream.yaml",
    "cron-workflow-multiple-schedules.upstream.yaml",
]


def _save_upstream_examples(argo_examples: List[str]) -> None:
    for example in argo_examples:
        output_file = example.replace("/", "__") + ".upstream.yaml"
        output_path = Path(f"examples/workflows/upstream/{output_file}")

        if HERA_REGENERATE or not output_path.exists():
            output_path.write_text(requests.get(f"{ARGO_REPO_URL}/{example}.yaml").text)
            print(f"Output file at {output_file}")


@pytest.mark.skipif(CI_MODE, reason="Dev tool test")
def test_for_missing_examples():
    repo_json = requests.get(GITHUB_API_ARGO).json()
    argo_examples = [
        file["path"] for file in repo_json["tree"] if "examples/" in file["path"] and ".yaml" in file["path"]
    ]

    argo_examples = [file[len("examples/") :][: -len(".yaml")] for file in argo_examples]
    _save_upstream_examples(argo_examples)

    hera_examples = [name for _, name, _ in pkgutil.iter_modules(hera_upstream_examples.__path__)]
    hera_examples = list(map(lambda file: file.replace("__", "/").replace("_", "-"), hera_examples))

    missing = set(argo_examples).difference(hera_examples)

    missing_examples = {
        example: f"https://github.com/argoproj/argo-workflows/blob/main/examples/{example}.yaml"
        for example in sorted(missing)
    }

    missing_examples_header = "## List of **missing** examples"

    lines = []
    with open("examples/workflows-examples.md", "r", encoding="utf-8") as examples_file:
        while True:
            line = examples_file.readline()
            if not line or missing_examples_header in line:
                break
            lines.append(line)

    if len(missing) > 0:
        lines.append(missing_examples_header)
        lines.append("\n\n")
        lines.append("*You can help by contributing these examples!*\n\n")
        lines.append("| Example |\n")
        lines.append("|---------|\n")
        for name, link in missing_examples.items():
            lines.append(f"| [{name}]({link}) |\n")

    with open("examples/workflows-examples.md", "w", encoding="utf-8") as examples_file:
        examples_file.writelines(lines)


@pytest.mark.parametrize(
    "file_name",
    [
        pytest.param(
            f,
            marks=(
                pytest.mark.xfail(
                    reason="Multiple workflows in one yaml file not yet supported.\nYAML round trip issues for certain types."
                )
                if f in UPSTREAM_EXAMPLE_XFAIL_FILES
                else ()
            ),
        )
        for f in os.listdir(UPSTREAM_EXAMPLES_FOLDER)
        if os.path.isfile(UPSTREAM_EXAMPLES_FOLDER / f) and f.endswith(".upstream.yaml")
    ],
)
def test_upstream_examples_roundtrip(file_name):
    spec = yaml.load((UPSTREAM_EXAMPLES_FOLDER / file_name).read_text(), Loader=yaml.FullLoader)
    kind = spec["kind"]
    if kind not in (
        "Workflow",
        "WorkflowTemplate",
        "ClusterWorkflowTemplate",
        "CronWorkflow",
    ):
        print(f"UNKNOWN KIND: {kind}")
        return

    if kind == "Workflow":
        kind_class = Workflow
    elif kind == "WorkflowTemplate":
        kind_class = WorkflowTemplate
    elif kind == "ClusterWorkflowTemplate":
        kind_class = ClusterWorkflowTemplate
    elif kind == "CronWorkflow":
        kind_class = CronWorkflow

    assert kind_class.from_dict(spec).to_dict() == spec

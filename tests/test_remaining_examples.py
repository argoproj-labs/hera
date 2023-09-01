from pathlib import Path
import pkgutil
from typing import List

import examples.workflows.upstream as hera_upstream_examples
import pytest
import requests

from tests.test_examples import CI_MODE, HERA_REGENERATE

ARGO_REPO_URL = "https://raw.githubusercontent.com/argoproj/argo-workflows/master/examples"
GITHUB_API_ARGO = "https://api.github.com/repos/argoproj/argo-workflows/git/trees/master?recursive=1"


def save_upstream_examples(argo_examples: List[str]) -> None:
    for example in argo_examples:
        output_file = example.replace("/", "__") + ".upstream.yaml"
        output_path = Path(f"examples/workflows/upstream/{output_file}")

        if HERA_REGENERATE or not output_path.exists():
            output_path.write_text(requests.get(f"{ARGO_REPO_URL}/{example}.yaml").text)
            print(f"Output file at {output_file}")
        else:
            print(f"Skipped {example}")


@pytest.mark.skipif(CI_MODE, reason="Dev tool test")
def test_for_missing_examples():
    repo_json = requests.get(GITHUB_API_ARGO).json()
    argo_examples = [
        file["path"] for file in repo_json["tree"] if "examples/" in file["path"] and ".yaml" in file["path"]
    ]

    argo_examples = [file[len("examples/") :][: -len(".yaml")] for file in argo_examples]
    save_upstream_examples(argo_examples)

    hera_examples = [name for _, name, _ in pkgutil.iter_modules(hera_upstream_examples.__path__)]
    hera_examples = list(map(lambda file: file.replace("__", "/").replace("_", "-"), hera_examples))

    missing = set(argo_examples).difference(hera_examples)

    missing_examples = {
        example: f"https://github.com/argoproj/argo-workflows/blob/master/examples/{example}.yaml"
        for example in sorted(missing)
    }

    missing_examples_header = "## List of **missing** examples"

    lines = []
    with open("docs/examples/workflows-examples.md", "r", encoding="utf-8") as examples_file:
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

        with open("docs/examples/workflows-examples.md", "w", encoding="utf-8") as examples_file:
            examples_file.writelines(lines)

        assert False, f"Missing {len(missing)} examples"

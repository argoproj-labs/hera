import json
import pkgutil

import pytest
import requests

import examples.workflows.upstream as hera_upstream_examples

GITHUB_API_ARGO = "https://api.github.com/repos/argoproj/argo-workflows/git/trees/master?recursive=1"


@pytest.mark.xfail(reason="Dev tool test")
def test_for_missing_examples():
    repo_json = requests.get(GITHUB_API_ARGO).json()
    argo_examples = [
        file["path"] for file in repo_json["tree"] if "examples/" in file["path"] and ".yaml" in file["path"]
    ]

    argo_examples = map(lambda file: file.removeprefix("examples/").removesuffix(".yaml"), argo_examples)

    hera_examples = [name for _, name, _ in pkgutil.iter_modules(hera_upstream_examples.__path__)]
    hera_examples = list(map(lambda file: file.replace("__", "/").replace("_", "-"), hera_examples))

    missing = set(argo_examples).difference(hera_examples)

    missing_examples = {
        example: f"https://github.com/argoproj/argo-workflows/blob/master/examples/{example}.yaml"
        for example in missing
    }

    assert len(missing) == 0, f"Missing {len(missing)} examples: {json.dumps(missing_examples, indent=2)}"

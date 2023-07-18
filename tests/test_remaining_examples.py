import json
import pkgutil

import examples.workflows.upstream as hera_upstream_examples
import pytest
import requests

GITHUB_API_ARGO = "https://api.github.com/repos/argoproj/argo-workflows/git/trees/master?recursive=1"


@pytest.mark.xfail(reason="Dev tool test")
def test_for_missing_examples():
    repo_json = requests.get(GITHUB_API_ARGO).json()
    argo_examples = [
        file["path"] for file in repo_json["tree"] if "examples/" in file["path"] and ".yaml" in file["path"]
    ]

    argo_examples = map(lambda file: file[len("examples/") :][: -len(".yaml")], argo_examples)

    hera_examples = [name for _, name, _ in pkgutil.iter_modules(hera_upstream_examples.__path__)]
    hera_examples = list(map(lambda file: file.replace("__", "/").replace("_", "-"), hera_examples))

    missing = set(argo_examples).difference(hera_examples)

    missing_examples = {
        example: f"https://github.com/argoproj/argo-workflows/blob/master/examples/{example}.yaml"
        for example in missing
    }

    if len(missing) > 0:
        print("| Name | Link |")
        print("|------|------|")
        for name, link in missing_examples.items():
            print(f"| {name} | {link} |")
        assert False, f"Missing {len(missing)} examples"

"""This small module downloads and adjusts the OpenAPI spec of a given Argo Workflows version."""

import json
import logging
import re
import sys
from typing import Dict, List, Set

import requests

logger: logging.Logger = logging.getLogger(__name__)

# get the version from the command line, along with the output file
version = sys.argv[1]

# ensure that the version satisfies the pattern v1.2.3
if not re.match(r"\d+\.\d+\.\d+", version):
    raise ValueError(f"Invalid version {version}, expected pattern `1.2.3`")

output_file = sys.argv[2]

# download the spec
response = requests.get(
    f"https://raw.githubusercontent.com/argoproj/argo-workflows/v{version}/api/openapi-spec/swagger.json"
)

# get the spec into a dictionary
spec = response.json()

optional_fields_map: Dict[str, List[str]] = {
    "io.argoproj.workflow.v1alpha1.CronWorkflowStatus": ["active", "lastScheduledTime", "conditions"],
    "io.argoproj.workflow.v1alpha1.CronWorkflowList": ["items"],
    "io.argoproj.workflow.v1alpha1.ClusterWorkflowTemplateList": ["items"],
    "io.argoproj.workflow.v1alpha1.WorkflowList": ["items"],
    "io.argoproj.workflow.v1alpha1.WorkflowTemplateList": ["items"],
    "io.argoproj.workflow.v1alpha1.WorkflowEventBindingList": ["items"],
    "io.argoproj.workflow.v1alpha1.Metrics": ["prometheus"],
}
for definition, optional_fields in optional_fields_map.items():
    try:
        curr_required: Set[str] = set(spec["definitions"][definition]["required"])
    except KeyError as e:
        raise KeyError(
            f"Could not find definition {definition} in Argo specification for version {version}, caught error: {e}"
        )
    for optional_field in optional_fields:
        if optional_field in curr_required:
            curr_required.remove(optional_field)
        else:
            logger.warning(
                f"Expected to find and change field {optional_fields} of {definition} from required to optional, "
                f"but it was not found"
            )
    spec["definitions"][definition]["required"] = list(curr_required)

with open(output_file, "w+") as f:
    json.dump(spec, f, indent=2)

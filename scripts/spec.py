"""This small module downloads and adjusts the OpenAPI spec of a given Argo Workflows version."""

import json
import logging
import re
import sys
from typing import Dict, List, Set

import requests

logger: logging.Logger = logging.getLogger(__name__)

# get the version from the command line, along with the output file
open_api_spec_url = sys.argv[1]
assert open_api_spec_url is not None, "Expected the OpenAPI spec URL to be passed as the first argument"

output_file = sys.argv[2]
assert output_file is not None, "Expected the output file to be passed as the second argument"

# download the spec
response = requests.get(open_api_spec_url)

# get the spec into a dictionary
spec = response.json()

# these are specifications of objects with fields that are marked as required. However, it is possible for the Argo
# Server to not return anything for those fields. In those cases, Pydantic fails type validation for those objects.
# Here, we maintain a map of objects specifications whose fields must be marked as optional i.e. removed from the
# `required` list in the OpenAPI specification.
DEFINITION_TO_OPTIONAL_FIELDS: Dict[str, List[str]] = {
    "io.argoproj.workflow.v1alpha1.CronWorkflowStatus": ["active", "lastScheduledTime", "conditions"],
    "io.argoproj.workflow.v1alpha1.CronWorkflowList": ["items"],
    "io.argoproj.workflow.v1alpha1.ClusterWorkflowTemplateList": ["items"],
    "io.argoproj.workflow.v1alpha1.WorkflowList": ["items"],
    "io.argoproj.workflow.v1alpha1.WorkflowTemplateList": ["items"],
    "io.argoproj.workflow.v1alpha1.WorkflowEventBindingList": ["items"],
    "io.argoproj.workflow.v1alpha1.Metrics": ["prometheus"],
}
for definition, optional_fields in DEFINITION_TO_OPTIONAL_FIELDS.items():
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

# finally, we write the spec to the output file that is passed to use assuming the client wants to perform
# something with this file
with open(output_file, "w+") as f:
    json.dump(spec, f, indent=2)

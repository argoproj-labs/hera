"""This small module downloads and adjusts the OpenAPI spec of a given Argo Workflows version."""

import json
import logging
import sys
from typing import Dict, List, Set, Tuple

import requests

logger: logging.Logger = logging.getLogger(__name__)

# get the OpenAPI spec URI from the command line, along with the output file
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
            f"Could not find definition {definition} in Argo specification for OpenAPI URI {open_api_spec_url}, "
            f"caught error: {e}"
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

# these are specifications of objects with fields that are marked to have a union type of IntOrString. However, K8s
# only accepts one or the other, unfortunately. Here, we remap those fields from their respective `$ref`s, which
# contain a specific type, to another type. The mapping is from the `$ref` to a tuple of the existing type and the
# new type. The dictionary model is:
# { object name: { field name: ( ( existing field, existing value ) , ( new field, new value ) ) } }
INT_OR_STRING_FIELD_REMAPPING: Dict[str, Dict[str, Tuple[Tuple[str, str], Tuple[str, str]]]] = {
    "io.k8s.api.core.v1.HTTPGetAction": {
        "port": (
            ("$ref", "#/definitions/io.k8s.apimachinery.pkg.util.intstr.IntOrString"),
            ("type", "integer"),
        ),
    },
}
for obj_name, field in INT_OR_STRING_FIELD_REMAPPING.items():
    try:
        curr_field = spec["definitions"][obj_name]
    except KeyError as e:
        raise KeyError(
            f"Could not find field {obj_name} in Argo specification for OpenAPI URI {open_api_spec_url}, "
            f"caught error: {e}"
        )

    try:
        properties = curr_field["properties"]
    except KeyError as e:
        raise KeyError(
            f"Could not find properties for field {obj_name} in Argo specification for OpenAPI URI "
            f"{open_api_spec_url}, caught error: {e}"
        )

    for property_to_change in field.keys():
        try:
            curr_property = properties[property_to_change]
        except KeyError as e:
            raise KeyError(
                f"Could not find property {property_to_change} for field {obj_name} in Argo specification for "
                f"OpenAPI URI {open_api_spec_url}, caught error: {e}"
            )

        # get the tuple of the existing field and value, and the new field and value
        existing_field, existing_value = field[property_to_change][0]
        new_field, new_value = field[property_to_change][1]

        # check that the existing field and value are the same as the current field and value
        assert curr_property[existing_field] == existing_value, (
            f"Expected to find field {existing_field} with value {existing_value} for property {property_to_change} "
            f"for field {obj_name} in Argo specification for OpenAPI URI {open_api_spec_url}, but found "
            f"{curr_property[existing_field]} instead"
        )

        # change the field and value
        curr_property[new_field] = new_value
        if existing_field != new_field:
            del curr_property[existing_field]

# finally, we write the spec to the output file that is passed to use assuming the client wants to perform
# something with this file
with open(output_file, "w+") as f:
    json.dump(spec, f, indent=2)

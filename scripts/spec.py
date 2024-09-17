"""This small module downloads and adjusts the OpenAPI spec of a given Argo Workflows version."""

import json
import logging
import sys
from typing import Dict, List, Optional, Set, Tuple, Union

import requests
from graphlib import TopologicalSorter

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
# new type. While the first piece of the mapping tuple must be defined the second one is optional - if the second
# part of the tuple is None then the field will be removed. The dictionary model is:
# { object name: { field name: ( ( existing field, existing value ) , ( new field, new value ) ) } }
FIELD_REMAPPINGS: Dict[
    str, Dict[str, Tuple[Tuple[str, Union[str, List[str]]], Optional[Tuple[str, Union[str, List[str]]]]]]
] = {
    "io.k8s.api.core.v1.HTTPGetAction": {
        "port": (
            ("$ref", "#/definitions/io.k8s.apimachinery.pkg.util.intstr.IntOrString"),
            ("type", "integer"),
        ),
    },
    "io.k8s.api.core.v1.Container": {
        "imagePullPolicy": (
            ("enum", None),
            None,
        )
    },
}
for obj_name, field in FIELD_REMAPPINGS.items():
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
        if field[property_to_change][1] is None:
            # if the second one is absent it means we want to delete the existing field
            del curr_property[existing_field]
            continue
        else:
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

# there are also some specifications that have to be introduced manually for backwards compatibility purposes. This
# block allows us to define those specifications and add them to the spec.
MANUAL_SPECIFICATIONS: List[Tuple[str, Dict]] = [
    (
        "io.k8s.api.core.v1.ImagePullPolicy",
        {
            "description": "An enum that contains available image pull policy options.",
            "type": "string",
            "enum": ["Always", "Never", "IfNotPresent"],
        },
    ),
    (
        "io.k8s.apimachinery.pkg.util.intstr.IntOrString",
        {
            "type": ["string", "integer"],
        },
    ),
]
for obj_name, obj_spec in MANUAL_SPECIFICATIONS:
    spec["definitions"][obj_name] = obj_spec


# Reorder spec topologically because pydantic only resolves forward refs to a certain depth (2 by default)
topo_sorter = TopologicalSorter()
prefix_len = len("#/definitions/")

# Create "nodes" for the sorter from definition names and any "properties" that reference other definitions
for definition, metadata in spec["definitions"].items():
    if "properties" not in metadata:
        topo_sorter.add(definition)
        continue

    object_references = []
    for prop, attrs in metadata["properties"].items():
        if "$ref" in attrs:
            object_references.append(attrs["$ref"][prefix_len:])
    topo_sorter.add(definition, *object_references)

# Rebuild definitions as a new dictionary to maintain ordering
ordered_defs = {}
for definition in topo_sorter.static_order():
    ordered_defs[definition] = spec["definitions"][definition]

spec["definitions"] = ordered_defs

# finally, we write the spec to the output file that is passed to use assuming the client wants to perform
# something with this file
with open(output_file, "w+") as f:
    json.dump(spec, f, indent=2)

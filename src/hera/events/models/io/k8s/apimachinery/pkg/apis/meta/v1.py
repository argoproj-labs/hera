# generated by datamodel-codegen:
#   filename:  https://raw.githubusercontent.com/argoproj/argo-workflows/v3.4.4/api/openapi-spec/swagger.json

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import Field

from hera.events._base_model import BaseModel


class CreateOptions(BaseModel):
    dry_run: Optional[List[str]] = Field(
        None,
        alias="dryRun",
        title=(
            "When present, indicates that modifications should not be\npersisted. An invalid or unrecognized dryRun"
            " directive will\nresult in an error response and no further processing of the\nrequest. Valid values"
            " are:\n- All: all dry run stages will be processed\n+optional"
        ),
    )
    field_manager: Optional[str] = Field(
        None,
        alias="fieldManager",
        title=(
            "fieldManager is a name associated with the actor or entity\nthat is making these changes. The value must"
            " be less than or\n128 characters long, and only contain printable characters,\nas defined by"
            " https://golang.org/pkg/unicode/#IsPrint.\n+optional"
        ),
    )
    field_validation: Optional[str] = Field(
        None,
        alias="fieldValidation",
        title=(
            "fieldValidation instructs the server on how to handle\nobjects in the request (POST/PUT/PATCH) containing"
            " unknown\nor duplicate fields, provided that the `ServerSideFieldValidation`\nfeature gate is also"
            " enabled. Valid values are:\n- Ignore: This will ignore any unknown fields that are silently\ndropped"
            " from the object, and will ignore all but the last duplicate\nfield that the decoder encounters. This is"
            " the default behavior\nprior to v1.23 and is the default behavior when the\n`ServerSideFieldValidation`"
            " feature gate is disabled.\n- Warn: This will send a warning via the standard warning response\nheader"
            " for each unknown field that is dropped from the object, and\nfor each duplicate field that is"
            " encountered. The request will\nstill succeed if there are no other errors, and will only persist\nthe"
            " last of any duplicate fields. This is the default when the\n`ServerSideFieldValidation` feature gate is"
            " enabled.\n- Strict: This will fail the request with a BadRequest error if\nany unknown fields would be"
            " dropped from the object, or if any\nduplicate fields are present. The error returned from the"
            " server\nwill contain all unknown and duplicate fields encountered.\n+optional"
        ),
    )


class FieldsV1(BaseModel):
    pass


class GroupVersionResource(BaseModel):
    group: Optional[str] = None
    resource: Optional[str] = None
    version: Optional[str] = None


class LabelSelectorRequirement(BaseModel):
    key: str = Field(..., description="key is the label key that the selector applies to.")
    operator: str = Field(
        ...,
        description=(
            "operator represents a key's relationship to a set of values. Valid operators are In, NotIn, Exists and"
            " DoesNotExist."
        ),
    )
    values: Optional[List[str]] = Field(
        None,
        description=(
            "values is an array of string values. If the operator is In or NotIn, the values array must be non-empty."
            " If the operator is Exists or DoesNotExist, the values array must be empty. This array is replaced during"
            " a strategic merge patch."
        ),
    )


class ListMeta(BaseModel):
    continue_: Optional[str] = Field(
        None,
        alias="continue",
        description=(
            "continue may be set if the user set a limit on the number of items returned, and indicates that the"
            " server has more data available. The value is opaque and may be used to issue another request to the"
            " endpoint that served this list to retrieve the next set of available objects. Continuing a consistent"
            " list may not be possible if the server configuration has changed or more than a few minutes have passed."
            " The resourceVersion field returned when using this continue value will be identical to the value in the"
            " first response, unless you have received this token from an error message."
        ),
    )
    remaining_item_count: Optional[int] = Field(
        None,
        alias="remainingItemCount",
        description=(
            "remainingItemCount is the number of subsequent items in the list which are not included in this list"
            " response. If the list request contained label or field selectors, then the number of remaining items is"
            " unknown and the field will be left unset and omitted during serialization. If the list is complete"
            " (either because it is not chunking or because this is the last chunk), then there are no more remaining"
            " items and this field will be left unset and omitted during serialization. Servers older than v1.15 do"
            " not set this field. The intended use of the remainingItemCount is *estimating* the size of a collection."
            " Clients should not rely on the remainingItemCount to be set or to be exact."
        ),
    )
    resource_version: Optional[str] = Field(
        None,
        alias="resourceVersion",
        description=(
            "String that identifies the server's internal version of this object that can be used by clients to"
            " determine when objects have changed. Value must be treated as opaque by clients and passed unmodified"
            " back to the server. Populated by the system. Read-only. More info:"
            " https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#concurrency-control-and-consistency"
        ),
    )
    self_link: Optional[str] = Field(
        None,
        alias="selfLink",
        description=(
            "selfLink is a URL representing this object. Populated by the system. Read-only.\n\nDEPRECATED Kubernetes"
            " will stop propagating this field in 1.20 release and the field is planned to be removed in 1.21 release."
        ),
    )


class MicroTime(BaseModel):
    __root__: datetime = Field(..., description="MicroTime is version of Time with microsecond level precision.")


class OwnerReference(BaseModel):
    api_version: str = Field(..., alias="apiVersion", description="API version of the referent.")
    block_owner_deletion: Optional[bool] = Field(
        None,
        alias="blockOwnerDeletion",
        description=(
            'If true, AND if the owner has the "foregroundDeletion" finalizer, then the owner cannot be deleted from'
            " the key-value store until this reference is removed. Defaults to false. To set this field, a user needs"
            ' "delete" permission of the owner, otherwise 422 (Unprocessable Entity) will be returned.'
        ),
    )
    controller: Optional[bool] = Field(None, description="If true, this reference points to the managing controller.")
    kind: str = Field(
        ...,
        description=(
            "Kind of the referent. More info:"
            " https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds"
        ),
    )
    name: str = Field(
        ..., description="Name of the referent. More info: http://kubernetes.io/docs/user-guide/identifiers#names"
    )
    uid: str = Field(
        ..., description="UID of the referent. More info: http://kubernetes.io/docs/user-guide/identifiers#uids"
    )


class StatusCause(BaseModel):
    field: Optional[str] = Field(
        None,
        description=(
            "The field of the resource that has caused this error, as named by its JSON serialization. May include dot"
            " and postfix notation for nested attributes. Arrays are zero-indexed.  Fields may appear more than once"
            ' in an array of causes due to fields having multiple errors. Optional.\n\nExamples:\n  "name" - the field'
            ' "name" on the current resource\n  "items[0].name" - the field "name" on the first array entry in "items"'
        ),
    )
    message: Optional[str] = Field(
        None,
        description=(
            "A human-readable description of the cause of the error.  This field may be presented as-is to a reader."
        ),
    )
    reason: Optional[str] = Field(
        None,
        description=(
            "A machine-readable description of the cause of the error. If this value is empty there is no information"
            " available."
        ),
    )


class Time(BaseModel):
    __root__: datetime = Field(
        ...,
        description=(
            "Time is a wrapper around time.Time which supports correct marshaling to YAML and JSON.  Wrappers are"
            " provided for many of the factory methods that the time package offers."
        ),
    )


class LabelSelector(BaseModel):
    match_expressions: Optional[List[LabelSelectorRequirement]] = Field(
        None,
        alias="matchExpressions",
        description="matchExpressions is a list of label selector requirements. The requirements are ANDed.",
    )
    match_labels: Optional[Dict[str, str]] = Field(
        None,
        alias="matchLabels",
        description=(
            "matchLabels is a map of {key,value} pairs. A single {key,value} in the matchLabels map is equivalent to"
            ' an element of matchExpressions, whose key field is "key", the operator is "In", and the values array'
            ' contains only "value". The requirements are ANDed.'
        ),
    )


class ManagedFieldsEntry(BaseModel):
    api_version: Optional[str] = Field(
        None,
        alias="apiVersion",
        description=(
            "APIVersion defines the version of this resource that this field set applies to. The format is"
            ' "group/version" just like the top-level APIVersion field. It is necessary to track the version of a'
            " field set because it cannot be automatically converted."
        ),
    )
    fields_type: Optional[str] = Field(
        None,
        alias="fieldsType",
        description=(
            "FieldsType is the discriminator for the different fields format and version. There is currently only one"
            ' possible value: "FieldsV1"'
        ),
    )
    fields_v1: Optional[FieldsV1] = Field(
        None,
        alias="fieldsV1",
        description='FieldsV1 holds the first JSON version format as described in the "FieldsV1" type.',
    )
    manager: Optional[str] = Field(None, description="Manager is an identifier of the workflow managing these fields.")
    operation: Optional[str] = Field(
        None,
        description=(
            "Operation is the type of operation which lead to this ManagedFieldsEntry being created. The only valid"
            " values for this field are 'Apply' and 'Update'."
        ),
    )
    subresource: Optional[str] = Field(
        None,
        description=(
            "Subresource is the name of the subresource used to update that object, or empty string if the object was"
            " updated through the main resource. The value of this field is used to distinguish between managers, even"
            " if they share the same name. For example, a status update will be distinct from a regular update using"
            " the same manager name. Note that the APIVersion field is not related to the Subresource field and it"
            " always corresponds to the version of the main resource."
        ),
    )
    time: Optional[Time] = Field(
        None,
        description=(
            "Time is timestamp of when these fields were set. It should always be empty if Operation is 'Apply'"
        ),
    )


class ObjectMeta(BaseModel):
    annotations: Optional[Dict[str, str]] = Field(
        None,
        description=(
            "Annotations is an unstructured key value map stored with a resource that may be set by external tools to"
            " store and retrieve arbitrary metadata. They are not queryable and should be preserved when modifying"
            " objects. More info: http://kubernetes.io/docs/user-guide/annotations"
        ),
    )
    cluster_name: Optional[str] = Field(
        None,
        alias="clusterName",
        description=(
            "The name of the cluster which the object belongs to. This is used to distinguish resources with same name"
            " and namespace in different clusters. This field is not set anywhere right now and apiserver is going to"
            " ignore it if set in create or update request."
        ),
    )
    creation_timestamp: Optional[Time] = Field(
        None,
        alias="creationTimestamp",
        description=(
            "CreationTimestamp is a timestamp representing the server time when this object was created. It is not"
            " guaranteed to be set in happens-before order across separate operations. Clients may not set this value."
            " It is represented in RFC3339 form and is in UTC.\n\nPopulated by the system. Read-only. Null for lists."
            " More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#metadata"
        ),
    )
    deletion_grace_period_seconds: Optional[int] = Field(
        None,
        alias="deletionGracePeriodSeconds",
        description=(
            "Number of seconds allowed for this object to gracefully terminate before it will be removed from the"
            " system. Only set when deletionTimestamp is also set. May only be shortened. Read-only."
        ),
    )
    deletion_timestamp: Optional[Time] = Field(
        None,
        alias="deletionTimestamp",
        description=(
            "DeletionTimestamp is RFC 3339 date and time at which this resource will be deleted. This field is set by"
            " the server when a graceful deletion is requested by the user, and is not directly settable by a client."
            " The resource is expected to be deleted (no longer visible from resource lists, and not reachable by"
            " name) after the time in this field, once the finalizers list is empty. As long as the finalizers list"
            " contains items, deletion is blocked. Once the deletionTimestamp is set, this value may not be unset or"
            " be set further into the future, although it may be shortened or the resource may be deleted prior to"
            " this time. For example, a user may request that a pod is deleted in 30 seconds. The Kubelet will react"
            " by sending a graceful termination signal to the containers in the pod. After that 30 seconds, the"
            " Kubelet will send a hard termination signal (SIGKILL) to the container and after cleanup, remove the pod"
            " from the API. In the presence of network partitions, this object may still exist after this timestamp,"
            " until an administrator or automated process can determine the resource is fully terminated. If not set,"
            " graceful deletion of the object has not been requested.\n\nPopulated by the system when a graceful"
            " deletion is requested. Read-only. More info:"
            " https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#metadata"
        ),
    )
    finalizers: Optional[List[str]] = Field(
        None,
        description=(
            "Must be empty before the object is deleted from the registry. Each entry is an identifier for the"
            " responsible component that will remove the entry from the list. If the deletionTimestamp of the object"
            " is non-nil, entries in this list can only be removed. Finalizers may be processed and removed in any"
            " order.  Order is NOT enforced because it introduces significant risk of stuck finalizers. finalizers is"
            " a shared field, any actor with permission can reorder it. If the finalizer list is processed in order,"
            " then this can lead to a situation in which the component responsible for the first finalizer in the list"
            " is waiting for a signal (field value, external system, or other) produced by a component responsible for"
            " a finalizer later in the list, resulting in a deadlock. Without enforced ordering finalizers are free to"
            " order amongst themselves and are not vulnerable to ordering changes in the list."
        ),
    )
    generate_name: Optional[str] = Field(
        None,
        alias="generateName",
        description=(
            "GenerateName is an optional prefix, used by the server, to generate a unique name ONLY IF the Name field"
            " has not been provided. If this field is used, the name returned to the client will be different than the"
            " name passed. This value will also be combined with a unique suffix. The provided value has the same"
            " validation rules as the Name field, and may be truncated by the length of the suffix required to make"
            " the value unique on the server.\n\nIf this field is specified and the generated name exists, the server"
            " will NOT return a 409 - instead, it will either return 201 Created or 500 with Reason ServerTimeout"
            " indicating a unique name could not be found in the time allotted, and the client should retry"
            " (optionally after the time indicated in the Retry-After header).\n\nApplied only if Name is not"
            " specified. More info:"
            " https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#idempotency"
        ),
    )
    generation: Optional[int] = Field(
        None,
        description=(
            "A sequence number representing a specific generation of the desired state. Populated by the system."
            " Read-only."
        ),
    )
    labels: Optional[Dict[str, str]] = Field(
        None,
        description=(
            "Map of string keys and values that can be used to organize and categorize (scope and select) objects. May"
            " match selectors of replication controllers and services. More info:"
            " http://kubernetes.io/docs/user-guide/labels"
        ),
    )
    managed_fields: Optional[List[ManagedFieldsEntry]] = Field(
        None,
        alias="managedFields",
        description=(
            "ManagedFields maps workflow-id and version to the set of fields that are managed by that workflow. This"
            " is mostly for internal housekeeping, and users typically shouldn't need to set or understand this"
            " field. A workflow can be the user's name, a controller's name, or the name of a specific apply path"
            ' like "ci-cd". The set of fields is always in the version that the workflow used when modifying the'
            " object."
        ),
    )
    name: Optional[str] = Field(
        None,
        description=(
            "Name must be unique within a namespace. Is required when creating resources, although some resources may"
            " allow a client to request the generation of an appropriate name automatically. Name is primarily"
            " intended for creation idempotence and configuration definition. Cannot be updated. More info:"
            " http://kubernetes.io/docs/user-guide/identifiers#names"
        ),
    )
    namespace: Optional[str] = Field(
        None,
        description=(
            "Namespace defines the space within which each name must be unique. An empty namespace is equivalent to"
            ' the "default" namespace, but "default" is the canonical representation. Not all objects are required to'
            " be scoped to a namespace - the value of this field for those objects will be empty.\n\nMust be a"
            " DNS_LABEL. Cannot be updated. More info: http://kubernetes.io/docs/user-guide/namespaces"
        ),
    )
    owner_references: Optional[List[OwnerReference]] = Field(
        None,
        alias="ownerReferences",
        description=(
            "List of objects depended by this object. If ALL objects in the list have been deleted, this object will"
            " be garbage collected. If this object is managed by a controller, then an entry in this list will point"
            " to this controller, with the controller field set to true. There cannot be more than one managing"
            " controller."
        ),
    )
    resource_version: Optional[str] = Field(
        None,
        alias="resourceVersion",
        description=(
            "An opaque value that represents the internal version of this object that can be used by clients to"
            " determine when objects have changed. May be used for optimistic concurrency, change detection, and the"
            " watch operation on a resource or set of resources. Clients must treat these values as opaque and passed"
            " unmodified back to the server. They may only be valid for a particular resource or set of"
            " resources.\n\nPopulated by the system. Read-only. Value must be treated as opaque by clients and . More"
            " info:"
            " https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#concurrency-control-and-consistency"
        ),
    )
    self_link: Optional[str] = Field(
        None,
        alias="selfLink",
        description=(
            "SelfLink is a URL representing this object. Populated by the system. Read-only.\n\nDEPRECATED Kubernetes"
            " will stop propagating this field in 1.20 release and the field is planned to be removed in 1.21 release."
        ),
    )
    uid: Optional[str] = Field(
        None,
        description=(
            "UID is the unique in time and space value for this object. It is typically generated by the server on"
            " successful creation of a resource and is not allowed to change on PUT operations.\n\nPopulated by the"
            " system. Read-only. More info: http://kubernetes.io/docs/user-guide/identifiers#uids"
        ),
    )

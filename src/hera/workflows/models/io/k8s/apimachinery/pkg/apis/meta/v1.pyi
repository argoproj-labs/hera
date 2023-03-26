from datetime import datetime
from typing import Dict, List, Optional

from hera.shared._base_model import BaseModel as BaseModel

class CreateOptions(BaseModel):
    dry_run: Optional[List[str]]
    field_manager: Optional[str]
    field_validation: Optional[str]

class FieldsV1(BaseModel): ...

class GroupVersionResource(BaseModel):
    group: Optional[str]
    resource: Optional[str]
    version: Optional[str]

class LabelSelectorRequirement(BaseModel):
    key: str
    operator: str
    values: Optional[List[str]]

class ListMeta(BaseModel):
    continue_: Optional[str]
    remaining_item_count: Optional[int]
    resource_version: Optional[str]
    self_link: Optional[str]

class MicroTime(BaseModel):
    __root__: datetime

class OwnerReference(BaseModel):
    api_version: str
    block_owner_deletion: Optional[bool]
    controller: Optional[bool]
    kind: str
    name: str
    uid: str

class StatusCause(BaseModel):
    field: Optional[str]
    message: Optional[str]
    reason: Optional[str]

class Time(BaseModel):
    __root__: datetime

class LabelSelector(BaseModel):
    match_expressions: Optional[List[LabelSelectorRequirement]]
    match_labels: Optional[Dict[str, str]]

class ManagedFieldsEntry(BaseModel):
    api_version: Optional[str]
    fields_type: Optional[str]
    fields_v1: Optional[FieldsV1]
    manager: Optional[str]
    operation: Optional[str]
    subresource: Optional[str]
    time: Optional[Time]

class ObjectMeta(BaseModel):
    annotations: Optional[Dict[str, str]]
    cluster_name: Optional[str]
    creation_timestamp: Optional[Time]
    deletion_grace_period_seconds: Optional[int]
    deletion_timestamp: Optional[Time]
    finalizers: Optional[List[str]]
    generate_name: Optional[str]
    generation: Optional[int]
    labels: Optional[Dict[str, str]]
    managed_fields: Optional[List[ManagedFieldsEntry]]
    name: Optional[str]
    namespace: Optional[str]
    owner_references: Optional[List[OwnerReference]]
    resource_version: Optional[str]
    self_link: Optional[str]
    uid: Optional[str]

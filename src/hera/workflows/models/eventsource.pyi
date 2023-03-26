from typing import Optional

from hera.shared._base_model import BaseModel as BaseModel

from .io.argoproj.events import v1alpha1 as v1alpha1
from .io.k8s.apimachinery.pkg.apis.meta import v1 as v1

class EventSourceDeletedResponse(BaseModel): ...

class LogEntry(BaseModel):
    event_name: Optional[str]
    event_source_name: Optional[str]
    event_source_type: Optional[str]
    level: Optional[str]
    msg: Optional[str]
    namespace: Optional[str]
    time: Optional[v1.Time]

class CreateEventSourceRequest(BaseModel):
    event_source: Optional[v1alpha1.EventSource]
    namespace: Optional[str]

class EventSourceWatchEvent(BaseModel):
    object: Optional[v1alpha1.EventSource]
    type: Optional[str]

class UpdateEventSourceRequest(BaseModel):
    event_source: Optional[v1alpha1.EventSource]
    name: Optional[str]
    namespace: Optional[str]

from typing import Optional

from hera.shared._base_model import BaseModel as BaseModel

from .io.argoproj.events import v1alpha1 as v1alpha1
from .io.k8s.apimachinery.pkg.apis.meta import v1 as v1

class DeleteSensorResponse(BaseModel): ...

class LogEntry(BaseModel):
    dependency_name: Optional[str]
    event_context: Optional[str]
    level: Optional[str]
    msg: Optional[str]
    namespace: Optional[str]
    sensor_name: Optional[str]
    time: Optional[v1.Time]
    trigger_name: Optional[str]

class CreateSensorRequest(BaseModel):
    create_options: Optional[v1.CreateOptions]
    namespace: Optional[str]
    sensor: Optional[v1alpha1.Sensor]

class SensorWatchEvent(BaseModel):
    object: Optional[v1alpha1.Sensor]
    type: Optional[str]

class UpdateSensorRequest(BaseModel):
    name: Optional[str]
    namespace: Optional[str]
    sensor: Optional[v1alpha1.Sensor]

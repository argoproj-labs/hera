# generated by datamodel-codegen:
#   filename:  argo-workflows-3.6.2.json

from __future__ import annotations

from typing import Annotated, Optional

from hera.shared._pydantic import BaseModel, Field

from .io.argoproj.events import v1alpha1
from .io.k8s.apimachinery.pkg.apis.meta import v1


class DeleteSensorResponse(BaseModel):
    pass


class LogEntry(BaseModel):
    dependency_name: Annotated[
        Optional[str],
        Field(alias="dependencyName", title="optional - trigger dependency name"),
    ] = None
    event_context: Annotated[
        Optional[str],
        Field(alias="eventContext", title="optional - Cloud Event context"),
    ] = None
    level: Optional[str] = None
    msg: Optional[str] = None
    namespace: Optional[str] = None
    sensor_name: Annotated[Optional[str], Field(alias="sensorName")] = None
    time: Optional[v1.Time] = None
    trigger_name: Annotated[Optional[str], Field(alias="triggerName", title="optional - any trigger name")] = None


class CreateSensorRequest(BaseModel):
    create_options: Annotated[Optional[v1.CreateOptions], Field(alias="createOptions")] = None
    namespace: Optional[str] = None
    sensor: Optional[v1alpha1.Sensor] = None


class SensorWatchEvent(BaseModel):
    object: Optional[v1alpha1.Sensor] = None
    type: Optional[str] = None


class UpdateSensorRequest(BaseModel):
    name: Optional[str] = None
    namespace: Optional[str] = None
    sensor: Optional[v1alpha1.Sensor] = None

from typing import Optional, cast
from urllib.parse import urljoin

import requests

from hera.events.models import (
    CreateEventSourceRequest,
    CreateSensorRequest,
    DeleteSensorResponse,
    Event,
    EventResponse,
    EventSource,
    EventSourceDeletedResponse,
    EventSourceList,
    EventsourceLogEntry,
    EventSourceWatchEvent,
    GetUserInfoResponse,
    InfoResponse,
    Item,
    Sensor,
    SensorList,
    SensorLogEntry,
    SensorWatchEvent,
    UpdateEventSourceRequest,
    UpdateSensorRequest,
    Version,
)
from hera.exceptions import exception_from_server_response
from hera.shared import global_config


def valid_host_scheme(host: str) -> bool:
    return host.startswith("http://") or host.startswith("https://")


class EventsService:
    def __init__(
        self,
        host: Optional[str] = None,
        verify_ssl: Optional[bool] = None,
        token: Optional[str] = None,
        namespace: Optional[str] = None,
    ):
        self.host = cast(str, host or global_config.host)
        self.verify_ssl = verify_ssl if verify_ssl is not None else global_config.verify_ssl
        self.token = token or global_config.token
        self.namespace = namespace or global_config.namespace

    def list_event_sources(
        self,
        namespace: Optional[str] = None,
        label_selector: Optional[str] = None,
        field_selector: Optional[str] = None,
        watch: Optional[bool] = None,
        allow_watch_bookmarks: Optional[bool] = None,
        resource_version: Optional[str] = None,
        resource_version_match: Optional[str] = None,
        timeout_seconds: Optional[str] = None,
        limit: Optional[str] = None,
        continue_: Optional[str] = None,
    ) -> EventSourceList:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.get(
            url=urljoin(self.host, "api/v1/event-sources/{namespace}").format(
                namespace=namespace if namespace is not None else self.namespace
            ),
            params={
                "listOptions.labelSelector": label_selector,
                "listOptions.fieldSelector": field_selector,
                "listOptions.watch": watch,
                "listOptions.allowWatchBookmarks": allow_watch_bookmarks,
                "listOptions.resourceVersion": resource_version,
                "listOptions.resourceVersionMatch": resource_version_match,
                "listOptions.timeoutSeconds": timeout_seconds,
                "listOptions.limit": limit,
                "listOptions.continue": continue_,
            },
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        )

        if resp.ok:
            return EventSourceList(**resp.json())

        raise exception_from_server_response(resp)

    def create_event_source(self, req: CreateEventSourceRequest, namespace: Optional[str] = None) -> EventSource:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.post(
            url=urljoin(self.host, "api/v1/event-sources/{namespace}").format(
                namespace=namespace if namespace is not None else self.namespace
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(
                exclude_none=True, by_alias=True, skip_defaults=True, exclude_unset=True, exclude_defaults=True
            ),
            verify=self.verify_ssl,
        )

        if resp.ok:
            return EventSource(**resp.json())

        raise exception_from_server_response(resp)

    def get_event_source(self, name: str, namespace: Optional[str] = None) -> EventSource:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.get(
            url=urljoin(self.host, "api/v1/event-sources/{namespace}/{name}").format(
                name=name, namespace=namespace if namespace is not None else self.namespace
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        )

        if resp.ok:
            return EventSource(**resp.json())

        raise exception_from_server_response(resp)

    def update_event_source(
        self, name: str, req: UpdateEventSourceRequest, namespace: Optional[str] = None
    ) -> EventSource:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.put(
            url=urljoin(self.host, "api/v1/event-sources/{namespace}/{name}").format(
                name=name, namespace=namespace if namespace is not None else self.namespace
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(
                exclude_none=True, by_alias=True, skip_defaults=True, exclude_unset=True, exclude_defaults=True
            ),
            verify=self.verify_ssl,
        )

        if resp.ok:
            return EventSource(**resp.json())

        raise exception_from_server_response(resp)

    def delete_event_source(
        self,
        name: str,
        namespace: Optional[str] = None,
        grace_period_seconds: Optional[str] = None,
        uid: Optional[str] = None,
        resource_version: Optional[str] = None,
        orphan_dependents: Optional[bool] = None,
        propagation_policy: Optional[str] = None,
        dry_run: Optional[list] = None,
    ) -> EventSourceDeletedResponse:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.delete(
            url=urljoin(self.host, "api/v1/event-sources/{namespace}/{name}").format(
                name=name, namespace=namespace if namespace is not None else self.namespace
            ),
            params={
                "deleteOptions.gracePeriodSeconds": grace_period_seconds,
                "deleteOptions.preconditions.uid": uid,
                "deleteOptions.preconditions.resourceVersion": resource_version,
                "deleteOptions.orphanDependents": orphan_dependents,
                "deleteOptions.propagationPolicy": propagation_policy,
                "deleteOptions.dryRun": dry_run,
            },
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        )

        if resp.ok:
            return EventSourceDeletedResponse()

        raise exception_from_server_response(resp)

    def receive_event(self, discriminator: str, req: Item, namespace: Optional[str] = None) -> EventResponse:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.post(
            url=urljoin(self.host, "api/v1/events/{namespace}/{discriminator}").format(
                discriminator=discriminator, namespace=namespace if namespace is not None else self.namespace
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(
                exclude_none=True, by_alias=True, skip_defaults=True, exclude_unset=True, exclude_defaults=True
            ),
            verify=self.verify_ssl,
        )

        if resp.ok:
            return EventResponse()

        raise exception_from_server_response(resp)

    def get_info(self) -> InfoResponse:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.get(
            url=urljoin(self.host, "api/v1/info"),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        )

        if resp.ok:
            return InfoResponse()

        raise exception_from_server_response(resp)

    def list_sensors(
        self,
        namespace: Optional[str] = None,
        label_selector: Optional[str] = None,
        field_selector: Optional[str] = None,
        watch: Optional[bool] = None,
        allow_watch_bookmarks: Optional[bool] = None,
        resource_version: Optional[str] = None,
        resource_version_match: Optional[str] = None,
        timeout_seconds: Optional[str] = None,
        limit: Optional[str] = None,
        continue_: Optional[str] = None,
    ) -> SensorList:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.get(
            url=urljoin(self.host, "api/v1/sensors/{namespace}").format(
                namespace=namespace if namespace is not None else self.namespace
            ),
            params={
                "listOptions.labelSelector": label_selector,
                "listOptions.fieldSelector": field_selector,
                "listOptions.watch": watch,
                "listOptions.allowWatchBookmarks": allow_watch_bookmarks,
                "listOptions.resourceVersion": resource_version,
                "listOptions.resourceVersionMatch": resource_version_match,
                "listOptions.timeoutSeconds": timeout_seconds,
                "listOptions.limit": limit,
                "listOptions.continue": continue_,
            },
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        )

        if resp.ok:
            return SensorList(**resp.json())

        raise exception_from_server_response(resp)

    def create_sensor(self, req: CreateSensorRequest, namespace: Optional[str] = None) -> Sensor:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.post(
            url=urljoin(self.host, "api/v1/sensors/{namespace}").format(
                namespace=namespace if namespace is not None else self.namespace
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(
                exclude_none=True, by_alias=True, skip_defaults=True, exclude_unset=True, exclude_defaults=True
            ),
            verify=self.verify_ssl,
        )

        if resp.ok:
            return Sensor(**resp.json())

        raise exception_from_server_response(resp)

    def get_sensor(self, name: str, namespace: Optional[str] = None, resource_version: Optional[str] = None) -> Sensor:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.get(
            url=urljoin(self.host, "api/v1/sensors/{namespace}/{name}").format(
                name=name, namespace=namespace if namespace is not None else self.namespace
            ),
            params={"getOptions.resourceVersion": resource_version},
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        )

        if resp.ok:
            return Sensor(**resp.json())

        raise exception_from_server_response(resp)

    def update_sensor(self, name: str, req: UpdateSensorRequest, namespace: Optional[str] = None) -> Sensor:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.put(
            url=urljoin(self.host, "api/v1/sensors/{namespace}/{name}").format(
                name=name, namespace=namespace if namespace is not None else self.namespace
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(
                exclude_none=True, by_alias=True, skip_defaults=True, exclude_unset=True, exclude_defaults=True
            ),
            verify=self.verify_ssl,
        )

        if resp.ok:
            return Sensor(**resp.json())

        raise exception_from_server_response(resp)

    def delete_sensor(
        self,
        name: str,
        namespace: Optional[str] = None,
        grace_period_seconds: Optional[str] = None,
        uid: Optional[str] = None,
        resource_version: Optional[str] = None,
        orphan_dependents: Optional[bool] = None,
        propagation_policy: Optional[str] = None,
        dry_run: Optional[list] = None,
    ) -> DeleteSensorResponse:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.delete(
            url=urljoin(self.host, "api/v1/sensors/{namespace}/{name}").format(
                name=name, namespace=namespace if namespace is not None else self.namespace
            ),
            params={
                "deleteOptions.gracePeriodSeconds": grace_period_seconds,
                "deleteOptions.preconditions.uid": uid,
                "deleteOptions.preconditions.resourceVersion": resource_version,
                "deleteOptions.orphanDependents": orphan_dependents,
                "deleteOptions.propagationPolicy": propagation_policy,
                "deleteOptions.dryRun": dry_run,
            },
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        )

        if resp.ok:
            return DeleteSensorResponse()

        raise exception_from_server_response(resp)

    def watch_event_sources(
        self,
        namespace: Optional[str] = None,
        label_selector: Optional[str] = None,
        field_selector: Optional[str] = None,
        watch: Optional[bool] = None,
        allow_watch_bookmarks: Optional[bool] = None,
        resource_version: Optional[str] = None,
        resource_version_match: Optional[str] = None,
        timeout_seconds: Optional[str] = None,
        limit: Optional[str] = None,
        continue_: Optional[str] = None,
    ) -> EventSourceWatchEvent:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.get(
            url=urljoin(self.host, "api/v1/stream/event-sources/{namespace}").format(
                namespace=namespace if namespace is not None else self.namespace
            ),
            params={
                "listOptions.labelSelector": label_selector,
                "listOptions.fieldSelector": field_selector,
                "listOptions.watch": watch,
                "listOptions.allowWatchBookmarks": allow_watch_bookmarks,
                "listOptions.resourceVersion": resource_version,
                "listOptions.resourceVersionMatch": resource_version_match,
                "listOptions.timeoutSeconds": timeout_seconds,
                "listOptions.limit": limit,
                "listOptions.continue": continue_,
            },
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        )

        if resp.ok:
            return EventSourceWatchEvent(**resp.json())

        raise exception_from_server_response(resp)

    def event_sources_logs(
        self,
        namespace: Optional[str] = None,
        name: Optional[str] = None,
        event_source_type: Optional[str] = None,
        event_name: Optional[str] = None,
        grep: Optional[str] = None,
        container: Optional[str] = None,
        follow: Optional[bool] = None,
        previous: Optional[bool] = None,
        since_seconds: Optional[str] = None,
        seconds: Optional[str] = None,
        nanos: Optional[int] = None,
        timestamps: Optional[bool] = None,
        tail_lines: Optional[str] = None,
        limit_bytes: Optional[str] = None,
        insecure_skip_tls_verify_backend: Optional[bool] = None,
    ) -> EventsourceLogEntry:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.get(
            url=urljoin(self.host, "api/v1/stream/event-sources/{namespace}/logs").format(
                namespace=namespace if namespace is not None else self.namespace
            ),
            params={
                "name": name,
                "eventSourceType": event_source_type,
                "eventName": event_name,
                "grep": grep,
                "podLogOptions.container": container,
                "podLogOptions.follow": follow,
                "podLogOptions.previous": previous,
                "podLogOptions.sinceSeconds": since_seconds,
                "podLogOptions.sinceTime.seconds": seconds,
                "podLogOptions.sinceTime.nanos": nanos,
                "podLogOptions.timestamps": timestamps,
                "podLogOptions.tailLines": tail_lines,
                "podLogOptions.limitBytes": limit_bytes,
                "podLogOptions.insecureSkipTLSVerifyBackend": insecure_skip_tls_verify_backend,
            },
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        )

        if resp.ok:
            return EventsourceLogEntry(**resp.json())

        raise exception_from_server_response(resp)

    def watch_events(
        self,
        namespace: Optional[str] = None,
        label_selector: Optional[str] = None,
        field_selector: Optional[str] = None,
        watch: Optional[bool] = None,
        allow_watch_bookmarks: Optional[bool] = None,
        resource_version: Optional[str] = None,
        resource_version_match: Optional[str] = None,
        timeout_seconds: Optional[str] = None,
        limit: Optional[str] = None,
        continue_: Optional[str] = None,
    ) -> Event:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.get(
            url=urljoin(self.host, "api/v1/stream/events/{namespace}").format(
                namespace=namespace if namespace is not None else self.namespace
            ),
            params={
                "listOptions.labelSelector": label_selector,
                "listOptions.fieldSelector": field_selector,
                "listOptions.watch": watch,
                "listOptions.allowWatchBookmarks": allow_watch_bookmarks,
                "listOptions.resourceVersion": resource_version,
                "listOptions.resourceVersionMatch": resource_version_match,
                "listOptions.timeoutSeconds": timeout_seconds,
                "listOptions.limit": limit,
                "listOptions.continue": continue_,
            },
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        )

        if resp.ok:
            return Event(**resp.json())

        raise exception_from_server_response(resp)

    def watch_sensors(
        self,
        namespace: Optional[str] = None,
        label_selector: Optional[str] = None,
        field_selector: Optional[str] = None,
        watch: Optional[bool] = None,
        allow_watch_bookmarks: Optional[bool] = None,
        resource_version: Optional[str] = None,
        resource_version_match: Optional[str] = None,
        timeout_seconds: Optional[str] = None,
        limit: Optional[str] = None,
        continue_: Optional[str] = None,
    ) -> SensorWatchEvent:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.get(
            url=urljoin(self.host, "api/v1/stream/sensors/{namespace}").format(
                namespace=namespace if namespace is not None else self.namespace
            ),
            params={
                "listOptions.labelSelector": label_selector,
                "listOptions.fieldSelector": field_selector,
                "listOptions.watch": watch,
                "listOptions.allowWatchBookmarks": allow_watch_bookmarks,
                "listOptions.resourceVersion": resource_version,
                "listOptions.resourceVersionMatch": resource_version_match,
                "listOptions.timeoutSeconds": timeout_seconds,
                "listOptions.limit": limit,
                "listOptions.continue": continue_,
            },
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        )

        if resp.ok:
            return SensorWatchEvent(**resp.json())

        raise exception_from_server_response(resp)

    def sensors_logs(
        self,
        namespace: Optional[str] = None,
        name: Optional[str] = None,
        trigger_name: Optional[str] = None,
        grep: Optional[str] = None,
        container: Optional[str] = None,
        follow: Optional[bool] = None,
        previous: Optional[bool] = None,
        since_seconds: Optional[str] = None,
        seconds: Optional[str] = None,
        nanos: Optional[int] = None,
        timestamps: Optional[bool] = None,
        tail_lines: Optional[str] = None,
        limit_bytes: Optional[str] = None,
        insecure_skip_tls_verify_backend: Optional[bool] = None,
    ) -> SensorLogEntry:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.get(
            url=urljoin(self.host, "api/v1/stream/sensors/{namespace}/logs").format(
                namespace=namespace if namespace is not None else self.namespace
            ),
            params={
                "name": name,
                "triggerName": trigger_name,
                "grep": grep,
                "podLogOptions.container": container,
                "podLogOptions.follow": follow,
                "podLogOptions.previous": previous,
                "podLogOptions.sinceSeconds": since_seconds,
                "podLogOptions.sinceTime.seconds": seconds,
                "podLogOptions.sinceTime.nanos": nanos,
                "podLogOptions.timestamps": timestamps,
                "podLogOptions.tailLines": tail_lines,
                "podLogOptions.limitBytes": limit_bytes,
                "podLogOptions.insecureSkipTLSVerifyBackend": insecure_skip_tls_verify_backend,
            },
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        )

        if resp.ok:
            return SensorLogEntry(**resp.json())

        raise exception_from_server_response(resp)

    def get_user_info(self) -> GetUserInfoResponse:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.get(
            url=urljoin(self.host, "api/v1/userinfo"),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        )

        if resp.ok:
            return GetUserInfoResponse()

        raise exception_from_server_response(resp)

    def get_version(self) -> Version:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.get(
            url=urljoin(self.host, "api/v1/version"),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        )

        if resp.ok:
            return Version(**resp.json())

        raise exception_from_server_response(resp)

    def get_artifact_file(
        self,
        id_discriminator: str,
        id_: str,
        node_id: str,
        artifact_name: str,
        artifact_discriminator: str,
        namespace: Optional[str] = None,
    ) -> str:
        """Get an artifact."""
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.get(
            url=urljoin(
                self.host,
                "artifact-files/{namespace}/{idDiscriminator}/{id}/{nodeId}/{artifactDiscriminator}/{artifactName}",
            ).format(
                idDiscriminator=id_discriminator,
                id=id_,
                nodeId=node_id,
                artifactName=artifact_name,
                artifactDiscriminator=artifact_discriminator,
                namespace=namespace if namespace is not None else self.namespace,
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        )

        if resp.ok:
            return str(resp.content)

        raise exception_from_server_response(resp)

    def get_output_artifact_by_uid(self, uid: str, node_id: str, artifact_name: str) -> str:
        """Get an output artifact by UID."""
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.get(
            url=urljoin(self.host, "artifacts-by-uid/{uid}/{nodeId}/{artifactName}").format(
                uid=uid, nodeId=node_id, artifactName=artifact_name
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        )

        if resp.ok:
            return str(resp.content)

        raise exception_from_server_response(resp)

    def get_output_artifact(self, name: str, node_id: str, artifact_name: str, namespace: Optional[str] = None) -> str:
        """Get an output artifact."""
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.get(
            url=urljoin(self.host, "artifacts/{namespace}/{name}/{nodeId}/{artifactName}").format(
                name=name,
                nodeId=node_id,
                artifactName=artifact_name,
                namespace=namespace if namespace is not None else self.namespace,
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        )

        if resp.ok:
            return str(resp.content)

        raise exception_from_server_response(resp)

    def get_input_artifact_by_uid(self, uid: str, node_id: str, artifact_name: str) -> str:
        """Get an input artifact by UID."""
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.get(
            url=urljoin(self.host, "input-artifacts-by-uid/{uid}/{nodeId}/{artifactName}").format(
                uid=uid, nodeId=node_id, artifactName=artifact_name
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        )

        if resp.ok:
            return str(resp.content)

        raise exception_from_server_response(resp)

    def get_input_artifact(self, name: str, node_id: str, artifact_name: str, namespace: Optional[str] = None) -> str:
        """Get an input artifact."""
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.get(
            url=urljoin(self.host, "input-artifacts/{namespace}/{name}/{nodeId}/{artifactName}").format(
                name=name,
                nodeId=node_id,
                artifactName=artifact_name,
                namespace=namespace if namespace is not None else self.namespace,
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        )

        if resp.ok:
            return str(resp.content)

        raise exception_from_server_response(resp)


__all__ = ["EventsService"]

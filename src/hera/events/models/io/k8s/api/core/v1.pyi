from enum import Enum
from typing import Dict, List, Optional

from hera.shared._base_model import BaseModel as BaseModel

from ...apimachinery.pkg.api import resource as resource
from ...apimachinery.pkg.apis.meta import v1 as v1
from ...apimachinery.pkg.util import intstr as intstr

class AWSElasticBlockStoreVolumeSource(BaseModel):
    fs_type: Optional[str]
    partition: Optional[int]
    read_only: Optional[bool]
    volume_id: str

class AzureDiskVolumeSource(BaseModel):
    caching_mode: Optional[str]
    disk_name: str
    disk_uri: str
    fs_type: Optional[str]
    kind: Optional[str]
    read_only: Optional[bool]

class AzureFileVolumeSource(BaseModel):
    read_only: Optional[bool]
    secret_name: str
    share_name: str

class Capabilities(BaseModel):
    add: Optional[List[str]]
    drop: Optional[List[str]]

class ConfigMapEnvSource(BaseModel):
    name: Optional[str]
    optional: Optional[bool]

class ConfigMapKeySelector(BaseModel):
    key: str
    name: Optional[str]
    optional: Optional[bool]

class ImagePullPolicy(Enum):
    always: str
    if_not_present: str
    never: str

class TerminationMessagePolicy(Enum):
    fallback_to_logs_on_error: str
    file: str

class Protocol(Enum):
    sctp: str
    tcp: str
    udp: str

class ContainerPort(BaseModel):
    container_port: int
    host_ip: Optional[str]
    host_port: Optional[int]
    name: Optional[str]
    protocol: Optional[Protocol]

class EventSource(BaseModel):
    component: Optional[str]
    host: Optional[str]

class ExecAction(BaseModel):
    command: Optional[List[str]]

class FCVolumeSource(BaseModel):
    fs_type: Optional[str]
    lun: Optional[int]
    read_only: Optional[bool]
    target_ww_ns: Optional[List[str]]
    wwids: Optional[List[str]]

class FlockerVolumeSource(BaseModel):
    dataset_name: Optional[str]
    dataset_uuid: Optional[str]

class GCEPersistentDiskVolumeSource(BaseModel):
    fs_type: Optional[str]
    partition: Optional[int]
    pd_name: str
    read_only: Optional[bool]

class GRPCAction(BaseModel):
    port: int
    service: Optional[str]

class GitRepoVolumeSource(BaseModel):
    directory: Optional[str]
    repository: str
    revision: Optional[str]

class GlusterfsVolumeSource(BaseModel):
    endpoints: str
    path: str
    read_only: Optional[bool]

class Scheme(Enum):
    http: str
    https: str

class HTTPHeader(BaseModel):
    name: str
    value: str

class HostAlias(BaseModel):
    hostnames: Optional[List[str]]
    ip: Optional[str]

class HostPathVolumeSource(BaseModel):
    path: str
    type: Optional[str]

class KeyToPath(BaseModel):
    key: str
    mode: Optional[int]
    path: str

class LocalObjectReference(BaseModel):
    name: Optional[str]

class NFSVolumeSource(BaseModel):
    path: str
    read_only: Optional[bool]
    server: str

class Operator(Enum):
    does_not_exist: str
    exists: str
    gt: str
    in_: str
    lt: str
    not_in: str

class NodeSelectorRequirement(BaseModel):
    key: str
    operator: Operator
    values: Optional[List[str]]

class NodeSelectorTerm(BaseModel):
    match_expressions: Optional[List[NodeSelectorRequirement]]
    match_fields: Optional[List[NodeSelectorRequirement]]

class ObjectFieldSelector(BaseModel):
    api_version: Optional[str]
    field_path: str

class ObjectReference(BaseModel):
    api_version: Optional[str]
    field_path: Optional[str]
    kind: Optional[str]
    name: Optional[str]
    namespace: Optional[str]
    resource_version: Optional[str]
    uid: Optional[str]

class Type(Enum):
    file_system_resize_pending: str
    resizing: str

class Phase(Enum):
    bound: str
    lost: str
    pending: str

class PersistentVolumeClaimVolumeSource(BaseModel):
    claim_name: str
    read_only: Optional[bool]

class PhotonPersistentDiskVolumeSource(BaseModel):
    fs_type: Optional[str]
    pd_id: str

class PodDNSConfigOption(BaseModel):
    name: Optional[str]
    value: Optional[str]

class PortworxVolumeSource(BaseModel):
    fs_type: Optional[str]
    read_only: Optional[bool]
    volume_id: str

class PreferredSchedulingTerm(BaseModel):
    preference: NodeSelectorTerm
    weight: int

class QuobyteVolumeSource(BaseModel):
    group: Optional[str]
    read_only: Optional[bool]
    registry: str
    tenant: Optional[str]
    user: Optional[str]
    volume: str

class RBDVolumeSource(BaseModel):
    fs_type: Optional[str]
    image: str
    keyring: Optional[str]
    monitors: List[str]
    pool: Optional[str]
    read_only: Optional[bool]
    secret_ref: Optional[LocalObjectReference]
    user: Optional[str]

class SELinuxOptions(BaseModel):
    level: Optional[str]
    role: Optional[str]
    type: Optional[str]
    user: Optional[str]

class ScaleIOVolumeSource(BaseModel):
    fs_type: Optional[str]
    gateway: str
    protection_domain: Optional[str]
    read_only: Optional[bool]
    secret_ref: LocalObjectReference
    ssl_enabled: Optional[bool]
    storage_mode: Optional[str]
    storage_pool: Optional[str]
    system: str
    volume_name: Optional[str]

class TypeModel(Enum):
    localhost: str
    runtime_default: str
    unconfined: str

class SeccompProfile(BaseModel):
    localhost_profile: Optional[str]
    type: TypeModel

class SecretEnvSource(BaseModel):
    name: Optional[str]
    optional: Optional[bool]

class SecretKeySelector(BaseModel):
    key: str
    name: Optional[str]
    optional: Optional[bool]

class SecretProjection(BaseModel):
    items: Optional[List[KeyToPath]]
    name: Optional[str]
    optional: Optional[bool]

class SecretVolumeSource(BaseModel):
    default_mode: Optional[int]
    items: Optional[List[KeyToPath]]
    optional: Optional[bool]
    secret_name: Optional[str]

class ServiceAccountTokenProjection(BaseModel):
    audience: Optional[str]
    expiration_seconds: Optional[int]
    path: str

class StorageOSVolumeSource(BaseModel):
    fs_type: Optional[str]
    read_only: Optional[bool]
    secret_ref: Optional[LocalObjectReference]
    volume_name: Optional[str]
    volume_namespace: Optional[str]

class Sysctl(BaseModel):
    name: str
    value: str

class Effect(Enum):
    no_execute: str
    no_schedule: str
    prefer_no_schedule: str

class OperatorModel(Enum):
    equal: str
    exists: str

class Toleration(BaseModel):
    effect: Optional[Effect]
    key: Optional[str]
    operator: Optional[OperatorModel]
    toleration_seconds: Optional[int]
    value: Optional[str]

class TypedLocalObjectReference(BaseModel):
    api_group: Optional[str]
    kind: str
    name: str

class VolumeDevice(BaseModel):
    device_path: str
    name: str

class VolumeMount(BaseModel):
    mount_path: str
    mount_propagation: Optional[str]
    name: str
    read_only: Optional[bool]
    sub_path: Optional[str]
    sub_path_expr: Optional[str]

class VsphereVirtualDiskVolumeSource(BaseModel):
    fs_type: Optional[str]
    storage_policy_id: Optional[str]
    storage_policy_name: Optional[str]
    volume_path: str

class WindowsSecurityContextOptions(BaseModel):
    gmsa_credential_spec: Optional[str]
    gmsa_credential_spec_name: Optional[str]
    host_process: Optional[bool]
    run_as_user_name: Optional[str]

class CSIVolumeSource(BaseModel):
    driver: str
    fs_type: Optional[str]
    node_publish_secret_ref: Optional[LocalObjectReference]
    read_only: Optional[bool]
    volume_attributes: Optional[Dict[str, str]]

class CephFSVolumeSource(BaseModel):
    monitors: List[str]
    path: Optional[str]
    read_only: Optional[bool]
    secret_file: Optional[str]
    secret_ref: Optional[LocalObjectReference]
    user: Optional[str]

class CinderVolumeSource(BaseModel):
    fs_type: Optional[str]
    read_only: Optional[bool]
    secret_ref: Optional[LocalObjectReference]
    volume_id: str

class ConfigMapProjection(BaseModel):
    items: Optional[List[KeyToPath]]
    name: Optional[str]
    optional: Optional[bool]

class ConfigMapVolumeSource(BaseModel):
    default_mode: Optional[int]
    items: Optional[List[KeyToPath]]
    name: Optional[str]
    optional: Optional[bool]

class EmptyDirVolumeSource(BaseModel):
    medium: Optional[str]
    size_limit: Optional[resource.Quantity]

class EnvFromSource(BaseModel):
    config_map_ref: Optional[ConfigMapEnvSource]
    prefix: Optional[str]
    secret_ref: Optional[SecretEnvSource]

class EventSeries(BaseModel):
    count: Optional[int]
    last_observed_time: Optional[v1.MicroTime]

class FlexVolumeSource(BaseModel):
    driver: str
    fs_type: Optional[str]
    options: Optional[Dict[str, str]]
    read_only: Optional[bool]
    secret_ref: Optional[LocalObjectReference]

class HTTPGetAction(BaseModel):
    host: Optional[str]
    http_headers: Optional[List[HTTPHeader]]
    path: Optional[str]
    port: intstr.IntOrString
    scheme: Optional[Scheme]

class ISCSIVolumeSource(BaseModel):
    chap_auth_discovery: Optional[bool]
    chap_auth_session: Optional[bool]
    fs_type: Optional[str]
    initiator_name: Optional[str]
    iqn: str
    iscsi_interface: Optional[str]
    lun: int
    portals: Optional[List[str]]
    read_only: Optional[bool]
    secret_ref: Optional[LocalObjectReference]
    target_portal: str

class NodeSelector(BaseModel):
    node_selector_terms: List[NodeSelectorTerm]

class PersistentVolumeClaimCondition(BaseModel):
    last_probe_time: Optional[v1.Time]
    last_transition_time: Optional[v1.Time]
    message: Optional[str]
    reason: Optional[str]
    status: str
    type: Type

class PersistentVolumeClaimStatus(BaseModel):
    access_modes: Optional[List[str]]
    allocated_resources: Optional[Dict[str, resource.Quantity]]
    capacity: Optional[Dict[str, resource.Quantity]]
    conditions: Optional[List[PersistentVolumeClaimCondition]]
    phase: Optional[Phase]
    resize_status: Optional[str]

class PodDNSConfig(BaseModel):
    nameservers: Optional[List[str]]
    options: Optional[List[PodDNSConfigOption]]
    searches: Optional[List[str]]

class PodSecurityContext(BaseModel):
    fs_group: Optional[int]
    fs_group_change_policy: Optional[str]
    run_as_group: Optional[int]
    run_as_non_root: Optional[bool]
    run_as_user: Optional[int]
    se_linux_options: Optional[SELinuxOptions]
    seccomp_profile: Optional[SeccompProfile]
    supplemental_groups: Optional[List[int]]
    sysctls: Optional[List[Sysctl]]
    windows_options: Optional[WindowsSecurityContextOptions]

class ResourceFieldSelector(BaseModel):
    container_name: Optional[str]
    divisor: Optional[resource.Quantity]
    resource: str

class ResourceRequirements(BaseModel):
    limits: Optional[Dict[str, resource.Quantity]]
    requests: Optional[Dict[str, resource.Quantity]]

class SecurityContext(BaseModel):
    allow_privilege_escalation: Optional[bool]
    capabilities: Optional[Capabilities]
    privileged: Optional[bool]
    proc_mount: Optional[str]
    read_only_root_filesystem: Optional[bool]
    run_as_group: Optional[int]
    run_as_non_root: Optional[bool]
    run_as_user: Optional[int]
    se_linux_options: Optional[SELinuxOptions]
    seccomp_profile: Optional[SeccompProfile]
    windows_options: Optional[WindowsSecurityContextOptions]

class ServicePort(BaseModel):
    app_protocol: Optional[str]
    name: Optional[str]
    node_port: Optional[int]
    port: int
    protocol: Optional[Protocol]
    target_port: Optional[intstr.IntOrString]

class TCPSocketAction(BaseModel):
    host: Optional[str]
    port: intstr.IntOrString

class DownwardAPIVolumeFile(BaseModel):
    field_ref: Optional[ObjectFieldSelector]
    mode: Optional[int]
    path: str
    resource_field_ref: Optional[ResourceFieldSelector]

class DownwardAPIVolumeSource(BaseModel):
    default_mode: Optional[int]
    items: Optional[List[DownwardAPIVolumeFile]]

class EnvVarSource(BaseModel):
    config_map_key_ref: Optional[ConfigMapKeySelector]
    field_ref: Optional[ObjectFieldSelector]
    resource_field_ref: Optional[ResourceFieldSelector]
    secret_key_ref: Optional[SecretKeySelector]

class Event(BaseModel):
    action: Optional[str]
    api_version: Optional[str]
    count: Optional[int]
    event_time: Optional[v1.MicroTime]
    first_timestamp: Optional[v1.Time]
    involved_object: ObjectReference
    kind: Optional[str]
    last_timestamp: Optional[v1.Time]
    message: Optional[str]
    metadata: v1.ObjectMeta
    reason: Optional[str]
    related: Optional[ObjectReference]
    reporting_component: Optional[str]
    reporting_instance: Optional[str]
    series: Optional[EventSeries]
    source: Optional[EventSource]
    type: Optional[str]

class LifecycleHandler(BaseModel):
    exec: Optional[ExecAction]
    http_get: Optional[HTTPGetAction]
    tcp_socket: Optional[TCPSocketAction]

class NodeAffinity(BaseModel):
    preferred_during_scheduling_ignored_during_execution: Optional[List[PreferredSchedulingTerm]]
    required_during_scheduling_ignored_during_execution: Optional[NodeSelector]

class PersistentVolumeClaimSpec(BaseModel):
    access_modes: Optional[List[str]]
    data_source: Optional[TypedLocalObjectReference]
    data_source_ref: Optional[TypedLocalObjectReference]
    resources: Optional[ResourceRequirements]
    selector: Optional[v1.LabelSelector]
    storage_class_name: Optional[str]
    volume_mode: Optional[str]
    volume_name: Optional[str]

class PersistentVolumeClaimTemplate(BaseModel):
    metadata: Optional[v1.ObjectMeta]
    spec: PersistentVolumeClaimSpec

class PodAffinityTerm(BaseModel):
    label_selector: Optional[v1.LabelSelector]
    namespace_selector: Optional[v1.LabelSelector]
    namespaces: Optional[List[str]]
    topology_key: str

class Probe(BaseModel):
    exec: Optional[ExecAction]
    failure_threshold: Optional[int]
    grpc: Optional[GRPCAction]
    http_get: Optional[HTTPGetAction]
    initial_delay_seconds: Optional[int]
    period_seconds: Optional[int]
    success_threshold: Optional[int]
    tcp_socket: Optional[TCPSocketAction]
    termination_grace_period_seconds: Optional[int]
    timeout_seconds: Optional[int]

class WeightedPodAffinityTerm(BaseModel):
    pod_affinity_term: PodAffinityTerm
    weight: int

class DownwardAPIProjection(BaseModel):
    items: Optional[List[DownwardAPIVolumeFile]]

class EnvVar(BaseModel):
    name: str
    value: Optional[str]
    value_from: Optional[EnvVarSource]

class EphemeralVolumeSource(BaseModel):
    volume_claim_template: Optional[PersistentVolumeClaimTemplate]

class Lifecycle(BaseModel):
    post_start: Optional[LifecycleHandler]
    pre_stop: Optional[LifecycleHandler]

class PersistentVolumeClaim(BaseModel):
    api_version: Optional[str]
    kind: Optional[str]
    metadata: Optional[v1.ObjectMeta]
    spec: Optional[PersistentVolumeClaimSpec]
    status: Optional[PersistentVolumeClaimStatus]

class PodAffinity(BaseModel):
    preferred_during_scheduling_ignored_during_execution: Optional[List[WeightedPodAffinityTerm]]
    required_during_scheduling_ignored_during_execution: Optional[List[PodAffinityTerm]]

class PodAntiAffinity(BaseModel):
    preferred_during_scheduling_ignored_during_execution: Optional[List[WeightedPodAffinityTerm]]
    required_during_scheduling_ignored_during_execution: Optional[List[PodAffinityTerm]]

class VolumeProjection(BaseModel):
    config_map: Optional[ConfigMapProjection]
    downward_api: Optional[DownwardAPIProjection]
    secret: Optional[SecretProjection]
    service_account_token: Optional[ServiceAccountTokenProjection]

class Affinity(BaseModel):
    node_affinity: Optional[NodeAffinity]
    pod_affinity: Optional[PodAffinity]
    pod_anti_affinity: Optional[PodAntiAffinity]

class Container(BaseModel):
    args: Optional[List[str]]
    command: Optional[List[str]]
    env: Optional[List[EnvVar]]
    env_from: Optional[List[EnvFromSource]]
    image: str
    image_pull_policy: Optional[ImagePullPolicy]
    lifecycle: Optional[Lifecycle]
    liveness_probe: Optional[Probe]
    name: Optional[str]
    ports: Optional[List[ContainerPort]]
    readiness_probe: Optional[Probe]
    resources: Optional[ResourceRequirements]
    security_context: Optional[SecurityContext]
    startup_probe: Optional[Probe]
    stdin: Optional[bool]
    stdin_once: Optional[bool]
    termination_message_path: Optional[str]
    termination_message_policy: Optional[TerminationMessagePolicy]
    tty: Optional[bool]
    volume_devices: Optional[List[VolumeDevice]]
    volume_mounts: Optional[List[VolumeMount]]
    working_dir: Optional[str]

class ProjectedVolumeSource(BaseModel):
    default_mode: Optional[int]
    sources: Optional[List[VolumeProjection]]

class Volume(BaseModel):
    aws_elastic_block_store: Optional[AWSElasticBlockStoreVolumeSource]
    azure_disk: Optional[AzureDiskVolumeSource]
    azure_file: Optional[AzureFileVolumeSource]
    cephfs: Optional[CephFSVolumeSource]
    cinder: Optional[CinderVolumeSource]
    config_map: Optional[ConfigMapVolumeSource]
    csi: Optional[CSIVolumeSource]
    downward_api: Optional[DownwardAPIVolumeSource]
    empty_dir: Optional[EmptyDirVolumeSource]
    ephemeral: Optional[EphemeralVolumeSource]
    fc: Optional[FCVolumeSource]
    flex_volume: Optional[FlexVolumeSource]
    flocker: Optional[FlockerVolumeSource]
    gce_persistent_disk: Optional[GCEPersistentDiskVolumeSource]
    git_repo: Optional[GitRepoVolumeSource]
    glusterfs: Optional[GlusterfsVolumeSource]
    host_path: Optional[HostPathVolumeSource]
    iscsi: Optional[ISCSIVolumeSource]
    name: str
    nfs: Optional[NFSVolumeSource]
    persistent_volume_claim: Optional[PersistentVolumeClaimVolumeSource]
    photon_persistent_disk: Optional[PhotonPersistentDiskVolumeSource]
    portworx_volume: Optional[PortworxVolumeSource]
    projected: Optional[ProjectedVolumeSource]
    quobyte: Optional[QuobyteVolumeSource]
    rbd: Optional[RBDVolumeSource]
    scale_io: Optional[ScaleIOVolumeSource]
    secret: Optional[SecretVolumeSource]
    storageos: Optional[StorageOSVolumeSource]
    vsphere_volume: Optional[VsphereVirtualDiskVolumeSource]

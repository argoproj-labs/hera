from typing import Any, Dict, List, Optional

from hera.shared._base_model import BaseModel as BaseModel

from ...k8s.api.core import v1 as v1
from ...k8s.api.policy import v1beta1 as v1beta1
from ...k8s.apimachinery.pkg.apis.meta import v1 as v1_1
from ...k8s.apimachinery.pkg.util import intstr as intstr

class Amount(BaseModel):
    __root__: float

class ArchivedWorkflowDeletedResponse(BaseModel): ...

class ArtGCStatus(BaseModel):
    not_specified: Optional[bool]
    pods_recouped: Optional[Dict[str, bool]]
    strategies_processed: Optional[Dict[str, bool]]

class ArtifactRepositoryRef(BaseModel):
    config_map: Optional[str]
    key: Optional[str]

class ArtifactResult(BaseModel):
    error: Optional[str]
    name: str
    success: Optional[bool]

class ArtifactResultNodeStatus(BaseModel):
    artifact_results: Optional[Dict[str, ArtifactResult]]

class ClusterWorkflowTemplateDeleteResponse(BaseModel): ...

class CollectEventRequest(BaseModel):
    name: Optional[str]

class CollectEventResponse(BaseModel): ...

class Condition(BaseModel):
    message: Optional[str]
    status: Optional[str]
    type: Optional[str]

class ContinueOn(BaseModel):
    error: Optional[bool]
    failed: Optional[bool]

class Counter(BaseModel):
    value: str

class CreateS3BucketOptions(BaseModel):
    object_locking: Optional[bool]

class CronWorkflowDeletedResponse(BaseModel): ...

class CronWorkflowResumeRequest(BaseModel):
    name: Optional[str]
    namespace: Optional[str]

class CronWorkflowSuspendRequest(BaseModel):
    name: Optional[str]
    namespace: Optional[str]

class Event(BaseModel):
    selector: str

class EventResponse(BaseModel): ...

class ExecutorConfig(BaseModel):
    service_account_name: Optional[str]

class Gauge(BaseModel):
    realtime: bool
    value: str

class GetUserInfoResponse(BaseModel):
    email: Optional[str]
    email_verified: Optional[bool]
    groups: Optional[List[str]]
    issuer: Optional[str]
    service_account_name: Optional[str]
    service_account_namespace: Optional[str]
    subject: Optional[str]

class HTTPBodySource(BaseModel):
    bytes: Optional[str]

class Header(BaseModel):
    name: str
    value: str

class Histogram(BaseModel):
    buckets: List[Amount]
    value: str

class Item(BaseModel):
    __root__: Any

class LabelKeys(BaseModel):
    items: Optional[List[str]]

class LabelValueFrom(BaseModel):
    expression: str

class LabelValues(BaseModel):
    items: Optional[List[str]]

class Link(BaseModel):
    name: str
    scope: str
    url: str

class LogEntry(BaseModel):
    content: Optional[str]
    pod_name: Optional[str]

class MemoizationStatus(BaseModel):
    cache_name: str
    hit: bool
    key: str

class Metadata(BaseModel):
    annotations: Optional[Dict[str, str]]
    labels: Optional[Dict[str, str]]

class MetricLabel(BaseModel):
    key: str
    value: str

class Mutex(BaseModel):
    name: Optional[str]

class MutexHolding(BaseModel):
    holder: Optional[str]
    mutex: Optional[str]

class MutexStatus(BaseModel):
    holding: Optional[List[MutexHolding]]
    waiting: Optional[List[MutexHolding]]

class NodeSynchronizationStatus(BaseModel):
    waiting: Optional[str]

class NoneStrategy(BaseModel): ...

class OAuth2EndpointParam(BaseModel):
    key: str
    value: Optional[str]

class OSSLifecycleRule(BaseModel):
    mark_deletion_after_days: Optional[int]
    mark_infrequent_access_after_days: Optional[int]

class Plugin(BaseModel): ...

class Prometheus(BaseModel):
    counter: Optional[Counter]
    gauge: Optional[Gauge]
    help: str
    histogram: Optional[Histogram]
    labels: Optional[List[MetricLabel]]
    name: str
    when: Optional[str]

class RawArtifact(BaseModel):
    data: str

class ResubmitArchivedWorkflowRequest(BaseModel):
    memoized: Optional[bool]
    name: Optional[str]
    namespace: Optional[str]
    parameters: Optional[List[str]]
    uid: Optional[str]

class RetryArchivedWorkflowRequest(BaseModel):
    name: Optional[str]
    namespace: Optional[str]
    node_field_selector: Optional[str]
    parameters: Optional[List[str]]
    restart_successful: Optional[bool]
    uid: Optional[str]

class RetryNodeAntiAffinity(BaseModel): ...

class SemaphoreHolding(BaseModel):
    holders: Optional[List[str]]
    semaphore: Optional[str]

class SemaphoreStatus(BaseModel):
    holding: Optional[List[SemaphoreHolding]]
    waiting: Optional[List[SemaphoreHolding]]

class SuppliedValueFrom(BaseModel): ...

class SuspendTemplate(BaseModel):
    duration: Optional[str]

class SynchronizationStatus(BaseModel):
    mutex: Optional[MutexStatus]
    semaphore: Optional[SemaphoreStatus]

class TTLStrategy(BaseModel):
    seconds_after_completion: Optional[int]
    seconds_after_failure: Optional[int]
    seconds_after_success: Optional[int]

class TarStrategy(BaseModel):
    compression_level: Optional[int]

class TemplateRef(BaseModel):
    cluster_scope: Optional[bool]
    name: Optional[str]
    template: Optional[str]

class TransformationStep(BaseModel):
    expression: str

class Version(BaseModel):
    build_date: str
    compiler: str
    git_commit: str
    git_tag: str
    git_tree_state: str
    go_version: str
    platform: str
    version: str

class VolumeClaimGC(BaseModel):
    strategy: Optional[str]

class WorkflowDeleteResponse(BaseModel): ...

class WorkflowMetadata(BaseModel):
    annotations: Optional[Dict[str, str]]
    labels: Optional[Dict[str, str]]
    labels_from: Optional[Dict[str, LabelValueFrom]]

class WorkflowResubmitRequest(BaseModel):
    memoized: Optional[bool]
    name: Optional[str]
    namespace: Optional[str]
    parameters: Optional[List[str]]

class WorkflowResumeRequest(BaseModel):
    name: Optional[str]
    namespace: Optional[str]
    node_field_selector: Optional[str]

class WorkflowRetryRequest(BaseModel):
    name: Optional[str]
    namespace: Optional[str]
    node_field_selector: Optional[str]
    parameters: Optional[List[str]]
    restart_successful: Optional[bool]

class WorkflowSetRequest(BaseModel):
    message: Optional[str]
    name: Optional[str]
    namespace: Optional[str]
    node_field_selector: Optional[str]
    output_parameters: Optional[str]
    phase: Optional[str]

class WorkflowStopRequest(BaseModel):
    message: Optional[str]
    name: Optional[str]
    namespace: Optional[str]
    node_field_selector: Optional[str]

class WorkflowSuspendRequest(BaseModel):
    name: Optional[str]
    namespace: Optional[str]

class WorkflowTemplateDeleteResponse(BaseModel): ...

class WorkflowTemplateRef(BaseModel):
    cluster_scope: Optional[bool]
    name: Optional[str]

class WorkflowTerminateRequest(BaseModel):
    name: Optional[str]
    namespace: Optional[str]

class ZipStrategy(BaseModel): ...

class ArchiveStrategy(BaseModel):
    none: Optional[NoneStrategy]
    tar: Optional[TarStrategy]
    zip: Optional[ZipStrategy]

class ArtifactGC(BaseModel):
    pod_metadata: Optional[Metadata]
    service_account_name: Optional[str]
    strategy: Optional[str]

class ArtifactGCStatus(BaseModel):
    artifact_results_by_node: Optional[Dict[str, ArtifactResultNodeStatus]]

class ArtifactoryArtifact(BaseModel):
    password_secret: Optional[v1.SecretKeySelector]
    url: str
    username_secret: Optional[v1.SecretKeySelector]

class ArtifactoryArtifactRepository(BaseModel):
    password_secret: Optional[v1.SecretKeySelector]
    repo_url: Optional[str]
    username_secret: Optional[v1.SecretKeySelector]

class AzureArtifact(BaseModel):
    account_key_secret: Optional[v1.SecretKeySelector]
    blob: str
    container: str
    endpoint: str
    use_sdk_creds: Optional[bool]

class AzureArtifactRepository(BaseModel):
    account_key_secret: Optional[v1.SecretKeySelector]
    blob_name_format: Optional[str]
    container: str
    endpoint: str
    use_sdk_creds: Optional[bool]

class Backoff(BaseModel):
    duration: Optional[str]
    factor: Optional[intstr.IntOrString]
    max_duration: Optional[str]

class BasicAuth(BaseModel):
    password_secret: Optional[v1.SecretKeySelector]
    username_secret: Optional[v1.SecretKeySelector]

class Cache(BaseModel):
    config_map: v1.ConfigMapKeySelector

class ClientCertAuth(BaseModel):
    client_cert_secret: Optional[v1.SecretKeySelector]
    client_key_secret: Optional[v1.SecretKeySelector]

class ContainerSetRetryStrategy(BaseModel):
    duration: Optional[str]
    retries: intstr.IntOrString

class CronWorkflowStatus(BaseModel):
    active: List[v1.ObjectReference]
    conditions: List[Condition]
    last_scheduled_time: v1_1.Time

class GCSArtifact(BaseModel):
    bucket: Optional[str]
    key: str
    service_account_key_secret: Optional[v1.SecretKeySelector]

class GCSArtifactRepository(BaseModel):
    bucket: Optional[str]
    key_format: Optional[str]
    service_account_key_secret: Optional[v1.SecretKeySelector]

class GitArtifact(BaseModel):
    branch: Optional[str]
    depth: Optional[int]
    disable_submodules: Optional[bool]
    fetch: Optional[List[str]]
    insecure_ignore_host_key: Optional[bool]
    password_secret: Optional[v1.SecretKeySelector]
    repo: str
    revision: Optional[str]
    single_branch: Optional[bool]
    ssh_private_key_secret: Optional[v1.SecretKeySelector]
    username_secret: Optional[v1.SecretKeySelector]

class HDFSArtifact(BaseModel):
    addresses: Optional[List[str]]
    force: Optional[bool]
    hdfs_user: Optional[str]
    krb_c_cache_secret: Optional[v1.SecretKeySelector]
    krb_config_config_map: Optional[v1.ConfigMapKeySelector]
    krb_keytab_secret: Optional[v1.SecretKeySelector]
    krb_realm: Optional[str]
    krb_service_principal_name: Optional[str]
    krb_username: Optional[str]
    path: str

class HDFSArtifactRepository(BaseModel):
    addresses: Optional[List[str]]
    force: Optional[bool]
    hdfs_user: Optional[str]
    krb_c_cache_secret: Optional[v1.SecretKeySelector]
    krb_config_config_map: Optional[v1.ConfigMapKeySelector]
    krb_keytab_secret: Optional[v1.SecretKeySelector]
    krb_realm: Optional[str]
    krb_service_principal_name: Optional[str]
    krb_username: Optional[str]
    path_format: Optional[str]

class HTTPHeaderSource(BaseModel):
    secret_key_ref: Optional[v1.SecretKeySelector]

class InfoResponse(BaseModel):
    links: Optional[List[Link]]
    managed_namespace: Optional[str]
    modals: Optional[Dict[str, bool]]
    nav_color: Optional[str]

class Memoize(BaseModel):
    cache: Cache
    key: str
    max_age: str

class Metrics(BaseModel):
    prometheus: List[Prometheus]

class OAuth2Auth(BaseModel):
    client_id_secret: Optional[v1.SecretKeySelector]
    client_secret_secret: Optional[v1.SecretKeySelector]
    endpoint_params: Optional[List[OAuth2EndpointParam]]
    scopes: Optional[List[str]]
    token_url_secret: Optional[v1.SecretKeySelector]

class OSSArtifact(BaseModel):
    access_key_secret: Optional[v1.SecretKeySelector]
    bucket: Optional[str]
    create_bucket_if_not_present: Optional[bool]
    endpoint: Optional[str]
    key: str
    lifecycle_rule: Optional[OSSLifecycleRule]
    secret_key_secret: Optional[v1.SecretKeySelector]
    security_token: Optional[str]

class OSSArtifactRepository(BaseModel):
    access_key_secret: Optional[v1.SecretKeySelector]
    bucket: Optional[str]
    create_bucket_if_not_present: Optional[bool]
    endpoint: Optional[str]
    key_format: Optional[str]
    lifecycle_rule: Optional[OSSLifecycleRule]
    secret_key_secret: Optional[v1.SecretKeySelector]
    security_token: Optional[str]

class RetryAffinity(BaseModel):
    node_anti_affinity: Optional[RetryNodeAntiAffinity]

class RetryStrategy(BaseModel):
    affinity: Optional[RetryAffinity]
    backoff: Optional[Backoff]
    expression: Optional[str]
    limit: Optional[intstr.IntOrString]
    retry_policy: Optional[str]

class S3EncryptionOptions(BaseModel):
    enable_encryption: Optional[bool]
    kms_encryption_context: Optional[str]
    kms_key_id: Optional[str]
    server_side_customer_key_secret: Optional[v1.SecretKeySelector]

class SemaphoreRef(BaseModel):
    config_map_key_ref: Optional[v1.ConfigMapKeySelector]

class Sequence(BaseModel):
    count: Optional[intstr.IntOrString]
    end: Optional[intstr.IntOrString]
    format: Optional[str]
    start: Optional[intstr.IntOrString]

class SubmitOpts(BaseModel):
    annotations: Optional[str]
    dry_run: Optional[bool]
    entry_point: Optional[str]
    generate_name: Optional[str]
    labels: Optional[str]
    name: Optional[str]
    owner_reference: Optional[v1_1.OwnerReference]
    parameters: Optional[List[str]]
    pod_priority_class_name: Optional[str]
    priority: Optional[int]
    server_dry_run: Optional[bool]
    service_account: Optional[str]

class Synchronization(BaseModel):
    mutex: Optional[Mutex]
    semaphore: Optional[SemaphoreRef]

class ValueFrom(BaseModel):
    config_map_key_ref: Optional[v1.ConfigMapKeySelector]
    default: Optional[str]
    event: Optional[str]
    expression: Optional[str]
    jq_filter: Optional[str]
    json_path: Optional[str]
    parameter: Optional[str]
    path: Optional[str]
    supplied: Optional[SuppliedValueFrom]

class WorkflowSubmitRequest(BaseModel):
    namespace: Optional[str]
    resource_kind: Optional[str]
    resource_name: Optional[str]
    submit_options: Optional[SubmitOpts]

class HTTPAuth(BaseModel):
    basic_auth: Optional[BasicAuth]
    client_cert: Optional[ClientCertAuth]
    oauth2: Optional[OAuth2Auth]

class HTTPHeader(BaseModel):
    name: str
    value: Optional[str]
    value_from: Optional[HTTPHeaderSource]

class Parameter(BaseModel):
    default: Optional[str]
    description: Optional[str]
    enum: Optional[List[str]]
    global_name: Optional[str]
    name: str
    value: Optional[str]
    value_from: Optional[ValueFrom]

class PodGC(BaseModel):
    label_selector: Optional[v1_1.LabelSelector]
    strategy: Optional[str]

class S3Artifact(BaseModel):
    access_key_secret: Optional[v1.SecretKeySelector]
    bucket: Optional[str]
    create_bucket_if_not_present: Optional[CreateS3BucketOptions]
    encryption_options: Optional[S3EncryptionOptions]
    endpoint: Optional[str]
    insecure: Optional[bool]
    key: Optional[str]
    region: Optional[str]
    role_arn: Optional[str]
    secret_key_secret: Optional[v1.SecretKeySelector]
    use_sdk_creds: Optional[bool]

class S3ArtifactRepository(BaseModel):
    access_key_secret: Optional[v1.SecretKeySelector]
    bucket: Optional[str]
    create_bucket_if_not_present: Optional[CreateS3BucketOptions]
    encryption_options: Optional[S3EncryptionOptions]
    endpoint: Optional[str]
    insecure: Optional[bool]
    key_format: Optional[str]
    key_prefix: Optional[str]
    region: Optional[str]
    role_arn: Optional[str]
    secret_key_secret: Optional[v1.SecretKeySelector]
    use_sdk_creds: Optional[bool]

class ArtifactRepository(BaseModel):
    archive_logs: Optional[bool]
    artifactory: Optional[ArtifactoryArtifactRepository]
    azure: Optional[AzureArtifactRepository]
    gcs: Optional[GCSArtifactRepository]
    hdfs: Optional[HDFSArtifactRepository]
    oss: Optional[OSSArtifactRepository]
    s3: Optional[S3ArtifactRepository]

class ArtifactRepositoryRefStatus(BaseModel):
    artifact_repository: Optional[ArtifactRepository]
    config_map: Optional[str]
    default: Optional[bool]
    key: Optional[str]
    namespace: Optional[str]

class HTTP(BaseModel):
    body: Optional[str]
    body_from: Optional[HTTPBodySource]
    headers: Optional[List[HTTPHeader]]
    insecure_skip_verify: Optional[bool]
    method: Optional[str]
    success_condition: Optional[str]
    timeout_seconds: Optional[int]
    url: str

class HTTPArtifact(BaseModel):
    auth: Optional[HTTPAuth]
    headers: Optional[List[Header]]
    url: str

class Artifact(BaseModel):
    archive: Optional[ArchiveStrategy]
    archive_logs: Optional[bool]
    artifact_gc: Optional[ArtifactGC]
    artifactory: Optional[ArtifactoryArtifact]
    azure: Optional[AzureArtifact]
    deleted: Optional[bool]
    from_: Optional[str]
    from_expression: Optional[str]
    gcs: Optional[GCSArtifact]
    git: Optional[GitArtifact]
    global_name: Optional[str]
    hdfs: Optional[HDFSArtifact]
    http: Optional[HTTPArtifact]
    mode: Optional[int]
    name: str
    optional: Optional[bool]
    oss: Optional[OSSArtifact]
    path: Optional[str]
    raw: Optional[RawArtifact]
    recurse_mode: Optional[bool]
    s3: Optional[S3Artifact]
    sub_path: Optional[str]

class ArtifactLocation(BaseModel):
    archive_logs: Optional[bool]
    artifactory: Optional[ArtifactoryArtifact]
    azure: Optional[AzureArtifact]
    gcs: Optional[GCSArtifact]
    git: Optional[GitArtifact]
    hdfs: Optional[HDFSArtifact]
    http: Optional[HTTPArtifact]
    oss: Optional[OSSArtifact]
    raw: Optional[RawArtifact]
    s3: Optional[S3Artifact]

class ArtifactNodeSpec(BaseModel):
    archive_location: Optional[ArtifactLocation]
    artifacts: Optional[Dict[str, Artifact]]

class ArtifactPaths(BaseModel):
    archive: Optional[ArchiveStrategy]
    archive_logs: Optional[bool]
    artifact_gc: Optional[ArtifactGC]
    artifactory: Optional[ArtifactoryArtifact]
    azure: Optional[AzureArtifact]
    deleted: Optional[bool]
    from_: Optional[str]
    from_expression: Optional[str]
    gcs: Optional[GCSArtifact]
    git: Optional[GitArtifact]
    global_name: Optional[str]
    hdfs: Optional[HDFSArtifact]
    http: Optional[HTTPArtifact]
    mode: Optional[int]
    name: str
    optional: Optional[bool]
    oss: Optional[OSSArtifact]
    path: Optional[str]
    raw: Optional[RawArtifact]
    recurse_mode: Optional[bool]
    s3: Optional[S3Artifact]
    sub_path: Optional[str]

class ContainerNode(BaseModel):
    args: Optional[List[str]]
    command: Optional[List[str]]
    dependencies: Optional[List[str]]
    env: Optional[List[v1.EnvVar]]
    env_from: Optional[List[v1.EnvFromSource]]
    image: Optional[str]
    image_pull_policy: Optional[str]
    lifecycle: Optional[v1.Lifecycle]
    liveness_probe: Optional[v1.Probe]
    name: str
    ports: Optional[List[v1.ContainerPort]]
    readiness_probe: Optional[v1.Probe]
    resources: Optional[v1.ResourceRequirements]
    security_context: Optional[v1.SecurityContext]
    startup_probe: Optional[v1.Probe]
    stdin: Optional[bool]
    stdin_once: Optional[bool]
    termination_message_path: Optional[str]
    termination_message_policy: Optional[str]
    tty: Optional[bool]
    volume_devices: Optional[List[v1.VolumeDevice]]
    volume_mounts: Optional[List[v1.VolumeMount]]
    working_dir: Optional[str]

class ContainerSetTemplate(BaseModel):
    containers: List[ContainerNode]
    retry_strategy: Optional[ContainerSetRetryStrategy]
    volume_mounts: Optional[List[v1.VolumeMount]]

class DataSource(BaseModel):
    artifact_paths: Optional[ArtifactPaths]

class Inputs(BaseModel):
    artifacts: Optional[List[Artifact]]
    parameters: Optional[List[Parameter]]

class ManifestFrom(BaseModel):
    artifact: Artifact

class Outputs(BaseModel):
    artifacts: Optional[List[Artifact]]
    exit_code: Optional[str]
    parameters: Optional[List[Parameter]]
    result: Optional[str]

class ResourceTemplate(BaseModel):
    action: str
    failure_condition: Optional[str]
    flags: Optional[List[str]]
    manifest: Optional[str]
    manifest_from: Optional[ManifestFrom]
    merge_strategy: Optional[str]
    set_owner_reference: Optional[bool]
    success_condition: Optional[str]

class ScriptTemplate(BaseModel):
    args: Optional[List[str]]
    command: Optional[List[str]]
    env: Optional[List[v1.EnvVar]]
    env_from: Optional[List[v1.EnvFromSource]]
    image: str
    image_pull_policy: Optional[str]
    lifecycle: Optional[v1.Lifecycle]
    liveness_probe: Optional[v1.Probe]
    name: Optional[str]
    ports: Optional[List[v1.ContainerPort]]
    readiness_probe: Optional[v1.Probe]
    resources: Optional[v1.ResourceRequirements]
    security_context: Optional[v1.SecurityContext]
    source: str
    startup_probe: Optional[v1.Probe]
    stdin: Optional[bool]
    stdin_once: Optional[bool]
    termination_message_path: Optional[str]
    termination_message_policy: Optional[str]
    tty: Optional[bool]
    volume_devices: Optional[List[v1.VolumeDevice]]
    volume_mounts: Optional[List[v1.VolumeMount]]
    working_dir: Optional[str]

class UserContainer(BaseModel):
    args: Optional[List[str]]
    command: Optional[List[str]]
    env: Optional[List[v1.EnvVar]]
    env_from: Optional[List[v1.EnvFromSource]]
    image: Optional[str]
    image_pull_policy: Optional[str]
    lifecycle: Optional[v1.Lifecycle]
    liveness_probe: Optional[v1.Probe]
    mirror_volume_mounts: Optional[bool]
    name: str
    ports: Optional[List[v1.ContainerPort]]
    readiness_probe: Optional[v1.Probe]
    resources: Optional[v1.ResourceRequirements]
    security_context: Optional[v1.SecurityContext]
    startup_probe: Optional[v1.Probe]
    stdin: Optional[bool]
    stdin_once: Optional[bool]
    termination_message_path: Optional[str]
    termination_message_policy: Optional[str]
    tty: Optional[bool]
    volume_devices: Optional[List[v1.VolumeDevice]]
    volume_mounts: Optional[List[v1.VolumeMount]]
    working_dir: Optional[str]

class Arguments(BaseModel):
    artifacts: Optional[List[Artifact]]
    parameters: Optional[List[Parameter]]

class ArtifactGCSpec(BaseModel):
    artifacts_by_node: Optional[Dict[str, ArtifactNodeSpec]]

class Data(BaseModel):
    source: DataSource
    transformation: List[TransformationStep]

class LifecycleHook(BaseModel):
    arguments: Optional[Arguments]
    expression: Optional[str]
    template: Optional[str]
    template_ref: Optional[TemplateRef]

class NodeResult(BaseModel):
    message: Optional[str]
    outputs: Optional[Outputs]
    phase: Optional[str]
    progress: Optional[str]

class NodeStatus(BaseModel):
    boundary_id: Optional[str]
    children: Optional[List[str]]
    daemoned: Optional[bool]
    display_name: Optional[str]
    estimated_duration: Optional[int]
    finished_at: Optional[v1_1.Time]
    host_node_name: Optional[str]
    id: str
    inputs: Optional[Inputs]
    memoization_status: Optional[MemoizationStatus]
    message: Optional[str]
    name: str
    outbound_nodes: Optional[List[str]]
    outputs: Optional[Outputs]
    phase: Optional[str]
    pod_ip: Optional[str]
    progress: Optional[str]
    resources_duration: Optional[Dict[str, int]]
    started_at: Optional[v1_1.Time]
    synchronization_status: Optional[NodeSynchronizationStatus]
    template_name: Optional[str]
    template_ref: Optional[TemplateRef]
    template_scope: Optional[str]
    type: str

class Submit(BaseModel):
    arguments: Optional[Arguments]
    metadata: Optional[v1_1.ObjectMeta]
    workflow_template_ref: WorkflowTemplateRef

class WorkflowEventBindingSpec(BaseModel):
    event: Event
    submit: Optional[Submit]

class WorkflowTaskSetStatus(BaseModel):
    nodes: Optional[Dict[str, NodeResult]]

class WorkflowEventBinding(BaseModel):
    api_version: Optional[str]
    kind: Optional[str]
    metadata: v1_1.ObjectMeta
    spec: WorkflowEventBindingSpec

class WorkflowEventBindingList(BaseModel):
    api_version: Optional[str]
    items: List[WorkflowEventBinding]
    kind: Optional[str]
    metadata: v1_1.ListMeta

class ClusterWorkflowTemplate(BaseModel):
    api_version: Optional[str]
    kind: Optional[str]
    metadata: v1_1.ObjectMeta
    spec: WorkflowSpec

class ClusterWorkflowTemplateCreateRequest(BaseModel):
    create_options: Optional[v1_1.CreateOptions]
    template: Optional[ClusterWorkflowTemplate]

class ClusterWorkflowTemplateLintRequest(BaseModel):
    create_options: Optional[v1_1.CreateOptions]
    template: Optional[ClusterWorkflowTemplate]

class ClusterWorkflowTemplateList(BaseModel):
    api_version: Optional[str]
    items: List[ClusterWorkflowTemplate]
    kind: Optional[str]
    metadata: v1_1.ListMeta

class ClusterWorkflowTemplateUpdateRequest(BaseModel):
    name: Optional[str]
    template: Optional[ClusterWorkflowTemplate]

class CreateCronWorkflowRequest(BaseModel):
    create_options: Optional[v1_1.CreateOptions]
    cron_workflow: Optional[CronWorkflow]
    namespace: Optional[str]

class CronWorkflow(BaseModel):
    api_version: Optional[str]
    kind: Optional[str]
    metadata: v1_1.ObjectMeta
    spec: CronWorkflowSpec
    status: Optional[CronWorkflowStatus]

class CronWorkflowList(BaseModel):
    api_version: Optional[str]
    items: List[CronWorkflow]
    kind: Optional[str]
    metadata: v1_1.ListMeta

class CronWorkflowSpec(BaseModel):
    concurrency_policy: Optional[str]
    failed_jobs_history_limit: Optional[int]
    schedule: str
    starting_deadline_seconds: Optional[int]
    successful_jobs_history_limit: Optional[int]
    suspend: Optional[bool]
    timezone: Optional[str]
    workflow_metadata: Optional[v1_1.ObjectMeta]
    workflow_spec: WorkflowSpec

class DAGTask(BaseModel):
    arguments: Optional[Arguments]
    continue_on: Optional[ContinueOn]
    dependencies: Optional[List[str]]
    depends: Optional[str]
    hooks: Optional[Dict[str, LifecycleHook]]
    inline: Optional[Template]
    name: str
    on_exit: Optional[str]
    template: Optional[str]
    template_ref: Optional[TemplateRef]
    when: Optional[str]
    with_items: Optional[List[Item]]
    with_param: Optional[str]
    with_sequence: Optional[Sequence]

class DAGTemplate(BaseModel):
    fail_fast: Optional[bool]
    target: Optional[str]
    tasks: List[DAGTask]

class LintCronWorkflowRequest(BaseModel):
    cron_workflow: Optional[CronWorkflow]
    namespace: Optional[str]

class ParallelSteps(BaseModel):
    __root__: List[WorkflowStep]

class Template(BaseModel):
    active_deadline_seconds: Optional[intstr.IntOrString]
    affinity: Optional[v1.Affinity]
    archive_location: Optional[ArtifactLocation]
    automount_service_account_token: Optional[bool]
    container: Optional[v1.Container]
    container_set: Optional[ContainerSetTemplate]
    daemon: Optional[bool]
    dag: Optional[DAGTemplate]
    data: Optional[Data]
    executor: Optional[ExecutorConfig]
    fail_fast: Optional[bool]
    host_aliases: Optional[List[v1.HostAlias]]
    http: Optional[HTTP]
    init_containers: Optional[List[UserContainer]]
    inputs: Optional[Inputs]
    memoize: Optional[Memoize]
    metadata: Optional[Metadata]
    metrics: Optional[Metrics]
    name: Optional[str]
    node_selector: Optional[Dict[str, str]]
    outputs: Optional[Outputs]
    parallelism: Optional[int]
    plugin: Optional[Plugin]
    pod_spec_patch: Optional[str]
    priority: Optional[int]
    priority_class_name: Optional[str]
    resource: Optional[ResourceTemplate]
    retry_strategy: Optional[RetryStrategy]
    scheduler_name: Optional[str]
    script: Optional[ScriptTemplate]
    security_context: Optional[v1.PodSecurityContext]
    service_account_name: Optional[str]
    sidecars: Optional[List[UserContainer]]
    steps: Optional[List[ParallelSteps]]
    suspend: Optional[SuspendTemplate]
    synchronization: Optional[Synchronization]
    timeout: Optional[str]
    tolerations: Optional[List[v1.Toleration]]
    volumes: Optional[List[v1.Volume]]

class UpdateCronWorkflowRequest(BaseModel):
    cron_workflow: Optional[CronWorkflow]
    name: Optional[str]
    namespace: Optional[str]

class Workflow(BaseModel):
    api_version: Optional[str]
    kind: Optional[str]
    metadata: v1_1.ObjectMeta
    spec: WorkflowSpec
    status: Optional[WorkflowStatus]

class WorkflowCreateRequest(BaseModel):
    create_options: Optional[v1_1.CreateOptions]
    instance_id: Optional[str]
    namespace: Optional[str]
    server_dry_run: Optional[bool]
    workflow: Optional[Workflow]

class WorkflowLintRequest(BaseModel):
    namespace: Optional[str]
    workflow: Optional[Workflow]

class WorkflowList(BaseModel):
    api_version: Optional[str]
    items: List[Workflow]
    kind: Optional[str]
    metadata: v1_1.ListMeta

class WorkflowSpec(BaseModel):
    active_deadline_seconds: Optional[int]
    affinity: Optional[v1.Affinity]
    archive_logs: Optional[bool]
    arguments: Optional[Arguments]
    artifact_gc: Optional[ArtifactGC]
    artifact_repository_ref: Optional[ArtifactRepositoryRef]
    automount_service_account_token: Optional[bool]
    dns_config: Optional[v1.PodDNSConfig]
    dns_policy: Optional[str]
    entrypoint: Optional[str]
    executor: Optional[ExecutorConfig]
    hooks: Optional[Dict[str, LifecycleHook]]
    host_aliases: Optional[List[v1.HostAlias]]
    host_network: Optional[bool]
    image_pull_secrets: Optional[List[v1.LocalObjectReference]]
    metrics: Optional[Metrics]
    node_selector: Optional[Dict[str, str]]
    on_exit: Optional[str]
    parallelism: Optional[int]
    pod_disruption_budget: Optional[v1beta1.PodDisruptionBudgetSpec]
    pod_gc: Optional[PodGC]
    pod_metadata: Optional[Metadata]
    pod_priority: Optional[int]
    pod_priority_class_name: Optional[str]
    pod_spec_patch: Optional[str]
    priority: Optional[int]
    retry_strategy: Optional[RetryStrategy]
    scheduler_name: Optional[str]
    security_context: Optional[v1.PodSecurityContext]
    service_account_name: Optional[str]
    shutdown: Optional[str]
    suspend: Optional[bool]
    synchronization: Optional[Synchronization]
    template_defaults: Optional[Template]
    templates: Optional[List[Template]]
    tolerations: Optional[List[v1.Toleration]]
    ttl_strategy: Optional[TTLStrategy]
    volume_claim_gc: Optional[VolumeClaimGC]
    volume_claim_templates: Optional[List[v1.PersistentVolumeClaim]]
    volumes: Optional[List[v1.Volume]]
    workflow_metadata: Optional[WorkflowMetadata]
    workflow_template_ref: Optional[WorkflowTemplateRef]

class WorkflowStatus(BaseModel):
    artifact_gc_status: Optional[ArtGCStatus]
    artifact_repository_ref: Optional[ArtifactRepositoryRefStatus]
    compressed_nodes: Optional[str]
    conditions: Optional[List[Condition]]
    estimated_duration: Optional[int]
    finished_at: Optional[v1_1.Time]
    message: Optional[str]
    nodes: Optional[Dict[str, NodeStatus]]
    offload_node_status_version: Optional[str]
    outputs: Optional[Outputs]
    persistent_volume_claims: Optional[List[v1.Volume]]
    phase: Optional[str]
    progress: Optional[str]
    resources_duration: Optional[Dict[str, int]]
    started_at: Optional[v1_1.Time]
    stored_templates: Optional[Dict[str, Template]]
    stored_workflow_template_spec: Optional[WorkflowSpec]
    synchronization: Optional[SynchronizationStatus]

class WorkflowStep(BaseModel):
    arguments: Optional[Arguments]
    continue_on: Optional[ContinueOn]
    hooks: Optional[Dict[str, LifecycleHook]]
    inline: Optional[Template]
    name: Optional[str]
    on_exit: Optional[str]
    template: Optional[str]
    template_ref: Optional[TemplateRef]
    when: Optional[str]
    with_items: Optional[List[Item]]
    with_param: Optional[str]
    with_sequence: Optional[Sequence]

class WorkflowTaskSetSpec(BaseModel):
    tasks: Optional[Dict[str, Template]]

class WorkflowTemplate(BaseModel):
    api_version: Optional[str]
    kind: Optional[str]
    metadata: v1_1.ObjectMeta
    spec: WorkflowSpec

class WorkflowTemplateCreateRequest(BaseModel):
    create_options: Optional[v1_1.CreateOptions]
    namespace: Optional[str]
    template: Optional[WorkflowTemplate]

class WorkflowTemplateLintRequest(BaseModel):
    create_options: Optional[v1_1.CreateOptions]
    namespace: Optional[str]
    template: Optional[WorkflowTemplate]

class WorkflowTemplateList(BaseModel):
    api_version: Optional[str]
    items: List[WorkflowTemplate]
    kind: Optional[str]
    metadata: v1_1.ListMeta

class WorkflowTemplateUpdateRequest(BaseModel):
    name: Optional[str]
    namespace: Optional[str]
    template: Optional[WorkflowTemplate]

class WorkflowWatchEvent(BaseModel):
    object: Optional[Workflow]
    type: Optional[str]

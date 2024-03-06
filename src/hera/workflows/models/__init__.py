"""[DO NOT EDIT MANUALLY] Auto-generated model classes.

Auto-generated by Hera via `make workflows-models`.
OpenAPI spec URL: https://raw.githubusercontent.com/argoproj/argo-workflows/v3.5.5/api/openapi-spec/swagger.json
"""

from hera.workflows.models.google.protobuf import Any
from hera.workflows.models.grpc.gateway.runtime import Error, StreamError
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import (
    HTTP,
    Amount,
    ArchivedWorkflowDeletedResponse,
    ArchiveStrategy,
    Arguments,
    ArtGCStatus,
    Artifact,
    ArtifactGC,
    ArtifactGCSpec,
    ArtifactGCStatus,
    ArtifactLocation,
    ArtifactNodeSpec,
    ArtifactoryArtifact,
    ArtifactoryArtifactRepository,
    ArtifactPaths,
    ArtifactRepository,
    ArtifactRepositoryRef,
    ArtifactRepositoryRefStatus,
    ArtifactResult,
    ArtifactResultNodeStatus,
    AzureArtifact,
    AzureArtifactRepository,
    Backoff,
    BasicAuth,
    Cache,
    ClientCertAuth,
    ClusterWorkflowTemplate,
    ClusterWorkflowTemplateCreateRequest,
    ClusterWorkflowTemplateDeleteResponse,
    ClusterWorkflowTemplateLintRequest,
    ClusterWorkflowTemplateList,
    ClusterWorkflowTemplateUpdateRequest,
    CollectEventRequest,
    CollectEventResponse,
    Column,
    Condition,
    ContainerNode,
    ContainerSetRetryStrategy,
    ContainerSetTemplate,
    ContinueOn,
    Counter,
    CreateCronWorkflowRequest,
    CreateS3BucketOptions,
    CronWorkflow,
    CronWorkflowDeletedResponse,
    CronWorkflowList,
    CronWorkflowResumeRequest,
    CronWorkflowSpec,
    CronWorkflowStatus,
    CronWorkflowSuspendRequest,
    DAGTask,
    DAGTemplate,
    Data,
    DataSource,
    Event,
    EventResponse,
    ExecutorConfig,
    Gauge,
    GCSArtifact,
    GCSArtifactRepository,
    GetUserInfoResponse,
    GitArtifact,
    HDFSArtifact,
    HDFSArtifactRepository,
    Header,
    Histogram,
    HTTPArtifact,
    HTTPAuth,
    HTTPBodySource,
    HTTPHeader as V1alpha1HTTPHeader,
    HTTPHeaderSource,
    InfoResponse,
    Inputs,
    Item,
    LabelKeys,
    LabelValueFrom,
    LabelValues,
    LifecycleHook,
    Link,
    LintCronWorkflowRequest,
    LogEntry as V1alpha1LogEntry,
    ManifestFrom,
    MemoizationStatus,
    Memoize,
    Metadata,
    MetricLabel,
    Metrics,
    Mutex,
    MutexHolding,
    MutexStatus,
    NodeFlag,
    NodeResult,
    NodeStatus,
    NodeSynchronizationStatus,
    NoneStrategy,
    OAuth2Auth,
    OAuth2EndpointParam,
    OSSArtifact,
    OSSArtifactRepository,
    OSSLifecycleRule,
    Outputs,
    ParallelSteps,
    Parameter,
    Plugin,
    PodGC,
    Prometheus,
    RawArtifact,
    ResourceTemplate,
    ResubmitArchivedWorkflowRequest,
    RetryAffinity,
    RetryArchivedWorkflowRequest,
    RetryNodeAntiAffinity,
    RetryStrategy,
    S3Artifact,
    S3ArtifactRepository,
    S3EncryptionOptions,
    ScriptTemplate,
    SemaphoreHolding,
    SemaphoreRef,
    SemaphoreStatus,
    Sequence,
    Submit,
    SubmitOpts,
    SuppliedValueFrom,
    SuspendTemplate,
    Synchronization,
    SynchronizationStatus,
    TarStrategy,
    Template,
    TemplateRef,
    TransformationStep,
    TTLStrategy,
    UpdateCronWorkflowRequest,
    UserContainer,
    ValueFrom,
    Version,
    VolumeClaimGC,
    Workflow,
    WorkflowCreateRequest,
    WorkflowDeleteResponse,
    WorkflowEventBinding,
    WorkflowEventBindingList,
    WorkflowEventBindingSpec,
    WorkflowLevelArtifactGC,
    WorkflowLintRequest,
    WorkflowList,
    WorkflowMetadata,
    WorkflowResubmitRequest,
    WorkflowResumeRequest,
    WorkflowRetryRequest,
    WorkflowSetRequest,
    WorkflowSpec,
    WorkflowStatus,
    WorkflowStep,
    WorkflowStopRequest,
    WorkflowSubmitRequest,
    WorkflowSuspendRequest,
    WorkflowTaskSetSpec,
    WorkflowTaskSetStatus,
    WorkflowTemplate,
    WorkflowTemplateCreateRequest,
    WorkflowTemplateDeleteResponse,
    WorkflowTemplateLintRequest,
    WorkflowTemplateList,
    WorkflowTemplateRef,
    WorkflowTemplateUpdateRequest,
    WorkflowTerminateRequest,
    WorkflowWatchEvent,
    ZipStrategy,
)
from hera.workflows.models.io.k8s.api.core.v1 import (
    Affinity,
    AWSElasticBlockStoreVolumeSource,
    AzureDiskVolumeSource,
    AzureFileVolumeSource,
    Capabilities,
    CephFSVolumeSource,
    CinderVolumeSource,
    ConfigMapEnvSource,
    ConfigMapKeySelector,
    ConfigMapProjection,
    ConfigMapVolumeSource,
    Container,
    ContainerPort,
    CSIVolumeSource,
    DownwardAPIProjection,
    DownwardAPIVolumeFile,
    DownwardAPIVolumeSource,
    Effect,
    EmptyDirVolumeSource,
    EnvFromSource,
    EnvVar,
    EnvVarSource,
    EphemeralVolumeSource,
    ExecAction,
    FCVolumeSource,
    FlexVolumeSource,
    FlockerVolumeSource,
    GCEPersistentDiskVolumeSource,
    GitRepoVolumeSource,
    GlusterfsVolumeSource,
    GRPCAction,
    HostAlias,
    HostPathVolumeSource,
    HTTPGetAction,
    HTTPHeader as V1HTTPHeader,
    ImagePullPolicy,
    ISCSIVolumeSource,
    KeyToPath,
    Lifecycle,
    LifecycleHandler,
    LocalObjectReference,
    NFSVolumeSource,
    NodeAffinity,
    NodeSelector,
    NodeSelectorRequirement,
    NodeSelectorTerm,
    ObjectFieldSelector,
    ObjectReference,
    Operator,
    OperatorModel,
    PersistentVolumeClaim,
    PersistentVolumeClaimCondition,
    PersistentVolumeClaimSpec,
    PersistentVolumeClaimStatus,
    PersistentVolumeClaimTemplate,
    PersistentVolumeClaimVolumeSource,
    Phase,
    PhotonPersistentDiskVolumeSource,
    PodAffinity,
    PodAffinityTerm,
    PodAntiAffinity,
    PodDNSConfig,
    PodDNSConfigOption,
    PodSecurityContext,
    PortworxVolumeSource,
    PreferredSchedulingTerm,
    Probe,
    ProjectedVolumeSource,
    Protocol,
    QuobyteVolumeSource,
    RBDVolumeSource,
    ResourceFieldSelector,
    ResourceRequirements,
    ScaleIOVolumeSource,
    Scheme,
    SeccompProfile,
    SecretEnvSource,
    SecretKeySelector,
    SecretProjection,
    SecretVolumeSource,
    SecurityContext,
    SELinuxOptions,
    ServiceAccountTokenProjection,
    ServicePort,
    StorageOSVolumeSource,
    Sysctl,
    TCPSocketAction,
    TerminationMessagePolicy,
    Toleration,
    Type,
    TypedLocalObjectReference,
    TypeModel,
    Volume,
    VolumeDevice,
    VolumeMount,
    VolumeProjection,
    VsphereVirtualDiskVolumeSource,
    WeightedPodAffinityTerm,
    WindowsSecurityContextOptions,
)
from hera.workflows.models.io.k8s.api.policy.v1 import PodDisruptionBudgetSpec
from hera.workflows.models.io.k8s.apimachinery.pkg.api.resource import Quantity
from hera.workflows.models.io.k8s.apimachinery.pkg.apis.meta.v1 import (
    CreateOptions,
    Duration,
    FieldsV1,
    GroupVersionResource,
    LabelSelector,
    LabelSelectorRequirement,
    ListMeta,
    ManagedFieldsEntry,
    MicroTime,
    ObjectMeta,
    OwnerReference,
    StatusCause,
    Time,
)
from hera.workflows.models.io.k8s.apimachinery.pkg.util.intstr import IntOrString

"""[DO NOT EDIT MANUALLY]Auto-generated model classes.

Auto-generated by Hera via `make workflows-models`.
OpenAPI spec URL: https://raw.githubusercontent.com/argoproj/argo-workflows/v3.4.4/api/openapi-spec/swagger.json
"""

from hera.workflows.models.io.argoproj.workflow.v1alpha1 import RetryAffinity
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import ResourceTemplate
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import WorkflowWatchEvent
from hera.workflows.models.io.k8s.api.core.v1 import Capabilities
from hera.workflows.models.io.k8s.api.core.v1 import DownwardAPIProjection
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import ClusterWorkflowTemplateList
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import OSSLifecycleRule
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import Header
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import ClusterWorkflowTemplate
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import ArtifactNodeSpec
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import S3Artifact
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import TransformationStep
from hera.workflows.models.io.k8s.api.core.v1 import PodDNSConfigOption
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import BasicAuth
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import Synchronization
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import Backoff
from hera.workflows.models.io.k8s.api.core.v1 import ResourceRequirements
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import Parameter
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import Submit
from hera.workflows.models.io.k8s.api.core.v1 import NodeSelectorRequirement
from hera.workflows.models.io.k8s.api.core.v1 import StorageOSVolumeSource
from hera.workflows.models.io.k8s.api.policy.v1beta1 import PodDisruptionBudgetSpec
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import WorkflowResumeRequest
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import GCSArtifact
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import ArtifactoryArtifact
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import SemaphoreHolding
from hera.workflows.models.io.k8s.apimachinery.pkg.apis.meta.v1 import StatusCause
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import CronWorkflow
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import Metadata
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import S3ArtifactRepository
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import TTLStrategy
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import WorkflowLintRequest
from hera.workflows.models.io.k8s.api.core.v1 import PodDNSConfig
from hera.workflows.models.io.k8s.api.core.v1 import SeccompProfile
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import WorkflowEventBindingList
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import LogEntry as V1alpha1LogEntry
from hera.workflows.models.io.k8s.api.core.v1 import SecretProjection
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import GetUserInfoResponse
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import CronWorkflowResumeRequest
from hera.workflows.models.io.k8s.api.core.v1 import ServicePort
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import HTTPBodySource
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import WorkflowEventBinding
from hera.workflows.models.io.k8s.apimachinery.pkg.apis.meta.v1 import LabelSelector
from hera.workflows.models.io.k8s.api.core.v1 import ContainerPort
from hera.workflows.models.io.k8s.api.core.v1 import PersistentVolumeClaimTemplate
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import DAGTask
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import EventResponse
from hera.workflows.models.io.k8s.api.core.v1 import QuobyteVolumeSource
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import WorkflowTemplateList
from hera.workflows.models.io.k8s.api.core.v1 import LifecycleHandler
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import CronWorkflowSpec
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import WorkflowStatus
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import ArtifactPaths
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import ArtifactRepository
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import HTTPAuth
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import SubmitOpts
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import ZipStrategy
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import ClusterWorkflowTemplateLintRequest
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import NodeResult
from hera.workflows.models.io.k8s.api.core.v1 import EphemeralVolumeSource
from hera.workflows.models.io.k8s.api.core.v1 import PortworxVolumeSource
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import UserContainer
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import SuppliedValueFrom
from hera.workflows.models.io.k8s.api.core.v1 import ObjectFieldSelector
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import ResubmitArchivedWorkflowRequest
from hera.workflows.models.io.k8s.api.core.v1 import ConfigMapProjection
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import Gauge
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import WorkflowSpec
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import MemoizationStatus
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import WorkflowTemplateCreateRequest
from hera.workflows.models.io.k8s.api.core.v1 import PodAntiAffinity
from hera.workflows.models.io.k8s.api.core.v1 import VolumeProjection
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import InfoResponse
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import Template
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import Inputs
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import TemplateRef
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import WorkflowTemplate
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import MutexStatus
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import LabelValueFrom
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import WorkflowResubmitRequest
from hera.workflows.models.io.k8s.api.core.v1 import GlusterfsVolumeSource
from hera.workflows.models.io.k8s.api.core.v1 import HostAlias
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import WorkflowList
from hera.workflows.models.io.k8s.api.core.v1 import AzureFileVolumeSource
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import AzureArtifactRepository
from hera.workflows.models.io.k8s.api.core.v1 import NFSVolumeSource
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import WorkflowTemplateDeleteResponse
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import ManifestFrom
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import WorkflowTerminateRequest
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import WorkflowEventBindingSpec
from hera.workflows.models.io.k8s.api.core.v1 import DownwardAPIVolumeSource
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import ArtifactRepositoryRefStatus
from hera.workflows.models.io.k8s.api.core.v1 import ServiceAccountTokenProjection
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import ArtifactoryArtifactRepository
from hera.workflows.models.io.k8s.api.core.v1 import KeyToPath
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import Link
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import WorkflowSuspendRequest
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import GitArtifact
from hera.workflows.models.grpc.gateway.runtime import StreamError
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import RawArtifact
from hera.workflows.models.io.k8s.api.core.v1 import ResourceFieldSelector
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import NodeSynchronizationStatus
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import S3EncryptionOptions
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import OSSArtifact
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import LifecycleHook
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import SuspendTemplate
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import DAGTemplate
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import CreateS3BucketOptions
from hera.workflows.models.io.k8s.api.core.v1 import ISCSIVolumeSource
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import Artifact
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import ArtifactLocation
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import ContainerSetRetryStrategy
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import HDFSArtifact
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import SemaphoreStatus
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import AzureArtifact
from hera.workflows.models.io.k8s.api.core.v1 import PodSecurityContext
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import Data
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import Outputs
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import ParallelSteps
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import WorkflowTaskSetSpec
from hera.workflows.models.io.k8s.api.core.v1 import CSIVolumeSource
from hera.workflows.models.io.k8s.api.core.v1 import NodeSelectorTerm
from hera.workflows.models.io.k8s.api.core.v1 import DownwardAPIVolumeFile
from hera.workflows.models.io.k8s.api.core.v1 import GRPCAction
from hera.workflows.models.io.k8s.apimachinery.pkg.apis.meta.v1 import FieldsV1
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import Arguments
from hera.workflows.models.io.k8s.api.core.v1 import ExecAction
from hera.workflows.models.io.k8s.api.core.v1 import ScaleIOVolumeSource
from hera.workflows.models.io.k8s.api.core.v1 import SecretKeySelector
from hera.workflows.models.grpc.gateway.runtime import Error
from hera.workflows.models.io.k8s.api.core.v1 import HostPathVolumeSource
from hera.workflows.models.io.k8s.api.core.v1 import FlockerVolumeSource
from hera.workflows.models.io.k8s.api.core.v1 import TCPSocketAction
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import RetryNodeAntiAffinity
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import WorkflowTemplateLintRequest
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import Condition
from hera.workflows.models.io.k8s.apimachinery.pkg.apis.meta.v1 import GroupVersionResource
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import ExecutorConfig
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import Sequence
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import WorkflowCreateRequest
from hera.workflows.models.io.k8s.apimachinery.pkg.apis.meta.v1 import LabelSelectorRequirement
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import CollectEventResponse
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import ContinueOn
from hera.workflows.models.io.k8s.api.core.v1 import EnvFromSource
from hera.workflows.models.io.k8s.api.core.v1 import VolumeDevice
from hera.workflows.models.io.k8s.apimachinery.pkg.apis.meta.v1 import ObjectMeta
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import Amount
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import ScriptTemplate
from hera.workflows.models.io.k8s.api.core.v1 import FlexVolumeSource
from hera.workflows.models.io.k8s.api.core.v1 import AWSElasticBlockStoreVolumeSource
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import HTTPHeader as V1alpha1HTTPHeader
from hera.workflows.models.io.k8s.api.core.v1 import WeightedPodAffinityTerm
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import ArtifactResultNodeStatus
from hera.workflows.models.io.k8s.api.core.v1 import SecretVolumeSource
from hera.workflows.models.io.k8s.api.core.v1 import Toleration
from hera.workflows.models.io.k8s.api.core.v1 import PodAffinityTerm
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import ArtifactResult
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import WorkflowSubmitRequest
from hera.workflows.models.io.k8s.api.core.v1 import CephFSVolumeSource
from hera.workflows.models.io.k8s.api.core.v1 import ConfigMapVolumeSource
from hera.workflows.models.io.k8s.api.core.v1 import GCEPersistentDiskVolumeSource
from hera.workflows.models.io.k8s.api.core.v1 import ObjectReference
from hera.workflows.models.io.k8s.api.core.v1 import VsphereVirtualDiskVolumeSource
from hera.workflows.models.io.k8s.api.core.v1 import HTTPGetAction
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import CronWorkflowList
from hera.workflows.models.io.k8s.api.core.v1 import PersistentVolumeClaimStatus
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import ClientCertAuth
from hera.workflows.models.io.k8s.api.core.v1 import PersistentVolumeClaim
from hera.workflows.models.io.k8s.api.core.v1 import GitRepoVolumeSource
from hera.workflows.models.io.k8s.api.core.v1 import Container
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import DataSource
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import WorkflowRetryRequest
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import ClusterWorkflowTemplateDeleteResponse
from hera.workflows.models.io.k8s.api.core.v1 import FCVolumeSource
from hera.workflows.models.io.k8s.api.core.v1 import Lifecycle
from hera.workflows.models.io.k8s.api.core.v1 import SecurityContext
from hera.workflows.models.io.k8s.apimachinery.pkg.apis.meta.v1 import CreateOptions
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import LabelKeys
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import WorkflowTaskSetStatus
from hera.workflows.models.io.k8s.api.core.v1 import SELinuxOptions
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import ArchiveStrategy
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import OAuth2Auth
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import Plugin
from hera.workflows.models.io.k8s.api.core.v1 import TypedLocalObjectReference
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import ArtifactRepositoryRef
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import RetryArchivedWorkflowRequest
from hera.workflows.models.io.k8s.api.core.v1 import WindowsSecurityContextOptions
from hera.workflows.models.io.k8s.apimachinery.pkg.api.resource import Quantity
from hera.workflows.models.io.k8s.api.core.v1 import NodeAffinity
from hera.workflows.models.io.k8s.api.core.v1 import Affinity
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import HTTP
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import ClusterWorkflowTemplateCreateRequest
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import ArtGCStatus
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import HDFSArtifactRepository
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import Mutex
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import RetryStrategy
from hera.workflows.models.io.k8s.api.core.v1 import EmptyDirVolumeSource
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import WorkflowDeleteResponse
from hera.workflows.models.io.k8s.api.core.v1 import PreferredSchedulingTerm
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import NoneStrategy
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import HTTPHeaderSource
from hera.workflows.models.io.k8s.api.core.v1 import PodAffinity
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import PodGC
from hera.workflows.models.io.k8s.api.core.v1 import CinderVolumeSource
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import Version
from hera.workflows.models.io.k8s.api.core.v1 import Sysctl
from hera.workflows.models.io.k8s.api.core.v1 import EnvVar
from hera.workflows.models.io.k8s.apimachinery.pkg.apis.meta.v1 import OwnerReference
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import Item
from hera.workflows.models.google.protobuf import Any
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import Memoize
from hera.workflows.models.io.k8s.apimachinery.pkg.apis.meta.v1 import ListMeta
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import TarStrategy
from hera.workflows.models.io.k8s.api.core.v1 import PersistentVolumeClaimVolumeSource
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import ContainerNode
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import LabelValues
from hera.workflows.models.io.k8s.api.core.v1 import PersistentVolumeClaimSpec
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import Event
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import CreateCronWorkflowRequest
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import Histogram
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import CronWorkflowSuspendRequest
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import ClusterWorkflowTemplateUpdateRequest
from hera.workflows.models.io.k8s.api.core.v1 import SecretEnvSource
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import ContainerSetTemplate
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import CronWorkflowDeletedResponse
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import HTTPArtifact
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import Counter
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import OAuth2EndpointParam
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import Metrics
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import NodeStatus
from hera.workflows.models.io.k8s.api.core.v1 import LocalObjectReference
from hera.workflows.models.io.k8s.apimachinery.pkg.apis.meta.v1 import MicroTime
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import Prometheus
from hera.workflows.models.io.k8s.api.core.v1 import ProjectedVolumeSource
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import LintCronWorkflowRequest
from hera.workflows.models.io.k8s.api.core.v1 import HTTPHeader as V1HTTPHeader
from hera.workflows.models.io.k8s.api.core.v1 import PhotonPersistentDiskVolumeSource
from hera.workflows.models.io.k8s.api.core.v1 import EnvVarSource
from hera.workflows.models.io.k8s.api.core.v1 import AzureDiskVolumeSource
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import WorkflowTemplateRef
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import WorkflowTemplateUpdateRequest
from hera.workflows.models.io.k8s.api.core.v1 import VolumeMount
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import WorkflowSetRequest
from hera.workflows.models.io.k8s.api.core.v1 import PersistentVolumeClaimCondition
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import ValueFrom
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import MetricLabel
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import VolumeClaimGC
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import Cache
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import WorkflowStopRequest
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import OSSArtifactRepository
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import MutexHolding
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import ArchivedWorkflowDeletedResponse
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import CollectEventRequest
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import SynchronizationStatus
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import Workflow
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import CronWorkflowStatus
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import SemaphoreRef
from hera.workflows.models.io.k8s.api.core.v1 import ConfigMapKeySelector
from hera.workflows.models.io.k8s.api.core.v1 import NodeSelector
from hera.workflows.models.io.k8s.apimachinery.pkg.apis.meta.v1 import ManagedFieldsEntry
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import UpdateCronWorkflowRequest
from hera.workflows.models.io.k8s.api.core.v1 import Probe
from hera.workflows.models.io.k8s.apimachinery.pkg.apis.meta.v1 import Time
from hera.workflows.models.io.k8s.api.core.v1 import Volume
from hera.workflows.models.io.k8s.api.core.v1 import ConfigMapEnvSource
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import GCSArtifactRepository
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import WorkflowMetadata
from hera.workflows.models.io.k8s.api.core.v1 import RBDVolumeSource
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import ArtifactGC
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import ArtifactGCStatus
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import ArtifactGCSpec
from hera.workflows.models.io.argoproj.workflow.v1alpha1 import WorkflowStep
from hera.workflows.models.io.k8s.apimachinery.pkg.util.intstr import IntOrString
from hera.workflows.models.io.k8s.api.core.v1 import ImagePullPolicy
from hera.workflows.models.io.k8s.api.core.v1 import TerminationMessagePolicy
from hera.workflows.models.io.k8s.api.core.v1 import Protocol
from hera.workflows.models.io.k8s.api.core.v1 import Scheme
from hera.workflows.models.io.k8s.api.core.v1 import Operator
from hera.workflows.models.io.k8s.api.core.v1 import Type
from hera.workflows.models.io.k8s.api.core.v1 import Phase
from hera.workflows.models.io.k8s.api.core.v1 import TypeModel
from hera.workflows.models.io.k8s.api.core.v1 import Effect
from hera.workflows.models.io.k8s.api.core.v1 import OperatorModel

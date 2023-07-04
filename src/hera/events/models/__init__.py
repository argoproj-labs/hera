"""[DO NOT EDIT MANUALLY] Auto-generated model classes.

Auto-generated by Hera via `make events-models`.
OpenAPI spec URL: https://raw.githubusercontent.com/argoproj/argo-workflows/v3.4.4/api/openapi-spec/swagger.json
"""

from hera.events.models.io.argoproj.events.v1alpha1 import GitlabEventSource
from hera.events.models.io.argoproj.events.v1alpha1 import TriggerPolicy
from hera.events.models.io.argoproj.events.v1alpha1 import EventDependency
from hera.events.models.io.argoproj.events.v1alpha1 import SensorStatus
from hera.events.models.io.argoproj.events.v1alpha1 import MQTTEventSource
from hera.events.models.io.argoproj.events.v1alpha1 import GithubAppCreds
from hera.events.models.io.argoproj.events.v1alpha1 import DataFilter
from hera.events.models.io.argoproj.events.v1alpha1 import StorageGridFilter
from hera.events.models.io.argoproj.events.v1alpha1 import FileArtifact
from hera.events.models.io.argoproj.events.v1alpha1 import EventSourceStatus
from hera.events.models.io.argoproj.events.v1alpha1 import AMQPConsumeConfig
from hera.events.models.io.argoproj.events.v1alpha1 import AWSLambdaTrigger
from hera.events.models.io.argoproj.events.v1alpha1 import ArtifactLocation
from hera.events.models.io.argoproj.events.v1alpha1 import LogTrigger
from hera.events.models.io.argoproj.events.v1alpha1 import BitbucketServerEventSource
from hera.events.models.sensor import CreateSensorRequest
from hera.events.models.eventsource import EventSourceWatchEvent
from hera.events.models.io.argoproj.events.v1alpha1 import PulsarTrigger
from hera.events.models.io.argoproj.events.v1alpha1 import EventDependencyFilter
from hera.events.models.io.argoproj.events.v1alpha1 import SASLConfig
from hera.events.models.io.argoproj.events.v1alpha1 import Trigger
from hera.events.models.io.argoproj.events.v1alpha1 import RateLimit
from hera.events.models.io.argoproj.events.v1alpha1 import TimeFilter
from hera.events.models.io.argoproj.events.v1alpha1 import ResourceFilter
from hera.events.models.io.argoproj.events.v1alpha1 import SensorSpec
from hera.events.models.io.argoproj.events.v1alpha1 import Status
from hera.events.models.io.argoproj.events.v1alpha1 import EventSourceList
from hera.events.models.sensor import LogEntry as SensorLogEntry
from hera.events.models.io.argoproj.events.v1alpha1 import Sensor
from hera.events.models.sensor import SensorWatchEvent
from hera.events.models.io.argoproj.events.v1alpha1 import ConfigMapPersistence
from hera.events.models.io.argoproj.events.v1alpha1 import EventSourceSpec
from hera.events.models.io.argoproj.events.v1alpha1 import S3Artifact
from hera.events.models.io.argoproj.events.v1alpha1 import Selector
from hera.events.models.io.argoproj.events.v1alpha1 import Metadata
from hera.events.models.io.argoproj.events.v1alpha1 import AMQPEventSource
from hera.events.models.io.argoproj.events.v1alpha1 import Service
from hera.events.models.io.argoproj.events.v1alpha1 import SQSEventSource
from hera.events.models.io.argoproj.events.v1alpha1 import CalendarEventSource
from hera.events.models.io.argoproj.events.v1alpha1 import AMQPQueueDeclareConfig
from hera.events.models.io.argoproj.events.v1alpha1 import StripeEventSource
from hera.events.models.io.argoproj.events.v1alpha1 import S3Filter
from hera.events.models.io.argoproj.events.v1alpha1 import Resource
from hera.events.models.io.argoproj.events.v1alpha1 import OpenWhiskTrigger
from hera.events.models.io.argoproj.events.v1alpha1 import NATSTrigger
from hera.events.models.io.argoproj.events.v1alpha1 import ResourceEventSource
from hera.events.models.io.argoproj.events.v1alpha1 import NATSEventsSource
from hera.events.models.eventsource import LogEntry as EventsourceLogEntry
from hera.events.models.io.argoproj.events.v1alpha1 import S3Bucket
from hera.events.models.io.argoproj.events.v1alpha1 import BitbucketEventSource
from hera.events.models.sensor import UpdateSensorRequest
from hera.events.models.io.argoproj.events.v1alpha1 import BitbucketAuth
from hera.events.models.io.argoproj.events.v1alpha1 import ValueFromSource
from hera.events.models.io.argoproj.events.v1alpha1 import GitArtifact
from hera.events.models.io.argoproj.events.v1alpha1 import HDFSEventSource
from hera.events.models.io.argoproj.events.v1alpha1 import EventContext
from hera.events.models.io.argoproj.events.v1alpha1 import SensorList
from hera.events.models.io.argoproj.events.v1alpha1 import TLSConfig
from hera.events.models.io.argoproj.events.v1alpha1 import SlackTrigger
from hera.events.models.io.argoproj.events.v1alpha1 import ArgoWorkflowTrigger
from hera.events.models.io.argoproj.events.v1alpha1 import GithubEventSource
from hera.events.models.io.argoproj.events.v1alpha1 import WebhookContext
from hera.events.models.io.argoproj.events.v1alpha1 import EventDependencyTransformer
from hera.events.models.io.argoproj.events.v1alpha1 import StatusPolicy
from hera.events.models.io.argoproj.events.v1alpha1 import GenericEventSource
from hera.events.models.io.argoproj.events.v1alpha1 import SNSEventSource
from hera.events.models.io.argoproj.events.v1alpha1 import TriggerParameterSource
from hera.events.models.io.argoproj.events.v1alpha1 import Int64OrString
from hera.events.models.io.argoproj.events.v1alpha1 import NATSAuth
from hera.events.models.io.argoproj.events.v1alpha1 import BasicAuth
from hera.events.models.io.argoproj.events.v1alpha1 import Template
from hera.events.models.io.argoproj.events.v1alpha1 import AzureEventsHubEventSource
from hera.events.models.io.argoproj.events.v1alpha1 import StorageGridEventSource
from hera.events.models.io.argoproj.events.v1alpha1 import KafkaConsumerGroup
from hera.events.models.io.argoproj.events.v1alpha1 import WebhookEventSource
from hera.events.models.io.argoproj.events.v1alpha1 import Condition
from hera.events.models.io.argoproj.events.v1alpha1 import ConditionsResetCriteria
from hera.events.models.io.argoproj.events.v1alpha1 import AMQPExchangeDeclareConfig
from hera.events.models.sensor import DeleteSensorResponse
from hera.events.models.io.argoproj.events.v1alpha1 import StandardK8STrigger
from hera.events.models.io.argoproj.events.v1alpha1 import CatchupConfiguration
from hera.events.models.io.argoproj.events.v1alpha1 import TriggerTemplate
from hera.events.models.io.argoproj.events.v1alpha1 import BitbucketServerRepository
from hera.events.models.io.argoproj.events.v1alpha1 import WatchPathConfig
from hera.events.models.io.argoproj.events.v1alpha1 import Amount
from hera.events.models.io.argoproj.events.v1alpha1 import AzureEventHubsTrigger
from hera.events.models.eventsource import UpdateEventSourceRequest
from hera.events.models.io.argoproj.events.v1alpha1 import SlackEventSource
from hera.events.models.io.argoproj.events.v1alpha1 import EventPersistence
from hera.events.models.io.argoproj.events.v1alpha1 import KafkaTrigger
from hera.events.models.io.argoproj.events.v1alpha1 import CustomTrigger
from hera.events.models.io.argoproj.events.v1alpha1 import BitbucketRepository
from hera.events.models.io.argoproj.events.v1alpha1 import FileEventSource
from hera.events.models.io.argoproj.events.v1alpha1 import NSQEventSource
from hera.events.models.io.argoproj.events.v1alpha1 import HTTPTrigger
from hera.events.models.io.argoproj.events.v1alpha1 import ConditionsResetByTime
from hera.events.models.io.argoproj.events.v1alpha1 import GitRemoteConfig
from hera.events.models.io.argoproj.events.v1alpha1 import OwnedRepositories
from hera.events.models.io.argoproj.events.v1alpha1 import EmitterEventSource
from hera.events.models.io.argoproj.events.v1alpha1 import AMQPQueueBindConfig
from hera.events.models.io.argoproj.events.v1alpha1 import PulsarEventSource
from hera.events.models.io.argoproj.events.v1alpha1 import GitCreds
from hera.events.models.eventsource import EventSourceDeletedResponse
from hera.events.models.io.argoproj.events.v1alpha1 import URLArtifact
from hera.events.models.io.argoproj.events.v1alpha1 import RedisStreamEventSource
from hera.events.models.io.argoproj.events.v1alpha1 import BitbucketBasicAuth
from hera.events.models.io.argoproj.events.v1alpha1 import PayloadField
from hera.events.models.io.argoproj.events.v1alpha1 import ExprFilter
from hera.events.models.io.argoproj.events.v1alpha1 import RedisEventSource
from hera.events.models.io.argoproj.events.v1alpha1 import SecureHeader
from hera.events.models.io.argoproj.events.v1alpha1 import EventSource
from hera.events.models.io.argoproj.events.v1alpha1 import Backoff
from hera.events.models.io.argoproj.events.v1alpha1 import K8SResourcePolicy
from hera.events.models.io.argoproj.events.v1alpha1 import PubSubEventSource
from hera.events.models.eventsource import CreateEventSourceRequest
from hera.events.models.io.argoproj.events.v1alpha1 import EventSourceFilter
from hera.events.models.io.argoproj.events.v1alpha1 import KafkaEventSource
from hera.events.models.io.argoproj.events.v1alpha1 import TriggerParameter
from hera.events.models.io.argoproj.workflow.v1alpha1 import Item
from hera.events.models.io.argoproj.workflow.v1alpha1 import Event
from hera.events.models.io.argoproj.workflow.v1alpha1 import EventResponse
from hera.events.models.io.argoproj.workflow.v1alpha1 import GetUserInfoResponse
from hera.events.models.io.argoproj.workflow.v1alpha1 import InfoResponse
from hera.events.models.io.argoproj.workflow.v1alpha1 import Version
from hera.events.models.io.k8s.api.core.v1 import ImagePullPolicy
from hera.events.models.io.k8s.api.core.v1 import TerminationMessagePolicy
from hera.events.models.io.k8s.api.core.v1 import Protocol
from hera.events.models.io.k8s.api.core.v1 import Scheme
from hera.events.models.io.k8s.api.core.v1 import Operator
from hera.events.models.io.k8s.api.core.v1 import Type
from hera.events.models.io.k8s.api.core.v1 import Phase
from hera.events.models.io.k8s.api.core.v1 import TypeModel
from hera.events.models.io.k8s.api.core.v1 import Effect
from hera.events.models.io.k8s.api.core.v1 import OperatorModel

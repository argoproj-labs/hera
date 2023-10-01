from typing import Dict, List, Optional

from hera.shared._base_model import BaseModel as BaseModel

from ...k8s.api.core import v1 as v1
from ...k8s.apimachinery.pkg.apis.meta import v1 as v1_1

class AMQPConsumeConfig(BaseModel):
    auto_ack: Optional[bool]
    consumer_tag: Optional[str]
    exclusive: Optional[bool]
    no_local: Optional[bool]
    no_wait: Optional[bool]

class AMQPExchangeDeclareConfig(BaseModel):
    auto_delete: Optional[bool]
    durable: Optional[bool]
    internal: Optional[bool]
    no_wait: Optional[bool]

class AMQPQueueBindConfig(BaseModel):
    no_wait: Optional[bool]

class AMQPQueueDeclareConfig(BaseModel):
    arguments: Optional[str]
    auto_delete: Optional[bool]
    durable: Optional[bool]
    exclusive: Optional[bool]
    name: Optional[str]
    no_wait: Optional[bool]

class Amount(BaseModel):
    value: Optional[str]

class BitbucketRepository(BaseModel):
    owner: Optional[str]
    repository_slug: Optional[str]

class BitbucketServerRepository(BaseModel):
    project_key: Optional[str]
    repository_slug: Optional[str]

class CatchupConfiguration(BaseModel):
    enabled: Optional[bool]
    max_duration: Optional[str]

class ConditionsResetByTime(BaseModel):
    cron: Optional[str]
    timezone: Optional[str]

class ConditionsResetCriteria(BaseModel):
    by_time: Optional[ConditionsResetByTime]

class ConfigMapPersistence(BaseModel):
    create_if_not_exist: Optional[bool]
    name: Optional[str]

class DataFilter(BaseModel):
    comparator: Optional[str]
    path: Optional[str]
    template: Optional[str]
    type: Optional[str]
    value: Optional[List[str]]

class EventDependencyTransformer(BaseModel):
    jq: Optional[str]
    script: Optional[str]

class EventPersistence(BaseModel):
    catchup: Optional[CatchupConfiguration]
    config_map: Optional[ConfigMapPersistence]

class EventSourceFilter(BaseModel):
    expression: Optional[str]

class FileArtifact(BaseModel):
    path: Optional[str]

class GitRemoteConfig(BaseModel):
    name: Optional[str]
    urls: Optional[List[str]]

class Int64OrString(BaseModel):
    int64_val: Optional[str]
    str_val: Optional[str]
    type: Optional[str]

class KafkaConsumerGroup(BaseModel):
    group_name: Optional[str]
    oldest: Optional[bool]
    rebalance_strategy: Optional[str]

class LogTrigger(BaseModel):
    interval_seconds: Optional[str]

class Metadata(BaseModel):
    annotations: Optional[Dict[str, str]]
    labels: Optional[Dict[str, str]]

class OwnedRepositories(BaseModel):
    names: Optional[List[str]]
    owner: Optional[str]

class PayloadField(BaseModel):
    name: Optional[str]
    path: Optional[str]

class RateLimit(BaseModel):
    requests_per_unit: Optional[int]
    unit: Optional[str]

class Resource(BaseModel):
    value: Optional[str]

class S3Bucket(BaseModel):
    key: Optional[str]
    name: Optional[str]

class S3Filter(BaseModel):
    prefix: Optional[str]
    suffix: Optional[str]

class Selector(BaseModel):
    key: Optional[str]
    operation: Optional[str]
    value: Optional[str]

class StatusPolicy(BaseModel):
    allow: Optional[List[int]]

class StorageGridFilter(BaseModel):
    prefix: Optional[str]
    suffix: Optional[str]

class TimeFilter(BaseModel):
    start: Optional[str]
    stop: Optional[str]

class TriggerParameterSource(BaseModel):
    context_key: Optional[str]
    context_template: Optional[str]
    data_key: Optional[str]
    data_template: Optional[str]
    dependency_name: Optional[str]
    value: Optional[str]

class URLArtifact(BaseModel):
    path: Optional[str]
    verify_cert: Optional[bool]

class WatchPathConfig(BaseModel):
    directory: Optional[str]
    path: Optional[str]
    path_regexp: Optional[str]

class AzureEventsHubEventSource(BaseModel):
    filter: Optional[EventSourceFilter]
    fqdn: Optional[str]
    hub_name: Optional[str]
    metadata: Optional[Dict[str, str]]
    shared_access_key: Optional[v1.SecretKeySelector]
    shared_access_key_name: Optional[v1.SecretKeySelector]

class Backoff(BaseModel):
    duration: Optional[Int64OrString]
    factor: Optional[Amount]
    jitter: Optional[Amount]
    steps: Optional[int]

class BasicAuth(BaseModel):
    password: Optional[v1.SecretKeySelector]
    username: Optional[v1.SecretKeySelector]

class BitbucketBasicAuth(BaseModel):
    password: Optional[v1.SecretKeySelector]
    username: Optional[v1.SecretKeySelector]

class CalendarEventSource(BaseModel):
    exclusion_dates: Optional[List[str]]
    filter: Optional[EventSourceFilter]
    interval: Optional[str]
    metadata: Optional[Dict[str, str]]
    persistence: Optional[EventPersistence]
    schedule: Optional[str]
    timezone: Optional[str]

class Condition(BaseModel):
    last_transition_time: Optional[v1_1.Time]
    message: Optional[str]
    reason: Optional[str]
    status: Optional[str]
    type: Optional[str]

class EventContext(BaseModel):
    datacontenttype: Optional[str]
    id: Optional[str]
    source: Optional[str]
    specversion: Optional[str]
    subject: Optional[str]
    time: Optional[v1_1.Time]
    type: Optional[str]

class ExprFilter(BaseModel):
    expr: Optional[str]
    fields: Optional[List[PayloadField]]

class FileEventSource(BaseModel):
    event_type: Optional[str]
    filter: Optional[EventSourceFilter]
    metadata: Optional[Dict[str, str]]
    polling: Optional[bool]
    watch_path_config: Optional[WatchPathConfig]

class GenericEventSource(BaseModel):
    auth_secret: Optional[v1.SecretKeySelector]
    config: Optional[str]
    filter: Optional[EventSourceFilter]
    insecure: Optional[bool]
    json_body: Optional[bool]
    metadata: Optional[Dict[str, str]]
    url: Optional[str]

class GitCreds(BaseModel):
    password: Optional[v1.SecretKeySelector]
    username: Optional[v1.SecretKeySelector]

class GithubAppCreds(BaseModel):
    app_id: Optional[str]
    installation_id: Optional[str]
    private_key: Optional[v1.SecretKeySelector]

class HDFSEventSource(BaseModel):
    addresses: Optional[List[str]]
    check_interval: Optional[str]
    filter: Optional[EventSourceFilter]
    hdfs_user: Optional[str]
    krb_c_cache_secret: Optional[v1.SecretKeySelector]
    krb_config_config_map: Optional[v1.ConfigMapKeySelector]
    krb_keytab_secret: Optional[v1.SecretKeySelector]
    krb_realm: Optional[str]
    krb_service_principal_name: Optional[str]
    krb_username: Optional[str]
    metadata: Optional[Dict[str, str]]
    type: Optional[str]
    watch_path_config: Optional[WatchPathConfig]

class K8SResourcePolicy(BaseModel):
    backoff: Optional[Backoff]
    error_on_backoff_timeout: Optional[bool]
    labels: Optional[Dict[str, str]]

class NATSAuth(BaseModel):
    basic: Optional[BasicAuth]
    credential: Optional[v1.SecretKeySelector]
    nkey: Optional[v1.SecretKeySelector]
    token: Optional[v1.SecretKeySelector]

class PubSubEventSource(BaseModel):
    credential_secret: Optional[v1.SecretKeySelector]
    delete_subscription_on_finish: Optional[bool]
    filter: Optional[EventSourceFilter]
    json_body: Optional[bool]
    metadata: Optional[Dict[str, str]]
    project_id: Optional[str]
    subscription_id: Optional[str]
    topic: Optional[str]
    topic_project_id: Optional[str]

class ResourceFilter(BaseModel):
    after_start: Optional[bool]
    created_by: Optional[v1_1.Time]
    fields: Optional[List[Selector]]
    labels: Optional[List[Selector]]
    prefix: Optional[str]

class S3Artifact(BaseModel):
    access_key: Optional[v1.SecretKeySelector]
    bucket: Optional[S3Bucket]
    endpoint: Optional[str]
    events: Optional[List[str]]
    filter: Optional[S3Filter]
    insecure: Optional[bool]
    metadata: Optional[Dict[str, str]]
    region: Optional[str]
    secret_key: Optional[v1.SecretKeySelector]

class SASLConfig(BaseModel):
    mechanism: Optional[str]
    password: Optional[v1.SecretKeySelector]
    user: Optional[v1.SecretKeySelector]

class SQSEventSource(BaseModel):
    access_key: Optional[v1.SecretKeySelector]
    dlq: Optional[bool]
    endpoint: Optional[str]
    filter: Optional[EventSourceFilter]
    json_body: Optional[bool]
    metadata: Optional[Dict[str, str]]
    queue: Optional[str]
    queue_account_id: Optional[str]
    region: Optional[str]
    role_arn: Optional[str]
    secret_key: Optional[v1.SecretKeySelector]
    session_token: Optional[v1.SecretKeySelector]
    wait_time_seconds: Optional[str]

class Status(BaseModel):
    conditions: Optional[List[Condition]]

class TLSConfig(BaseModel):
    ca_cert_secret: Optional[v1.SecretKeySelector]
    client_cert_secret: Optional[v1.SecretKeySelector]
    client_key_secret: Optional[v1.SecretKeySelector]
    insecure_skip_verify: Optional[bool]

class TriggerParameter(BaseModel):
    dest: Optional[str]
    operation: Optional[str]
    src: Optional[TriggerParameterSource]

class TriggerPolicy(BaseModel):
    k8s: Optional[K8SResourcePolicy]
    status: Optional[StatusPolicy]

class ValueFromSource(BaseModel):
    config_map_key_ref: Optional[v1.ConfigMapKeySelector]
    secret_key_ref: Optional[v1.SecretKeySelector]

class WebhookContext(BaseModel):
    auth_secret: Optional[v1.SecretKeySelector]
    endpoint: Optional[str]
    max_payload_size: Optional[str]
    metadata: Optional[Dict[str, str]]
    method: Optional[str]
    port: Optional[str]
    server_cert_secret: Optional[v1.SecretKeySelector]
    server_key_secret: Optional[v1.SecretKeySelector]
    url: Optional[str]

class WebhookEventSource(BaseModel):
    filter: Optional[EventSourceFilter]
    webhook_context: Optional[WebhookContext]

class AMQPEventSource(BaseModel):
    auth: Optional[BasicAuth]
    connection_backoff: Optional[Backoff]
    consume: Optional[AMQPConsumeConfig]
    exchange_declare: Optional[AMQPExchangeDeclareConfig]
    exchange_name: Optional[str]
    exchange_type: Optional[str]
    filter: Optional[EventSourceFilter]
    json_body: Optional[bool]
    metadata: Optional[Dict[str, str]]
    queue_bind: Optional[AMQPQueueBindConfig]
    queue_declare: Optional[AMQPQueueDeclareConfig]
    routing_key: Optional[str]
    tls: Optional[TLSConfig]
    url: Optional[str]
    url_secret: Optional[v1.SecretKeySelector]

class AWSLambdaTrigger(BaseModel):
    access_key: Optional[v1.SecretKeySelector]
    function_name: Optional[str]
    invocation_type: Optional[str]
    parameters: Optional[List[TriggerParameter]]
    payload: Optional[List[TriggerParameter]]
    region: Optional[str]
    role_arn: Optional[str]
    secret_key: Optional[v1.SecretKeySelector]

class AzureEventHubsTrigger(BaseModel):
    fqdn: Optional[str]
    hub_name: Optional[str]
    parameters: Optional[List[TriggerParameter]]
    payload: Optional[List[TriggerParameter]]
    shared_access_key: Optional[v1.SecretKeySelector]
    shared_access_key_name: Optional[v1.SecretKeySelector]

class BitbucketAuth(BaseModel):
    basic: Optional[BitbucketBasicAuth]
    oauth_token: Optional[v1.SecretKeySelector]

class BitbucketEventSource(BaseModel):
    auth: Optional[BitbucketAuth]
    delete_hook_on_finish: Optional[bool]
    events: Optional[List[str]]
    filter: Optional[EventSourceFilter]
    metadata: Optional[Dict[str, str]]
    owner: Optional[str]
    project_key: Optional[str]
    repositories: Optional[List[BitbucketRepository]]
    repository_slug: Optional[str]
    webhook: Optional[WebhookContext]

class BitbucketServerEventSource(BaseModel):
    access_token: Optional[v1.SecretKeySelector]
    bitbucketserver_base_url: Optional[str]
    delete_hook_on_finish: Optional[bool]
    events: Optional[List[str]]
    filter: Optional[EventSourceFilter]
    metadata: Optional[Dict[str, str]]
    project_key: Optional[str]
    repositories: Optional[List[BitbucketServerRepository]]
    repository_slug: Optional[str]
    webhook: Optional[WebhookContext]
    webhook_secret: Optional[v1.SecretKeySelector]

class CustomTrigger(BaseModel):
    cert_secret: Optional[v1.SecretKeySelector]
    parameters: Optional[List[TriggerParameter]]
    payload: Optional[List[TriggerParameter]]
    secure: Optional[bool]
    server_name_override: Optional[str]
    server_url: Optional[str]
    spec: Optional[Dict[str, str]]

class EmitterEventSource(BaseModel):
    broker: Optional[str]
    channel_key: Optional[str]
    channel_name: Optional[str]
    connection_backoff: Optional[Backoff]
    filter: Optional[EventSourceFilter]
    json_body: Optional[bool]
    metadata: Optional[Dict[str, str]]
    password: Optional[v1.SecretKeySelector]
    tls: Optional[TLSConfig]
    username: Optional[v1.SecretKeySelector]

class EventDependencyFilter(BaseModel):
    context: Optional[EventContext]
    data: Optional[List[DataFilter]]
    data_logical_operator: Optional[str]
    expr_logical_operator: Optional[str]
    exprs: Optional[List[ExprFilter]]
    script: Optional[str]
    time: Optional[TimeFilter]

class EventSourceStatus(BaseModel):
    status: Optional[Status]

class GitArtifact(BaseModel):
    branch: Optional[str]
    clone_directory: Optional[str]
    creds: Optional[GitCreds]
    file_path: Optional[str]
    insecure_ignore_host_key: Optional[bool]
    ref: Optional[str]
    remote: Optional[GitRemoteConfig]
    ssh_key_secret: Optional[v1.SecretKeySelector]
    tag: Optional[str]
    url: Optional[str]

class GithubEventSource(BaseModel):
    active: Optional[bool]
    api_token: Optional[v1.SecretKeySelector]
    content_type: Optional[str]
    delete_hook_on_finish: Optional[bool]
    events: Optional[List[str]]
    filter: Optional[EventSourceFilter]
    github_app: Optional[GithubAppCreds]
    github_base_url: Optional[str]
    github_upload_url: Optional[str]
    id: Optional[str]
    insecure: Optional[bool]
    metadata: Optional[Dict[str, str]]
    organizations: Optional[List[str]]
    owner: Optional[str]
    repositories: Optional[List[OwnedRepositories]]
    repository: Optional[str]
    webhook: Optional[WebhookContext]
    webhook_secret: Optional[v1.SecretKeySelector]

class GitlabEventSource(BaseModel):
    access_token: Optional[v1.SecretKeySelector]
    delete_hook_on_finish: Optional[bool]
    enable_ssl_verification: Optional[bool]
    events: Optional[List[str]]
    filter: Optional[EventSourceFilter]
    gitlab_base_url: Optional[str]
    metadata: Optional[Dict[str, str]]
    project_id: Optional[str]
    projects: Optional[List[str]]
    secret_token: Optional[v1.SecretKeySelector]
    webhook: Optional[WebhookContext]

class KafkaEventSource(BaseModel):
    config: Optional[str]
    connection_backoff: Optional[Backoff]
    consumer_group: Optional[KafkaConsumerGroup]
    filter: Optional[EventSourceFilter]
    json_body: Optional[bool]
    limit_events_per_second: Optional[str]
    metadata: Optional[Dict[str, str]]
    partition: Optional[str]
    sasl: Optional[SASLConfig]
    tls: Optional[TLSConfig]
    topic: Optional[str]
    url: Optional[str]
    version: Optional[str]

class KafkaTrigger(BaseModel):
    compress: Optional[bool]
    flush_frequency: Optional[int]
    parameters: Optional[List[TriggerParameter]]
    partition: Optional[int]
    partitioning_key: Optional[str]
    payload: Optional[List[TriggerParameter]]
    required_acks: Optional[int]
    sasl: Optional[SASLConfig]
    tls: Optional[TLSConfig]
    topic: Optional[str]
    url: Optional[str]
    version: Optional[str]

class MQTTEventSource(BaseModel):
    client_id: Optional[str]
    connection_backoff: Optional[Backoff]
    filter: Optional[EventSourceFilter]
    json_body: Optional[bool]
    metadata: Optional[Dict[str, str]]
    tls: Optional[TLSConfig]
    topic: Optional[str]
    url: Optional[str]

class NATSEventsSource(BaseModel):
    auth: Optional[NATSAuth]
    connection_backoff: Optional[Backoff]
    filter: Optional[EventSourceFilter]
    json_body: Optional[bool]
    metadata: Optional[Dict[str, str]]
    subject: Optional[str]
    tls: Optional[TLSConfig]
    url: Optional[str]

class NATSTrigger(BaseModel):
    parameters: Optional[List[TriggerParameter]]
    payload: Optional[List[TriggerParameter]]
    subject: Optional[str]
    tls: Optional[TLSConfig]
    url: Optional[str]

class NSQEventSource(BaseModel):
    channel: Optional[str]
    connection_backoff: Optional[Backoff]
    filter: Optional[EventSourceFilter]
    host_address: Optional[str]
    json_body: Optional[bool]
    metadata: Optional[Dict[str, str]]
    tls: Optional[TLSConfig]
    topic: Optional[str]

class OpenWhiskTrigger(BaseModel):
    action_name: Optional[str]
    auth_token: Optional[v1.SecretKeySelector]
    host: Optional[str]
    namespace: Optional[str]
    parameters: Optional[List[TriggerParameter]]
    payload: Optional[List[TriggerParameter]]
    version: Optional[str]

class PulsarEventSource(BaseModel):
    auth_token_secret: Optional[v1.SecretKeySelector]
    connection_backoff: Optional[Backoff]
    filter: Optional[EventSourceFilter]
    json_body: Optional[bool]
    metadata: Optional[Dict[str, str]]
    tls: Optional[TLSConfig]
    tls_allow_insecure_connection: Optional[bool]
    tls_trust_certs_secret: Optional[v1.SecretKeySelector]
    tls_validate_hostname: Optional[bool]
    topics: Optional[List[str]]
    type: Optional[str]
    url: Optional[str]

class PulsarTrigger(BaseModel):
    auth_token_secret: Optional[v1.SecretKeySelector]
    connection_backoff: Optional[Backoff]
    parameters: Optional[List[TriggerParameter]]
    payload: Optional[List[TriggerParameter]]
    tls: Optional[TLSConfig]
    tls_allow_insecure_connection: Optional[bool]
    tls_trust_certs_secret: Optional[v1.SecretKeySelector]
    tls_validate_hostname: Optional[bool]
    topic: Optional[str]
    url: Optional[str]

class RedisEventSource(BaseModel):
    channels: Optional[List[str]]
    db: Optional[int]
    filter: Optional[EventSourceFilter]
    host_address: Optional[str]
    json_body: Optional[bool]
    metadata: Optional[Dict[str, str]]
    namespace: Optional[str]
    password: Optional[v1.SecretKeySelector]
    tls: Optional[TLSConfig]
    username: Optional[str]

class RedisStreamEventSource(BaseModel):
    consumer_group: Optional[str]
    db: Optional[int]
    filter: Optional[EventSourceFilter]
    host_address: Optional[str]
    max_msg_count_per_read: Optional[int]
    metadata: Optional[Dict[str, str]]
    password: Optional[v1.SecretKeySelector]
    streams: Optional[List[str]]
    tls: Optional[TLSConfig]
    username: Optional[str]

class ResourceEventSource(BaseModel):
    event_types: Optional[List[str]]
    filter: Optional[ResourceFilter]
    group_version_resource: Optional[v1_1.GroupVersionResource]
    metadata: Optional[Dict[str, str]]
    namespace: Optional[str]

class SNSEventSource(BaseModel):
    access_key: Optional[v1.SecretKeySelector]
    endpoint: Optional[str]
    filter: Optional[EventSourceFilter]
    metadata: Optional[Dict[str, str]]
    region: Optional[str]
    role_arn: Optional[str]
    secret_key: Optional[v1.SecretKeySelector]
    topic_arn: Optional[str]
    validate_signature: Optional[bool]
    webhook: Optional[WebhookContext]

class SecureHeader(BaseModel):
    name: Optional[str]
    value_from: Optional[ValueFromSource]

class SensorStatus(BaseModel):
    status: Optional[Status]

class Service(BaseModel):
    cluster_ip: Optional[str]
    ports: Optional[List[v1.ServicePort]]

class SlackEventSource(BaseModel):
    filter: Optional[EventSourceFilter]
    metadata: Optional[Dict[str, str]]
    signing_secret: Optional[v1.SecretKeySelector]
    token: Optional[v1.SecretKeySelector]
    webhook: Optional[WebhookContext]

class SlackTrigger(BaseModel):
    channel: Optional[str]
    message: Optional[str]
    parameters: Optional[List[TriggerParameter]]
    slack_token: Optional[v1.SecretKeySelector]

class StorageGridEventSource(BaseModel):
    api_url: Optional[str]
    auth_token: Optional[v1.SecretKeySelector]
    bucket: Optional[str]
    events: Optional[List[str]]
    filter: Optional[StorageGridFilter]
    metadata: Optional[Dict[str, str]]
    region: Optional[str]
    topic_arn: Optional[str]
    webhook: Optional[WebhookContext]

class StripeEventSource(BaseModel):
    api_key: Optional[v1.SecretKeySelector]
    create_webhook: Optional[bool]
    event_filter: Optional[List[str]]
    metadata: Optional[Dict[str, str]]
    webhook: Optional[WebhookContext]

class ArtifactLocation(BaseModel):
    configmap: Optional[v1.ConfigMapKeySelector]
    file: Optional[FileArtifact]
    git: Optional[GitArtifact]
    inline: Optional[str]
    resource: Optional[Resource]
    s3: Optional[S3Artifact]
    url: Optional[URLArtifact]

class EventDependency(BaseModel):
    event_name: Optional[str]
    event_source_name: Optional[str]
    filters: Optional[EventDependencyFilter]
    filters_logical_operator: Optional[str]
    name: Optional[str]
    transform: Optional[EventDependencyTransformer]

class HTTPTrigger(BaseModel):
    basic_auth: Optional[BasicAuth]
    headers: Optional[Dict[str, str]]
    method: Optional[str]
    parameters: Optional[List[TriggerParameter]]
    payload: Optional[List[TriggerParameter]]
    secure_headers: Optional[List[SecureHeader]]
    timeout: Optional[str]
    tls: Optional[TLSConfig]
    url: Optional[str]

class StandardK8STrigger(BaseModel):
    live_object: Optional[bool]
    operation: Optional[str]
    parameters: Optional[List[TriggerParameter]]
    patch_strategy: Optional[str]
    source: Optional[ArtifactLocation]

class ArgoWorkflowTrigger(BaseModel):
    args: Optional[List[str]]
    operation: Optional[str]
    parameters: Optional[List[TriggerParameter]]
    source: Optional[ArtifactLocation]

class TriggerTemplate(BaseModel):
    argo_workflow: Optional[ArgoWorkflowTrigger]
    aws_lambda: Optional[AWSLambdaTrigger]
    azure_event_hubs: Optional[AzureEventHubsTrigger]
    conditions: Optional[str]
    conditions_reset: Optional[List[ConditionsResetCriteria]]
    custom: Optional[CustomTrigger]
    http: Optional[HTTPTrigger]
    k8s: Optional[StandardK8STrigger]
    kafka: Optional[KafkaTrigger]
    log: Optional[LogTrigger]
    name: Optional[str]
    nats: Optional[NATSTrigger]
    open_whisk: Optional[OpenWhiskTrigger]
    pulsar: Optional[PulsarTrigger]
    slack: Optional[SlackTrigger]

class Template(BaseModel):
    affinity: Optional[v1.Affinity]
    container: Optional[v1.Container]
    image_pull_secrets: Optional[List[v1.LocalObjectReference]]
    metadata: Optional[Metadata]
    node_selector: Optional[Dict[str, str]]
    priority: Optional[int]
    priority_class_name: Optional[str]
    security_context: Optional[v1.PodSecurityContext]
    service_account_name: Optional[str]
    tolerations: Optional[List[v1.Toleration]]
    volumes: Optional[List[v1.Volume]]

class Trigger(BaseModel):
    parameters: Optional[List[TriggerParameter]]
    policy: Optional[TriggerPolicy]
    rate_limit: Optional[RateLimit]
    retry_strategy: Optional[Backoff]
    template: Optional[TriggerTemplate]

class EventSourceSpec(BaseModel):
    amqp: Optional[Dict[str, AMQPEventSource]]
    azure_events_hub: Optional[Dict[str, AzureEventsHubEventSource]]
    bitbucket: Optional[Dict[str, BitbucketEventSource]]
    bitbucketserver: Optional[Dict[str, BitbucketServerEventSource]]
    calendar: Optional[Dict[str, CalendarEventSource]]
    emitter: Optional[Dict[str, EmitterEventSource]]
    event_bus_name: Optional[str]
    file: Optional[Dict[str, FileEventSource]]
    generic: Optional[Dict[str, GenericEventSource]]
    github: Optional[Dict[str, GithubEventSource]]
    gitlab: Optional[Dict[str, GitlabEventSource]]
    hdfs: Optional[Dict[str, HDFSEventSource]]
    kafka: Optional[Dict[str, KafkaEventSource]]
    minio: Optional[Dict[str, S3Artifact]]
    mqtt: Optional[Dict[str, MQTTEventSource]]
    nats: Optional[Dict[str, NATSEventsSource]]
    nsq: Optional[Dict[str, NSQEventSource]]
    pub_sub: Optional[Dict[str, PubSubEventSource]]
    pulsar: Optional[Dict[str, PulsarEventSource]]
    redis: Optional[Dict[str, RedisEventSource]]
    redis_stream: Optional[Dict[str, RedisStreamEventSource]]
    replicas: Optional[int]
    resource: Optional[Dict[str, ResourceEventSource]]
    service: Optional[Service]
    slack: Optional[Dict[str, SlackEventSource]]
    sns: Optional[Dict[str, SNSEventSource]]
    sqs: Optional[Dict[str, SQSEventSource]]
    storage_grid: Optional[Dict[str, StorageGridEventSource]]
    stripe: Optional[Dict[str, StripeEventSource]]
    template: Optional[Template]
    webhook: Optional[Dict[str, WebhookEventSource]]

class SensorSpec(BaseModel):
    dependencies: Optional[List[EventDependency]]
    error_on_failed_round: Optional[bool]
    event_bus_name: Optional[str]
    replicas: Optional[int]
    template: Optional[Template]
    triggers: Optional[List[Trigger]]

class EventSource(BaseModel):
    metadata: Optional[v1_1.ObjectMeta]
    spec: Optional[EventSourceSpec]
    status: Optional[EventSourceStatus]

class EventSourceList(BaseModel):
    items: Optional[List[EventSource]]
    metadata: Optional[v1_1.ListMeta]

class Sensor(BaseModel):
    metadata: Optional[v1_1.ObjectMeta]
    spec: Optional[SensorSpec]
    status: Optional[SensorStatus]

class SensorList(BaseModel):
    items: Optional[List[Sensor]]
    metadata: Optional[v1_1.ListMeta]

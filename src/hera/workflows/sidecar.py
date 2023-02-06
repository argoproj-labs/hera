from typing import List, Optional

from argo_workflows.models import IoArgoprojWorkflowV1alpha1UserContainer

from hera.env import Env
from hera.env_from import BaseEnvFrom
from hera.image import ImagePullPolicy
from hera.lifecycle import Lifecycle
from hera.port import ContainerPort
from hera.probe import Probe
from hera.resources import Resources
from hera.security_context import BaseSecurityContext
from hera.volumes import VolumeDevice, VolumeMount


class Sidecar:
    """Sidecar container for the main pod running a task.

    Parameters
    ----------
    name: str
        Name of the container specified as a DNS_LABEL. Each container in a pod must have a unique name (DNS_LABEL).
    args: Optional[List[str]] = None
        Arguments to the entrypoint. The docker image's CMD is used if this is not provided.
        Variable references $(VAR_NAME) are expanded using the container's environment. If a variable cannot be
        resolved, the reference in the input string will be unchanged. Double $$ are reduced to a single $, which
        allows for escaping the $(VAR_NAME) syntax: i.e. \"$$(VAR_NAME)\" will produce the string literal
        \"$(VAR_NAME)\". Escaped references will never be expanded, regardless of whether the variable exists or not.
    command: Optional[List[str]] = None
        Entrypoint array. Not executed within a shell. The docker image's ENTRYPOINT is used if this is not provided.
        Variable references $(VAR_NAME) are expanded using the container's environment. If a variable cannot be
        resolved, the reference in the input string will be unchanged. Double $$ are reduced to a single $, which
        allows for escaping the $(VAR_NAME) syntax: i.e. \"$$(VAR_NAME)\" will produce the string literal
        \"$(VAR_NAME)\". Escaped references will never be expanded, regardless of whether the variable exists or not.
    env: Optional[List[Env]] = None
        List of environment variables to set in the container
    env_from: Optional[List[BaseEnvFrom]] = None
        List of sources to populate environment variables in the container. The keys defined within a source must be
        a C_IDENTIFIER. All invalid keys will be reported as an event when the container is starting. When a key
        exists in multiple sources, the value associated with the last source will take precedence. Values defined by
        an Env with a duplicate key will take precedence.
    image: Optional[str] = None
        Docker image name. More info: https://kubernetes.io/docs/concepts/containers/images
    image_pull_policy: Optional[ImagePullPolicy] = None
        Optional image pull policy. See `ImagePullPolicy`.
    lifecycle: Optional[Lifecycle] = None
        Optional lifecycle. See `Lifecycle`.
    liveness_probe: Optional[Probe] = None
        Optional liveness probe. See `Probe`.
    mirror_volume_mounts: Optional[bool] = None
        If True, will mount the same volumes specified in the main container to the container (including artifacts),
        at the same mountPaths. This enables dind daemon to partially see the same filesystem as the main container
        in order to use features such as docker volume binding.
    ports: Optional[List[ContainerPort]] = None
        List of ports to expose from the container. Exposing a port here gives the system additional information
        about the network connections a container uses, but is primarily informational. Not specifying a port here
        DOES NOT prevent that port from being exposed. Any port which is listening on the default \"0.0.0.0\"
        address inside a container will be accessible from the network.
    readiness_probe: Optional[Probe] = None
        Optional readiness probe. See `Probe`.
    resources: Optional[Resources] = None
        Optional resources. See `Resources`.
    security_context: Optional[BaseSecurityContext] = None
        Optional security context. See `BaseSecurityContext` inheritors.
    startup_probe: Optional[Probe] = None
        Optional startup probe. See `Probe`.
    stdin: Optional[bool] = None
        Whether this container should allocate a buffer for stdin in the container runtime. If this is not set, reads
        from stdin in the container will always result in EOF.
    stdin_once: Optional[bool] = None
        Whether the container runtime should close the stdin channel after it has been opened by a single attach.
        When stdin is true the stdin stream will remain open across multiple attach sessions. If stdinOnce is set to
        true, stdin is opened on container start, is empty until the first client attaches to stdin, and then
        remains open and accepts data until the client disconnects, at which time stdin is closed and remains
        closed until the container is restarted. If this flag is false, a container processes that reads from stdin
        will never receive an EOF.
    termination_message_path: Optional[str] = None
        Path at which the file to which the container's termination message will be written is mounted into the
        container's filesystem. Message written is intended to be brief final status, such as an assertion failure
        message. Will be truncated by the node if greater than 4096 bytes. The total message length across all
        containers will be limited to 12kb.
    termination_message_policy: Optional[str] = None
        Indicate how the termination message should be populated. File will use the contents of terminationMessagePath
         to populate the container status message on both success and failure. FallbackToLogsOnError will use the
         last chunk of container log output if the termination message file is empty and the container exited with
          an error. The log output is limited to 2048 bytes or 80 lines, whichever is smaller.
    tty: Optional[bool] = None
        Whether this container should allocate a TTY for itself, also requires 'stdin' to be True.
    volume_devices: Optional[VolumeDevice] = None
        List of block devices to be used by the container.
    volume_mounts: Optional[Volume] = None
        Pod volumes to mount into the container's filesystem.
    working_dir: Optional[str] = None
        Container's working directory. If not specified, the container runtime's default will be used, which might
        be configured in the container image.
    """

    def __init__(
        self,
        name: str,
        args: Optional[List[str]] = None,
        command: Optional[List[str]] = None,
        env: Optional[List[Env]] = None,
        env_from: Optional[List[BaseEnvFrom]] = None,
        image: Optional[str] = None,
        image_pull_policy: Optional[ImagePullPolicy] = None,
        lifecycle: Optional[Lifecycle] = None,
        liveness_probe: Optional[Probe] = None,
        mirror_volume_mounts: Optional[bool] = None,
        ports: Optional[List[ContainerPort]] = None,
        readiness_probe: Optional[Probe] = None,
        resources: Optional[Resources] = None,
        security_context: Optional[BaseSecurityContext] = None,
        startup_probe: Optional[Probe] = None,
        stdin: Optional[bool] = None,
        stdin_once: Optional[bool] = None,
        termination_message_path: Optional[str] = None,
        termination_message_policy: Optional[str] = None,
        tty: Optional[bool] = None,
        volume_devices: Optional[List[VolumeDevice]] = None,
        volume_mounts: Optional[List[VolumeMount]] = None,
        working_dir: Optional[str] = None,
    ):
        self.name = name
        self.args = args
        self.command = command
        self.env = env
        self.env_from = env_from
        self.image = image
        self.image_pull_policy = image_pull_policy
        self.lifecycle = lifecycle
        self.liveness_probe = liveness_probe
        self.mirror_volume_mounts = mirror_volume_mounts
        self.ports = ports
        self.readiness_probe = readiness_probe
        self.resources = resources
        self.security_context = security_context
        self.startup_probe = startup_probe
        self.stdin = stdin
        self.stdin_once = stdin_once
        self.termination_message_path = termination_message_path
        self.termination_message_policy = termination_message_policy
        self.tty = tty
        self.volume_devices = volume_devices
        self.volume_mounts = volume_mounts
        self.working_dir = working_dir

    def build(self) -> IoArgoprojWorkflowV1alpha1UserContainer:
        container = IoArgoprojWorkflowV1alpha1UserContainer(self.name)
        if self.args is not None:
            setattr(container, 'args', self.args)
        if self.command is not None:
            setattr(container, 'command', self.command)
        if self.env is not None:
            setattr(container, 'env', [e.build() for e in self.env])
        if self.env_from is not None:
            setattr(container, 'env_from', [e.build() for e in self.env_from])
        if self.image is not None:
            setattr(container, 'image', self.image)
        if self.image_pull_policy is not None:
            setattr(container, 'image_pull_policy', self.image_pull_policy.value)
        if self.lifecycle is not None:
            setattr(container, 'lifecycle', self.lifecycle.build())
        if self.liveness_probe is not None:
            setattr(container, 'liveness_probe', self.liveness_probe.build())
        if self.mirror_volume_mounts is not None:
            setattr(container, 'mirror_volume_mounts', self.mirror_volume_mounts)
        if self.ports is not None:
            setattr(container, 'ports', [p.build() for p in self.ports])
        if self.readiness_probe is not None:
            setattr(container, "readiness_probe", self.readiness_probe.build())
        if self.resources is not None:
            setattr(container, "resources", self.resources.build())
        if self.security_context is not None:
            setattr(container, "security_context", self.security_context.build())
        if self.startup_probe is not None:
            setattr(container, "startup_probe", self.startup_probe.build())
        if self.stdin is not None:
            setattr(container, "stdin", self.stdin)
        if self.stdin_once is not None:
            setattr(container, "stdin_once", self.stdin_once)
        if self.termination_message_path is not None:
            setattr(container, "termination_message_path", self.termination_message_path)
        if self.termination_message_policy is not None:
            setattr(container, "termination_message_policy", self.termination_message_policy)
        if self.tty is not None:
            setattr(container, "tty", self.tty)
        if self.volume_devices is not None:
            setattr(container, "volume_devices", [vd.build() for vd in self.volume_devices])
        if self.volume_mounts is not None:
            setattr(container, "volume_mounts", [vm._build_mount() for vm in self.volume_mounts])
        if self.working_dir:
            setattr(container, "working_dir", self.working_dir)
        return container

from argo_workflows.models import IoArgoprojWorkflowV1alpha1UserContainer
from hera.env import Env
from hera.env_from import BaseEnvFrom
from hera.image import ImagePullPolicy
from typing import Optional, List
from hera.security_context import BaseSecurityContext
from hera.volumes import Volume

class VolumeDevice:
    pass
class Lifecycle:
    pass

class Probe:
    pass

class ContainerPort:
    pass

class Sidecar:
    def __init__(
        self,
        name: str,
        args: Optional[List[str]],
        command: Optional[List[str]],
        env: Optional[List[Env]],
        env_from:Optional[List[BaseEnvFrom]],
        image:Optional[str],
        image_pull_policy:Optional[ImagePullPolicy],
        lifecycle: Lifecycle,
    ):
        pass
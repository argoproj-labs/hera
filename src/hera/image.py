from enum import Enum


class ImagePullPolicy(str, Enum):
    """A representations of the pull policy for a container and the tag of the image affect.

    This influences K8S's behavior when the kubelet attempts to pull (download) the specified image.
    """

    Always = "Always"
    Never = "Never"
    IfNotPresent = "IfNotPresent"

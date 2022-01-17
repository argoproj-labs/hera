from typing import Optional

from pydantic import BaseModel


class Toleration(BaseModel):
    """Toleration is a representation of a Kubernetes toleration:
    https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/

    This can be used on tasks to make pods that run the task be scheduled on specific nodes in a K8S cluster. This is
    valuable for scheduling tasks that need to use GPUs.

    Attributes
    ----------
    key: str
        The key used to taint a node with a specific value.
    effect: str
        The effect that will occur if the key/operator/value is not satisfied.
    operator: str
        The operator to use when matching the key to the value.
    value: str
        The value to scan for matching against a taint.

    return V1Toleration(key='nvidia.com/gpu', effect='NoSchedule', operator='Equal', value='present')
    """

    key: str
    effect: str
    operator: str
    value: Optional[str] = None


GPUToleration = Toleration(key='nvidia.com/gpu', effect='NoSchedule', operator='Equal', value='present')
"""GPUToleration denotes a GPU toleration. This works on GKE and Azure but not necessarily on platforms like AWS"""

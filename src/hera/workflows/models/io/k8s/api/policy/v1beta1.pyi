from ...apimachinery.pkg.apis.meta import v1 as v1
from ...apimachinery.pkg.util import intstr as intstr
from hera.shared._base_model import BaseModel as BaseModel
from typing import Optional

class PodDisruptionBudgetSpec(BaseModel):
    max_unavailable: Optional[intstr.IntOrString]
    min_available: Optional[intstr.IntOrString]
    selector: Optional[v1.LabelSelector]

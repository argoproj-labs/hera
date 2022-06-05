from enum import Enum
from typing import Dict, List, Optional

from argo_workflows.models import Affinity as ArgoAffinity
from argo_workflows.models import LabelSelector as ArgoLabelSelector
from argo_workflows.models import (
    LabelSelectorRequirement as ArgoLabelSelectorRequirement,
)
from argo_workflows.models import NodeAffinity as ArgoNodeAffinity
from argo_workflows.models import NodeSelector as ArgoNodeSelector
from argo_workflows.models import NodeSelectorRequirement as ArgoNodeSelectorRequirement
from argo_workflows.models import NodeSelectorTerm as ArgoNodeSelectorTerm
from argo_workflows.models import PodAffinity as ArgoPodAffinity
from argo_workflows.models import PodAffinityTerm as ArgoPodAffinityTerm
from argo_workflows.models import PodAntiAffinity as ArgoPodAntiAffinity
from argo_workflows.models import PreferredSchedulingTerm as ArgoPreferredSchedulingTerm
from argo_workflows.models import WeightedPodAffinityTerm as ArgoWeightedPodAffinityTerm


class LabelOperator(Enum):
    In = 'In'
    NotIn = 'NotIn'
    Exists = 'Exists'
    DoesNotExist = 'DoesNotExist'


class NodeSelectorRequirement:
    def __init__(self, key: str, operator: LabelOperator, values: Optional[List[str]] = None) -> None:
        self.key = key
        self.operator = operator
        self.values = values

    def get_spec(self) -> Optional[ArgoNodeSelectorRequirement]:
        if self.values:
            return ArgoNodeSelectorRequirement(
                key=self.key,
                operator=self.operator.value,
                values=self.values,
            )
        return ArgoNodeSelectorRequirement(
            key=self.key,
            operator=self.operator.value,
        )


Expression = NodeSelectorRequirement
Field = NodeSelectorRequirement


class NodeSelectorTerm:
    def __init__(self, expressions: Optional[List[Expression]] = None, fields: Optional[List[Field]] = None) -> None:
        self.expressions = expressions
        self.fields = fields

    def get_spec(self) -> Optional[ArgoNodeSelectorTerm]:
        if self.expressions is not None or self.fields is not None:
            match_expressions = [expression.get_spec() for expression in self.expressions]
            match_fields = [field.get_spec() for field in self.fields]
            return ArgoNodeSelectorTerm(
                match_expressions=match_expressions if any(match_expressions) else None,
                match_fields=match_fields if any(match_fields) else None,
            )
        return None


class PreferredSchedulingTerm:
    def __init__(self, node_selector_term: NodeSelectorTerm, weight: int) -> None:
        self.node_selector_term = node_selector_term
        self.weight = weight

    def get_spec(self) -> Optional[ArgoPreferredSchedulingTerm]:
        node_selector_term = self.node_selector_term.get_spec()
        if node_selector_term is not None:
            return ArgoPreferredSchedulingTerm(
                preference=node_selector_term,
                weight=self.weight,
            )
        return None


class LabelSelectorRequirement:
    def __init__(self, key: str, operator: LabelOperator, values: Optional[List[str]] = None) -> None:
        self.key = key
        self.operator = operator
        self.values = values

    def get_spec(self) -> ArgoLabelSelectorRequirement:
        if self.values is not None:
            return ArgoLabelSelectorRequirement(
                key=self.key,
                operator=self.operator.value,
                values=self.values,
            )
        return ArgoLabelSelectorRequirement(
            key=self.key,
            operator=self.operator.value,
        )


class LabelSelector:
    match_expressions: List[LabelSelectorRequirement] = []
    match_labels: Dict[str, str] = {}

    def __init__(
        self,
        match_expressions: Optional[List[LabelSelectorRequirement]] = None,
        match_labels: Optional[Dict[str, str]] = None,
    ) -> None:
        self.match_expressions = match_expressions
        self.match_labels = match_labels

    def get_spec(self) -> Optional[ArgoLabelSelector]:
        match_expressions = [expression.get_spec() for expression in self.match_expressions]
        if any(self.match_expressions) is not None or self.match_labels is not None:
            return ArgoLabelSelector(
                match_expressions=match_expressions if any(match_expressions) else None,
                match_labels=self.match_labels if self.match_labels else None,
            )
        return None


class PodAffinityTerm:
    def __init__(
        self,
        topology_key: str,
        label_selector: Optional[LabelSelector] = None,
        namespace_selector: Optional[LabelSelector] = None,
        namespaces: Optional[List[str]] = None,
    ) -> None:
        self.topology_key = topology_key
        self.label_selector = label_selector
        self.namespace_selector = namespace_selector
        self.namespaces = namespaces

    def get_spec(self) -> Optional[ArgoPodAffinityTerm]:
        term = ArgoPodAffinityTerm(topology_key=self.topology_key)
        if self.label_selector is not None:
            setattr(term, 'label_selector', self.label_selector.get_spec())
        if self.namespace_selector is not None:
            setattr(term, 'namespace_selector', self.namespace_selector.get_spec())
        if self.namespaces is not None:
            setattr(term, 'namespaces', self.namespaces)
        if hasattr(term, 'label_selector') or hasattr(term, 'namespace_selector') or hasattr(term, 'namespaces'):
            return term
        return None


class WeightedPodAffinityTerm:
    def __init__(
        self,
        pod_affinity_term: PodAffinityTerm,
        weight: int,
    ):
        self.pod_affinity_term = pod_affinity_term
        self.weight = weight

    def get_spec(self) -> ArgoWeightedPodAffinityTerm:
        return ArgoWeightedPodAffinityTerm(
            pod_affinity_term=self.pod_affinity_term.get_spec(),
            weight=self.weight,
        )


class PodAffinity:
    def __init__(
        self,
        preferred_during_scheduling_ignored_during_execution: Optional[List[WeightedPodAffinityTerm]] = None,
        required_during_scheduling_ignored_during_execution: Optional[List[PodAffinityTerm]] = None,
    ) -> None:
        self.preferred_during_scheduling_ignored_during_execution = (
            preferred_during_scheduling_ignored_during_execution
        )
        self.required_during_scheduling_ignored_during_execution = required_during_scheduling_ignored_during_execution

    def get_spec(self) -> Optional[ArgoPodAffinity]:
        if (
            self.preferred_during_scheduling_ignored_during_execution is not None
            or self.required_during_scheduling_ignored_during_execution is not None
        ):
            affinity = ArgoPodAffinity()
            preferred_during_scheduling_ignored_during_execution = [
                term.get_spec() for term in self.preferred_during_scheduling_ignored_during_execution
            ]
            required_during_scheduling_ignored_during_execution = [
                term.get_spec() for term in self.required_during_scheduling_ignored_during_execution
            ]
            if any(preferred_during_scheduling_ignored_during_execution):
                setattr(affinity, 'preferred_during_scheduling_ignored_during_execution',
                        preferred_during_scheduling_ignored_during_execution)
            if any(required_during_scheduling_ignored_during_execution):
                setattr(affinity, 'required_during_scheduling_ignored_during_execution',
                        required_during_scheduling_ignored_during_execution)
            if hasattr(affinity, 'preferred_during_scheduling_ignored_during_execution') or hasattr(affinity,
                                                                                                    'required_during_scheduling_ignored_during_execution'):
                return affinity
            return None


class PodAntiAffinity:
    def __init__(
        self,
        preferred_during_scheduling_ignored_during_execution: Optional[List[WeightedPodAffinityTerm]] = None,
        required_during_scheduling_ignored_during_execution: Optional[List[PodAffinityTerm]] = None,
    ) -> None:
        self.preferred_during_scheduling_ignored_during_execution = (
            preferred_during_scheduling_ignored_during_execution
        )
        self.required_during_scheduling_ignored_during_execution = required_during_scheduling_ignored_during_execution

    def get_spec(self) -> Optional[ArgoPodAntiAffinity]:
        if (
            self.preferred_during_scheduling_ignored_during_execution is not None
            or self.required_during_scheduling_ignored_during_execution is not None
        ):
            return ArgoPodAntiAffinity(
                preferred_during_scheduling_ignored_during_execution=[
                    term.get_spec() for term in self.preferred_during_scheduling_ignored_during_execution
                ]
                if self.preferred_during_scheduling_ignored_during_execution is not None
                else None,
                required_during_scheduling_ignored_during_execution=[
                    term.get_spec() for term in self.required_during_scheduling_ignored_during_execution
                ]
                if self.required_during_scheduling_ignored_during_execution is not None
                else None,
            )
        return None


class NodeAffinity:
    def __init__(
        self,
        preferred_during_scheduling_ignored_during_execution: Optional[List[PreferredSchedulingTerm]] = None,
        required_during_scheduling_ignored_during_execution: Optional[NodeSelectorTerm] = None,
    ) -> None:
        self.preferred_during_scheduling_ignored_during_execution = (
            preferred_during_scheduling_ignored_during_execution
        )
        self.required_during_scheduling_ignored_during_execution = required_during_scheduling_ignored_during_execution

    def get_spec(self) -> Optional[ArgoNodeAffinity]:
        if (
            self.preferred_during_scheduling_ignored_during_execution is not None
            or self.required_during_scheduling_ignored_during_execution is not None
        ):
            return ArgoNodeAffinity(
                preferred_during_scheduling_ignored_during_execution=[
                    term.get_spec() for term in self.preferred_during_scheduling_ignored_during_execution
                ]
                if self.preferred_during_scheduling_ignored_during_execution
                else None,
                required_during_scheduling_ignored_during_execution=(
                    self.required_during_scheduling_ignored_during_execution.get_spec()
                )
                if self.required_during_scheduling_ignored_during_execution
                else None,
            )
        return None


class Affinity:
    def __init__(
        self,
        pod_affinity: Optional[PodAffinity] = None,
        pod_anti_affinity: Optional[PodAntiAffinity] = None,
        node_affinity: Optional[NodeAffinity] = None,
    ) -> None:
        self.pod_affinity = pod_affinity
        self.pod_anti_affinity = pod_anti_affinity
        self.node_affinity = node_affinity

    def get_spec(self) -> Optional[ArgoAffinity]:
        if self.pod_affinity is not None or self.pod_anti_affinity is not None or self.node_affinity is not None:
            return ArgoAffinity(
                pod_affinity=self.pod_affinity.get_spec() if self.pod_affinity else None,
                pod_anti_affinity=self.pod_anti_affinity.get_spec() if self.pod_anti_affinity else None,
                node_affinity=self.node_affinity.get_spec() if self.node_affinity else None,
            )
        return None

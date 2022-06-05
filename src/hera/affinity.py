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


class NodeSelectorRequirement:
    def __init__(self, values: Optional[List[str]]) -> None:
        self.values = values

    def get_spec(self) -> ArgoNodeSelectorRequirement:
        return ArgoNodeSelectorRequirement(values=self.values)


Expression = NodeSelectorRequirement
Field = NodeSelectorRequirement


class NodeSelectorTerm:
    def __init__(self, expressions: Optional[List[Expression]], fields: Optional[List[Field]] = None) -> None:
        self.expressions = expressions
        self.fields = fields

    def get_spec(self) -> ArgoNodeSelectorTerm:
        return ArgoNodeSelectorTerm(
            match_expressions=[expression.get_spec() for expression in self.expressions],
            match_fields=[field.get_spec() for field in self.fields],
        )


class PreferredSchedulingTerm:
    def __init__(self, node_selector_terms: List[NodeSelectorTerm], weight: int) -> None:
        self.node_selector_terms = node_selector_terms
        self.weight = weight

    def get_spec(self) -> ArgoPreferredSchedulingTerm:
        return ArgoPreferredSchedulingTerm(
            preference=ArgoNodeSelector(node_selector_terms=[term.get_spec() for term in self.node_selector_terms]),
            weight=self.weight,
        )


class LabelOperator(Enum):
    In = 'In'
    NotIn = 'NotIn'
    Exists = 'Exists'
    DoesNotExist = 'DoesNotExist'


class LabelSelectorRequirement:
    def __init__(self, key: str, operator: LabelOperator, values: Optional[List[str]] = None) -> None:
        self.key = key
        self.operator = operator
        self.values = values

    def get_spec(self) -> ArgoLabelSelectorRequirement:
        return ArgoLabelSelectorRequirement(
            key=self.key,
            operator=self.operator.value,
            values=self.values,
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

    def get_spec(self) -> ArgoLabelSelector:
        return ArgoLabelSelector(
            match_expressions=[expression.get_spec() for expression in self.match_expressions]
            if self.match_expressions
            else None,
            match_labels=self.match_labels if self.match_labels else None,
        )


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

    def get_spec(self) -> ArgoPodAffinityTerm:
        return ArgoPodAffinityTerm(
            topology_key=self.topology_key,
            label_selector=self.label_selector.get_spec() if self.label_selector else None,
            namespace_selector=self.namespace_selector.get_spec() if self.namespace_selector else None,
            namespaces=self.namespaces,
        )


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

    def get_spec(self) -> ArgoPodAffinity:
        return ArgoPodAffinity(
            preferred_during_scheduling_ignored_during_execution=[
                term.get_spec() for term in self.preferred_during_scheduling_ignored_during_execution
            ]
            if self.preferred_during_scheduling_ignored_during_execution
            else None,
            required_during_scheduling_ignored_during_execution=[
                term.get_spec() for term in self.required_during_scheduling_ignored_during_execution
            ]
            if self.required_during_scheduling_ignored_during_execution
            else None,
        )


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

    def get_spec(self) -> ArgoPodAntiAffinity:
        return ArgoPodAntiAffinity(
            preferred_during_scheduling_ignored_during_execution=[
                term.get_spec() for term in self.preferred_during_scheduling_ignored_during_execution
            ]
            if self.preferred_during_scheduling_ignored_during_execution
            else None,
            required_during_scheduling_ignored_during_execution=[
                term.get_spec() for term in self.required_during_scheduling_ignored_during_execution
            ]
            if self.required_during_scheduling_ignored_during_execution
            else None,
        )


class NodeAffinity:
    def __init__(
        self,
        preferred_during_scheduling_ignored_during_execution: Optional[List[PreferredSchedulingTerm]] = [],
        required_during_scheduling_ignored_during_execution: Optional[NodeSelectorTerm] = None,
    ) -> None:
        self.preferred_during_scheduling_ignored_during_execution = (
            preferred_during_scheduling_ignored_during_execution
        )
        self.required_during_scheduling_ignored_during_execution = required_during_scheduling_ignored_during_execution

    def get_spec(self) -> ArgoNodeAffinity:
        return ArgoNodeAffinity(
            preferred_during_scheduling_ignored_during_execution=[
                term.get_spec() for term in self.preferred_during_scheduling_ignored_during_execution
            ],
            required_during_scheduling_ignored_during_execution=(
                self.required_during_scheduling_ignored_during_execution.get_spec()
            ),
        )


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

    def get_spec(self) -> ArgoAffinity:
        return ArgoAffinity(
            pod_affinity=self.pod_affinity.get_spec() if self.pod_affinity else None,
            pod_anti_affinity=self.pod_anti_affinity.get_spec() if self.pod_anti_affinity else None,
            node_affinity=self.node_affinity.get_spec() if self.node_affinity else None,
        )

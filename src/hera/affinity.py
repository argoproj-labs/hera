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
    In = "In"
    NotIn = "NotIn"
    Exists = "Exists"
    DoesNotExist = "DoesNotExist"


class NodeSelectorRequirement:
    """Builds the K8S node selector requirement.

    See also
    --------
        https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity
    """

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
    """Builds the K8S node selector term.

    See also
    --------
        https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity
    """

    def __init__(self, expressions: Optional[List[Expression]] = None, fields: Optional[List[Field]] = None) -> None:
        self.expressions = expressions
        self.fields = fields

    def get_spec(self) -> Optional[ArgoNodeSelectorTerm]:
        term = ArgoNodeSelectorTerm()

        if self.expressions is not None:
            match_expressions = [expression.get_spec() for expression in self.expressions]
            if any(match_expressions):
                setattr(term, "match_expressions", match_expressions)

        if self.fields is not None:
            match_fields = [field.get_spec() for field in self.fields]
            if any(match_fields):
                setattr(term, "match_fields", match_fields)

        if hasattr(term, "match_expressions") or hasattr(term, "match_fields"):
            return term
        return None


class PreferredSchedulingTerm:
    """Builds the K8S preferred scheduling term.

    See also
    --------
        https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity
    """

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
    """Builds the K8S label selector requirement.

    See also
    --------
        https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity
    """

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
    """Builds the K8S label selector.

    See also
    --------
        https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity
    """

    def __init__(
        self,
        label_selector_requirements: Optional[List[LabelSelectorRequirement]] = None,
        match_labels: Optional[Dict[str, str]] = None,
    ) -> None:
        self.label_selector_requirements = label_selector_requirements
        self.match_labels = match_labels

    def get_spec(self) -> Optional[ArgoLabelSelector]:
        selector = ArgoLabelSelector()

        if self.label_selector_requirements is not None:
            match_expressions = [expression.get_spec() for expression in self.label_selector_requirements]
            if any(match_expressions):
                setattr(selector, "match_expressions", match_expressions)

        if self.match_labels is not None:
            setattr(selector, "match_labels", self.match_labels)

        if hasattr(selector, "match_expressions") or hasattr(selector, "match_labels"):
            return selector
        return None


class PodAffinityTerm:
    """Builds the K8S pod affinity term.

    See also
    --------
        https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity
    """

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
            setattr(term, "label_selector", self.label_selector.get_spec())

        if self.namespace_selector is not None:
            setattr(term, "namespace_selector", self.namespace_selector.get_spec())

        if self.namespaces is not None:
            setattr(term, "namespaces", self.namespaces)

        if hasattr(term, "label_selector") or hasattr(term, "namespace_selector") or hasattr(term, "namespaces"):
            return term
        return None


class WeightedPodAffinityTerm:
    """Builds the K8S weighted pod affinity term.

    See also
    --------
        https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity
    """

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
    """Builds the K8S pod affinity.

    See also
    --------
        https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity
    """

    def __init__(
        self,
        weighted_pod_affinities: Optional[List[WeightedPodAffinityTerm]] = None,
        pod_affinity_terms: Optional[List[PodAffinityTerm]] = None,
    ) -> None:
        self.weighted_pod_affinities = weighted_pod_affinities
        self.pod_affinity_terms = pod_affinity_terms

    def get_spec(self) -> Optional[ArgoPodAffinity]:
        affinity = ArgoPodAffinity()

        if self.weighted_pod_affinities is not None:
            preferred_during_scheduling_ignored_during_execution = [
                term.get_spec() for term in self.weighted_pod_affinities
            ]
            if any(preferred_during_scheduling_ignored_during_execution):
                setattr(
                    affinity,
                    "preferred_during_scheduling_ignored_during_execution",
                    preferred_during_scheduling_ignored_during_execution,
                )

        if self.pod_affinity_terms:
            required_during_scheduling_ignored_during_execution = [term.get_spec() for term in self.pod_affinity_terms]
            if any(required_during_scheduling_ignored_during_execution):
                setattr(
                    affinity,
                    "required_during_scheduling_ignored_during_execution",
                    required_during_scheduling_ignored_during_execution,
                )

        if hasattr(affinity, "preferred_during_scheduling_ignored_during_execution") or hasattr(
            affinity, "required_during_scheduling_ignored_during_execution"
        ):
            return affinity
        return None


class PodAntiAffinity:
    """Builds the K8S pod anti-affinity.

    See also
    --------
        https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity
    """

    def __init__(
        self,
        weighted_pod_affinities: Optional[List[WeightedPodAffinityTerm]] = None,
        pod_affinity_terms: Optional[List[PodAffinityTerm]] = None,
    ) -> None:
        self.weighted_pod_affinities = weighted_pod_affinities
        self.pod_affinity_terms = pod_affinity_terms

    def get_spec(self) -> Optional[ArgoPodAntiAffinity]:
        affinity = ArgoPodAntiAffinity()

        if self.weighted_pod_affinities is not None:
            preferred_during_scheduling_ignored_during_execution = [
                term.get_spec() for term in self.weighted_pod_affinities
            ]
            if any(preferred_during_scheduling_ignored_during_execution):
                setattr(
                    affinity,
                    "preferred_during_scheduling_ignored_during_execution",
                    preferred_during_scheduling_ignored_during_execution,
                )

        if self.pod_affinity_terms is not None:
            required_during_scheduling_ignored_during_execution = [term.get_spec() for term in self.pod_affinity_terms]
            if any(required_during_scheduling_ignored_during_execution):
                setattr(
                    affinity,
                    "required_during_scheduling_ignored_during_execution",
                    required_during_scheduling_ignored_during_execution,
                )

        if hasattr(affinity, "preferred_during_scheduling_ignored_during_execution") or hasattr(
            affinity, "required_during_scheduling_ignored_during_execution"
        ):
            return affinity
        return None


class NodeSelector:
    """Builds the K8S node selector.

    See also
    --------
        https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity
    """

    def __init__(self, terms: Optional[List[NodeSelectorTerm]] = None):
        self.terms = terms

    def get_spec(self) -> Optional[ArgoNodeSelector]:
        if self.terms is not None:
            terms = [term.get_spec() if term else None for term in self.terms]
            if any(terms):
                return ArgoNodeSelector(node_selector_terms=terms)
        return None


class NodeAffinity:
    """Builds the K8S node affinity.

    See also
    --------
        https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity
    """

    def __init__(
        self,
        preferred_scheduling_terms: Optional[List[PreferredSchedulingTerm]] = None,
        node_selector: Optional[NodeSelector] = None,
    ) -> None:
        self.preferred_scheduling_terms = preferred_scheduling_terms
        self.node_selector = node_selector

    def get_spec(self) -> Optional[ArgoNodeAffinity]:
        affinity = ArgoNodeAffinity()

        if self.preferred_scheduling_terms is not None:
            preferred_during_scheduling_ignored_during_execution = [
                term.get_spec() for term in self.preferred_scheduling_terms
            ]
            if any(preferred_during_scheduling_ignored_during_execution):
                setattr(
                    affinity,
                    "preferred_during_scheduling_ignored_during_execution",
                    preferred_during_scheduling_ignored_during_execution,
                )

        if self.node_selector is not None:
            required_during_scheduling_ignored_during_execution = self.node_selector.get_spec()
            if required_during_scheduling_ignored_during_execution:
                setattr(
                    affinity,
                    "required_during_scheduling_ignored_during_execution",
                    required_during_scheduling_ignored_during_execution,
                )

        if hasattr(affinity, "preferred_during_scheduling_ignored_during_execution") or hasattr(
            affinity, "required_during_scheduling_ignored_during_execution"
        ):
            return affinity
        return None


class Affinity:
    """Builds the K8S affinity.

    See also
    --------
        https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity
    """

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
        affinity = ArgoAffinity()

        if self.pod_affinity is not None:
            pod_affinity = self.pod_affinity.get_spec()
            setattr(affinity, "pod_affinity", pod_affinity)

        if self.pod_anti_affinity is not None:
            pod_anti_affinity = self.pod_anti_affinity.get_spec()
            setattr(affinity, "pod_anti_affinity", pod_anti_affinity)

        if self.node_affinity is not None:
            node_affinity = self.node_affinity.get_spec()
            setattr(affinity, "node_affinity", node_affinity)

        if (
            hasattr(affinity, "pod_affinity")
            or hasattr(affinity, "pod_anti_affinity")
            or hasattr(affinity, "node_affinity")
        ):
            return affinity
        return None

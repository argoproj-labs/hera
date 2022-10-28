from enum import Enum
from typing import Dict, List, Optional, Union

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


class LabelOperator(str, Enum):
    """Collection of valid labels for node selectors"""

    In = "In"
    NotIn = "NotIn"
    Exists = "Exists"
    DoesNotExist = "DoesNotExist"

    def __str__(self):
        return str(self.value)


class NodeSelectorRequirement:
    """Builds the K8S node selector requirement.

    Parameters
    ----------
    key: str
        String key to use for the node selector.
    operator: Union[LabelOperator, str]
        A representation of the operator to use for selector assembly.
    values: Optional[List[str]] = None
        An optional list of values to assemble for the key to match, as dictated by the operator.

    Notes
    -----
    See https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity
    """

    def __init__(self, key: str, operator: Union[LabelOperator, str], values: Optional[List[str]] = None) -> None:
        self.key = key
        self.operator: str = str(operator)
        self.values = values

    def _build(self) -> Optional[ArgoNodeSelectorRequirement]:
        """Assembles the Argo node selector requirement"""
        if self.values is not None:
            return ArgoNodeSelectorRequirement(
                key=self.key,
                operator=self.operator,
                values=self.values,
            )
        return ArgoNodeSelectorRequirement(
            key=self.key,
            operator=self.operator,
        )


Expression = NodeSelectorRequirement
Field = NodeSelectorRequirement


class NodeSelectorTerm:
    """Builds the K8S node selector term.

    Parameters
    ----------
    expressions: Optional[List[Expression]] = None
        A list of expressions for the node selector term to match. See `hera.affinity.NodeSelectorRequirement`.
    fields: Optional[List[Field]] = None
        A list of fields for the node selector term to match. See `hera.affinity.NodeSelectorRequirement`.

    Notes
    -----
    See: https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity
    """

    def __init__(self, expressions: Optional[List[Expression]] = None, fields: Optional[List[Field]] = None) -> None:
        self.expressions = expressions
        self.fields = fields

    def _build(self) -> Optional[ArgoNodeSelectorTerm]:
        """Assembles the Argo node selector term"""
        term = ArgoNodeSelectorTerm()

        if self.expressions is not None:
            match_expressions = [expression._build() for expression in self.expressions]
            if any(match_expressions):
                setattr(term, "match_expressions", match_expressions)

        if self.fields is not None:
            match_fields = [field._build() for field in self.fields]
            if any(match_fields):
                setattr(term, "match_fields", match_fields)

        if hasattr(term, "match_expressions") or hasattr(term, "match_fields"):
            return term
        return None


class PreferredSchedulingTerm:
    """Builds the K8S preferred scheduling term.

    Parameters
    ----------
    node_selector_term: NodeSelectorTerm
        The node selector term for node selector assembly. See also `hera.affinity.NodeSelectorTerm`.
    weight: int
        Integer weight for the scheduling term. This is supposed to be between 1 and 100.

    Notes
    -----
    See: https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity
    """

    def __init__(self, node_selector_term: NodeSelectorTerm, weight: int) -> None:
        self.node_selector_term = node_selector_term
        assert 1 <= weight <= 100, "Node selector weight for scheduling term preference should be between 1 and 100"
        self.weight = weight

    def _build(self) -> Optional[ArgoPreferredSchedulingTerm]:
        """Assembles the Argo preferred scheduling term"""
        node_selector_term = self.node_selector_term._build()
        if node_selector_term is not None:
            return ArgoPreferredSchedulingTerm(
                preference=node_selector_term,
                weight=self.weight,
            )
        return None


class LabelSelectorRequirement:
    """Builds the K8S label selector requirement.

    Parameters
    ----------
    key: str
        String key to use for the label selector.
    operator: Union[LabelOperator, str]
        A representation of the operator to use for selector assembly.
    values: Optional[List[str]] = None
        An optional list of values to assemble for the key to match, as dictated by the operator.

    Notes
    -----
    See: https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity
    """

    def __init__(self, key: str, operator: Union[LabelOperator, str], values: Optional[List[str]] = None) -> None:
        self.key = key
        self.operator: str = str(operator)
        self.values = values

    def _build(self) -> ArgoLabelSelectorRequirement:
        """Assembles the Argo label selector requirement"""
        if self.values is not None:
            return ArgoLabelSelectorRequirement(
                key=self.key,
                operator=self.operator,
                values=self.values,
            )
        return ArgoLabelSelectorRequirement(
            key=self.key,
            operator=self.operator,
        )


class LabelSelector:
    """Builds the K8S label selector.

    Parameters
    ----------
    label_selector_requirements: Optional[List[LabelSelectorRequirement]] = None
        A list of label selector requirements. See `hera.affinity.LabelSelectorRequirement`.
    match_labels: Optional[Dict[str, str]] = None
        A list of labels to match, in the form of key value pairs.

    Notes
    -----
    See: https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity
    """

    def __init__(
        self,
        label_selector_requirements: Optional[List[LabelSelectorRequirement]] = None,
        match_labels: Optional[Dict[str, str]] = None,
    ) -> None:
        self.label_selector_requirements = label_selector_requirements
        self.match_labels = match_labels

    def _build(self) -> Optional[ArgoLabelSelector]:
        """Assembles the Argo label selector"""
        selector = ArgoLabelSelector()

        if self.label_selector_requirements is not None:
            match_expressions = [expression._build() for expression in self.label_selector_requirements]
            if any(match_expressions):
                setattr(selector, "match_expressions", match_expressions)

        if self.match_labels is not None:
            setattr(selector, "match_labels", self.match_labels)

        if hasattr(selector, "match_expressions") or hasattr(selector, "match_labels"):
            return selector
        return None


class PodAffinityTerm:
    """Builds the K8S pod affinity term.

    Parameters
    ----------
    topology_key: str
        The topology key to use for pod affinity.
    label_selector: Optional[LabelSelector] = None
        The label selector. See also `hera.affinity.LabelSelector`.
    namespace_selector: Optional[LabelSelector] = None
        The namespace selector as a label selector. See also `hera.affinity.LabelSelector`.
    namespaces: Optional[List[str]] = None
        Namespace to match pod affinity term in.

    Notes
    -----
    See: https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity
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

    def _build(self) -> Optional[ArgoPodAffinityTerm]:
        """Assembles the pod affinity term"""
        term = ArgoPodAffinityTerm(topology_key=self.topology_key)

        if self.label_selector is not None:
            setattr(term, "label_selector", self.label_selector._build())

        if self.namespace_selector is not None:
            setattr(term, "namespace_selector", self.namespace_selector._build())

        if self.namespaces is not None:
            setattr(term, "namespaces", self.namespaces)

        if hasattr(term, "label_selector") or hasattr(term, "namespace_selector") or hasattr(term, "namespaces"):
            return term
        return None


class WeightedPodAffinityTerm:
    """Builds the K8S weighted pod affinity term.

    Parameters
    ----------
    pod_affinity_term: PodAffinityTerm
        The pod affinity term. See also `hera.affinity.PodAffinityTerm`.
    weight: int
        The weight of the pod affinity term. This should be between 1 and 100.

    Notes
    -----
    See: https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity
    """

    def __init__(
        self,
        pod_affinity_term: PodAffinityTerm,
        weight: int,
    ):
        self.pod_affinity_term = pod_affinity_term
        assert 1 <= weight <= 100, "Pod affinity term weight should be between 1 and 100"
        self.weight = weight

    def _build(self) -> ArgoWeightedPodAffinityTerm:
        """Assembles the weighted pod affinity term"""
        return ArgoWeightedPodAffinityTerm(
            pod_affinity_term=self.pod_affinity_term._build(),
            weight=self.weight,
        )


class PodAffinity:
    """Builds the K8S pod affinity.

    Parameters
    ----------
    weighted_pod_affinities: Optional[List[WeightedPodAffinityTerm]] = None
        Optional list of weighted pod affinity terms. See also `hera.affinity.WeightedPodAffinityTerm`.
    pod_affinity_terms: Optional[List[PodAffinityTerm]] = None
        Optional list of pod affinity terms. See also `hera.affinity.PodAffinityTerm`.

    Notes
    -----
    See: https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity
    """

    def __init__(
        self,
        weighted_pod_affinities: Optional[List[WeightedPodAffinityTerm]] = None,
        pod_affinity_terms: Optional[List[PodAffinityTerm]] = None,
    ) -> None:
        self.weighted_pod_affinities = weighted_pod_affinities
        self.pod_affinity_terms = pod_affinity_terms

    def _build(self) -> Optional[ArgoPodAffinity]:
        """Assembles the pod affinity"""
        affinity = ArgoPodAffinity()

        if self.weighted_pod_affinities is not None:
            preferred_during_scheduling_ignored_during_execution = [
                term._build() for term in self.weighted_pod_affinities
            ]
            if any(preferred_during_scheduling_ignored_during_execution):
                setattr(
                    affinity,
                    "preferred_during_scheduling_ignored_during_execution",
                    preferred_during_scheduling_ignored_during_execution,
                )

        if self.pod_affinity_terms:
            required_during_scheduling_ignored_during_execution = [term._build() for term in self.pod_affinity_terms]
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

    weighted_pod_affinities: Optional[List[WeightedPodAffinityTerm]] = None
        Optional list of weighted pod affinity terms. See also `hera.affinity.WeightedPodAffinityTerm`.
    pod_affinity_terms: Optional[List[PodAffinityTerm]] = None
        Optional list of pod affinity terms. See also `hera.affinity.PodAffinityTerm`.

    Notes
    -----
    See: https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity
    """

    def __init__(
        self,
        weighted_pod_affinities: Optional[List[WeightedPodAffinityTerm]] = None,
        pod_affinity_terms: Optional[List[PodAffinityTerm]] = None,
    ) -> None:
        self.weighted_pod_affinities = weighted_pod_affinities
        self.pod_affinity_terms = pod_affinity_terms

    def _build(self) -> Optional[ArgoPodAntiAffinity]:
        """Assembles the pod anti affinity"""
        affinity = ArgoPodAntiAffinity()

        if self.weighted_pod_affinities is not None:
            preferred_during_scheduling_ignored_during_execution = [
                term._build() for term in self.weighted_pod_affinities
            ]
            if any(preferred_during_scheduling_ignored_during_execution):
                setattr(
                    affinity,
                    "preferred_during_scheduling_ignored_during_execution",
                    preferred_during_scheduling_ignored_during_execution,
                )

        if self.pod_affinity_terms is not None:
            required_during_scheduling_ignored_during_execution = [term._build() for term in self.pod_affinity_terms]
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

    Parameters
    ----------
    terms: Optional[List[NodeSelectorTerm]] = None
        The terms to use for node selector assembly. See also `hera.affinity.NodeSelectorTerm`.

    Notes
    -----
    See: https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity
    """

    def __init__(self, terms: Optional[List[NodeSelectorTerm]] = None):
        self.terms = terms

    def _build(self) -> Optional[ArgoNodeSelector]:
        """Assembles the node selector"""
        if self.terms is not None:
            terms = [term._build() if term else None for term in self.terms]
            if any(terms):
                return ArgoNodeSelector(node_selector_terms=terms)
        return None


class NodeAffinity:
    """Builds the K8S node affinity.

    Parameters
    ----------
    preferred_scheduling_terms: Optional[List[PreferredSchedulingTerm]] = None,
        Optional list of preferred scheduling terms. See `hera.affinity.PreferredSchedulingTerm`.
    node_selector: Optional[NodeSelector] = None
        Optional node selector for node affinity. See `hera.affinity.NodeSelector`.

    Notes
    -----
    See: https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity
    """

    def __init__(
        self,
        preferred_scheduling_terms: Optional[List[PreferredSchedulingTerm]] = None,
        node_selector: Optional[NodeSelector] = None,
    ) -> None:
        self.preferred_scheduling_terms = preferred_scheduling_terms
        self.node_selector = node_selector

    def _build(self) -> Optional[ArgoNodeAffinity]:
        """Assembles the node affinity"""
        affinity = ArgoNodeAffinity()

        if self.preferred_scheduling_terms is not None:
            preferred_during_scheduling_ignored_during_execution = [
                term._build() for term in self.preferred_scheduling_terms
            ]
            if any(preferred_during_scheduling_ignored_during_execution):
                setattr(
                    affinity,
                    "preferred_during_scheduling_ignored_during_execution",
                    preferred_during_scheduling_ignored_during_execution,
                )

        if self.node_selector is not None:
            required_during_scheduling_ignored_during_execution = self.node_selector._build()
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
    """Builds a full K8S affinity specification.

    Parameters
    ----------
    pod_affinity: Optional[PodAffinity] = None
        Pod affinity specification. See `hera.affinity.PodAffinity`.
    pod_anti_affinity: Optional[PodAntiAffinity] = None
        Pod anti affinity specification. See `hera.affinity.PodAntiAffinity`.
    node_affinity: Optional[NodeAffinity] = None
        Node affinity. See `hera.affinity.NodeAffinity`.

    Notes
    -----
    See: https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity
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

    def _build(self) -> Optional[ArgoAffinity]:
        """Assembles an affinity"""
        affinity = ArgoAffinity()

        if self.pod_affinity is not None:
            pod_affinity = self.pod_affinity._build()
            setattr(affinity, "pod_affinity", pod_affinity)

        if self.pod_anti_affinity is not None:
            pod_anti_affinity = self.pod_anti_affinity._build()
            setattr(affinity, "pod_anti_affinity", pod_anti_affinity)

        if self.node_affinity is not None:
            node_affinity = self.node_affinity._build()
            setattr(affinity, "node_affinity", node_affinity)

        if (
            hasattr(affinity, "pod_affinity")
            or hasattr(affinity, "pod_anti_affinity")
            or hasattr(affinity, "node_affinity")
        ):
            return affinity
        return None

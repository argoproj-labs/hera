from hera.affinity import NodeSelectorRequirement, Expression, Field, NodeSelectorTerm, PreferredSchedulingTerm, \
    LabelSelector, PodAffinityTerm, WeightedPodAffinityTerm, PodAffinity, PodAntiAffinity, NodeAffinity, Affinity, \
    LabelOperator, LabelSelectorRequirement
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


def test_node_selector_requirement_returns_expected_spec():
    node_selector_requirement = NodeSelectorRequirement('a', LabelOperator.In, values=['value'])
    spec = node_selector_requirement.get_spec()
    assert isinstance(spec, ArgoNodeSelectorRequirement)
    assert spec.key == 'a'
    assert spec.operator == 'In'
    assert spec.values == ['value']

    node_selector_requirement = NodeSelectorRequirement('a', LabelOperator.In)
    spec = node_selector_requirement.get_spec()
    assert isinstance(spec, ArgoNodeSelectorRequirement)
    assert spec.key == 'a'
    assert spec.operator == 'In'


def test_node_selector_term_returns_expected_spec():
    expressions = [Expression('a', LabelOperator.In, ['value'])]
    fields = [Field('a', LabelOperator.In, ['value'])]

    node_selector_term = NodeSelectorTerm(expressions=expressions, fields=fields)
    spec = node_selector_term.get_spec()
    assert isinstance(spec, ArgoNodeSelectorTerm)
    assert spec.match_expressions == [
        ArgoNodeSelectorRequirement(key='a', operator='In', values=['value']),
    ]
    assert spec.match_fields == [
        ArgoNodeSelectorRequirement(key='a', operator='In', values=['value']),
    ]

    node_selector_term = NodeSelectorTerm()
    spec = node_selector_term.get_spec()
    assert spec is None


def test_preferred_scheduling_term_returns_expected_spec():
    term = PreferredSchedulingTerm(NodeSelectorTerm(), 1)
    spec = term.get_spec()
    assert spec is None

    expressions = [Expression('a', LabelOperator.In, ['value'])]
    fields = [Field('a', LabelOperator.In, ['value'])]
    node_selector_term = NodeSelectorTerm(expressions=expressions, fields=fields)
    term = PreferredSchedulingTerm(node_selector_term, 1)
    spec = term.get_spec()
    assert isinstance(spec, ArgoPreferredSchedulingTerm)
    assert spec.preference is not None
    assert spec.preference.match_expressions == [
        ArgoNodeSelectorRequirement(key='a', operator='In', values=['value']),
    ]
    assert spec.preference.match_fields == [
        ArgoNodeSelectorRequirement(key='a', operator='In', values=['value']),
    ]
    assert spec.weight == 1


def test_label_selector_requirement():
    label_selector_requirement = LabelSelectorRequirement('a', LabelOperator.In, values=['value'])
    spec = label_selector_requirement.get_spec()
    assert isinstance(spec, ArgoLabelSelectorRequirement)
    assert spec.key == 'a'
    assert spec.operator == 'In'
    assert spec.values == ['value']

    label_selector_requirement = LabelSelectorRequirement('a', LabelOperator.In)
    spec = label_selector_requirement.get_spec()
    assert isinstance(spec, ArgoLabelSelectorRequirement)
    assert spec.key == 'a'
    assert spec.operator == 'In'


def test_label_selector():
    label_selector = LabelSelector(
        match_expressions=[LabelSelectorRequirement('a', LabelOperator.In, values=['value'])], match_labels={'a': 'b'},
    )
    spec = label_selector.get_spec()
    assert isinstance(spec, ArgoLabelSelector)
    assert spec.match_expressions == [
        ArgoLabelSelectorRequirement(key='a', operator='In', values=['value']),
    ]
    assert spec.match_labels is not None
    assert spec.match_labels == {'a': 'b'}

    label_selector = LabelSelector(
        match_expressions=[LabelSelectorRequirement('a', LabelOperator.In)], match_labels={'a': 'b'})
    spec = label_selector.get_spec()
    assert isinstance(spec, ArgoLabelSelector)
    assert spec.match_expressions == [
        ArgoLabelSelectorRequirement(key='a', operator='In'),
    ]
    assert spec.match_labels is not None
    assert spec.match_labels == {'a': 'b'}


def test_pod_affinity_term():
    label_selector = LabelSelector(
        match_expressions=[LabelSelectorRequirement('a', LabelOperator.In, values=['value'])], match_labels={'a': 'b'},
    )
    pod_affinity_term = PodAffinityTerm(
        topology_key='a',
        label_selector=label_selector,
        namespace_selector=label_selector,
        namespaces=['a'],
    )
    assert pod_affinity_term.topology_key == 'a'
    assert pod_affinity_term.label_selector == label_selector
    assert pod_affinity_term.namespace_selector == label_selector
    assert pod_affinity_term.namespaces == ['a']

    spec = pod_affinity_term.get_spec()
    assert isinstance(spec, ArgoPodAffinityTerm)
    assert spec.label_selector.match_expressions == [
        ArgoLabelSelectorRequirement(key='a', operator='In', values=['value']),
    ]
    assert spec.namespace_selector.match_expressions == [
        ArgoLabelSelectorRequirement(key='a', operator='In', values=['value']),
    ]
    assert spec.namespaces == ['a']

    pod_affinity_term = PodAffinityTerm('a')
    spec = pod_affinity_term.get_spec()
    assert spec is None


def test_weighted_pod_affinity_term():
    label_selector = LabelSelector(
        match_expressions=[LabelSelectorRequirement('a', LabelOperator.In, values=['value'])], match_labels={'a': 'b'},
    )
    weighted_pod_affinity_term = WeightedPodAffinityTerm(
        weight=1,
        pod_affinity_term=PodAffinityTerm(
            topology_key='a',
            label_selector=label_selector,
            namespace_selector=label_selector,
            namespaces=['a'],
        ),
    )
    spec = weighted_pod_affinity_term.get_spec()
    assert isinstance(spec, ArgoWeightedPodAffinityTerm)
    assert spec.weight == 1
    assert spec.pod_affinity_term.label_selector.match_expressions == [
        ArgoLabelSelectorRequirement(key='a', operator='In', values=['value']),
    ]
    assert spec.pod_affinity_term.namespace_selector.match_expressions == [
        ArgoLabelSelectorRequirement(key='a', operator='In', values=['value']),
    ]
    assert spec.pod_affinity_term.namespaces == ['a']


def test_pod_affinity():
    pod_affinity = PodAffinity(
        required_during_scheduling_ignored_during_execution=[PodAffinityTerm(
            topology_key='a',
            label_selector=LabelSelector(
                match_expressions=[LabelSelectorRequirement('a', LabelOperator.In, values=['value'])],
                match_labels={'a': 'b'},
            ),
            namespace_selector=LabelSelector(
                match_expressions=[LabelSelectorRequirement('a', LabelOperator.In, values=['value'])],
                match_labels={'a': 'b'},
            ),
            namespaces=['a'],
        )],
        preferred_during_scheduling_ignored_during_execution=[WeightedPodAffinityTerm(
            weight=1,
            pod_affinity_term=PodAffinityTerm(
                topology_key='a',
                label_selector=LabelSelector(
                    match_expressions=[LabelSelectorRequirement('a', LabelOperator.In, values=['value'])],
                    match_labels={'a': 'b'},
                ),
                namespace_selector=LabelSelector(
                    match_expressions=[LabelSelectorRequirement('a', LabelOperator.In, values=['value'])],
                    match_labels={'a': 'b'},
                ),
                namespaces=['a'],
            ),
        )],
    )
    spec = pod_affinity.get_spec()
    assert isinstance(spec, ArgoPodAffinity)
    assert spec.required_during_scheduling_ignored_during_execution == [
        ArgoPodAffinityTerm(
            topology_key='a',
            label_selector=ArgoLabelSelector(
                match_expressions=[
                    ArgoLabelSelectorRequirement(key='a', operator='In', values=['value']),
                ],
                match_labels={'a': 'b'},
            ),
            namespace_selector=ArgoLabelSelector(
                match_expressions=[
                    ArgoLabelSelectorRequirement(key='a', operator='In', values=['value']),
                ],
                match_labels={'a': 'b'},
            ),
            namespaces=['a'],
        ),
    ]

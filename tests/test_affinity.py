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

from hera.affinity import (
    Affinity,
    Expression,
    Field,
    LabelOperator,
    LabelSelector,
    LabelSelectorRequirement,
    NodeAffinity,
    NodeSelector,
    NodeSelectorRequirement,
    NodeSelectorTerm,
    PodAffinity,
    PodAffinityTerm,
    PodAntiAffinity,
    PreferredSchedulingTerm,
    WeightedPodAffinityTerm,
)


def test_node_selector_requirement_returns_expected_spec():
    node_selector_requirement = NodeSelectorRequirement('a', LabelOperator.In, values=['value'])
    assert node_selector_requirement.key == 'a'
    assert node_selector_requirement.operator == LabelOperator.In
    assert node_selector_requirement.values == ['value']

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
    assert node_selector_term.expressions == expressions
    assert node_selector_term.fields == fields

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
    assert node_selector_term.expressions == expressions
    assert node_selector_term.fields == fields

    term = PreferredSchedulingTerm(node_selector_term, 1)
    assert term.node_selector_term == node_selector_term
    assert term.weight == 1

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
    assert label_selector_requirement.key == 'a'
    assert label_selector_requirement.operator == LabelOperator.In
    assert label_selector_requirement.values == ['value']

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
        label_selector_requirements=[LabelSelectorRequirement('a', LabelOperator.In, values=['value'])],
        match_labels={'a': 'b'},
    )

    spec = label_selector.get_spec()
    assert isinstance(spec, ArgoLabelSelector)
    assert spec.match_expressions == [
        ArgoLabelSelectorRequirement(key='a', operator='In', values=['value']),
    ]
    assert spec.match_labels is not None
    assert spec.match_labels == {'a': 'b'}

    label_selector = LabelSelector(
        label_selector_requirements=[LabelSelectorRequirement('a', LabelOperator.In)], match_labels={'a': 'b'}
    )

    spec = label_selector.get_spec()
    assert isinstance(spec, ArgoLabelSelector)
    assert spec.match_expressions == [
        ArgoLabelSelectorRequirement(key='a', operator='In'),
    ]
    assert spec.match_labels is not None
    assert spec.match_labels == {'a': 'b'}

    label_selector = LabelSelector()
    spec = label_selector.get_spec()
    assert spec is None


def test_pod_affinity_term():
    label_selector = LabelSelector(
        label_selector_requirements=[LabelSelectorRequirement('a', LabelOperator.In, values=['value'])],
        match_labels={'a': 'b'},
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
        label_selector_requirements=[LabelSelectorRequirement('a', LabelOperator.In, values=['value'])],
        match_labels={'a': 'b'},
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
        pod_affinity_terms=[
            PodAffinityTerm(
                topology_key='a',
                label_selector=LabelSelector(
                    label_selector_requirements=[LabelSelectorRequirement('a', LabelOperator.In, values=['value'])],
                    match_labels={'a': 'b'},
                ),
                namespace_selector=LabelSelector(
                    label_selector_requirements=[LabelSelectorRequirement('a', LabelOperator.In, values=['value'])],
                    match_labels={'a': 'b'},
                ),
                namespaces=['a'],
            )
        ],
        weighted_pod_affinities=[
            WeightedPodAffinityTerm(
                weight=1,
                pod_affinity_term=PodAffinityTerm(
                    topology_key='a',
                    label_selector=LabelSelector(
                        label_selector_requirements=[
                            LabelSelectorRequirement('a', LabelOperator.In, values=['value'])
                        ],
                        match_labels={'a': 'b'},
                    ),
                    namespace_selector=LabelSelector(
                        label_selector_requirements=[
                            LabelSelectorRequirement('a', LabelOperator.In, values=['value'])
                        ],
                        match_labels={'a': 'b'},
                    ),
                    namespaces=['a'],
                ),
            )
        ],
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

    pod_affinity = PodAffinity()
    spec = pod_affinity.get_spec()
    assert spec is None


def test_pod_anti_affinity():
    pod_affinity = PodAntiAffinity(
        pod_affinity_terms=[
            PodAffinityTerm(
                topology_key='a',
                label_selector=LabelSelector(
                    label_selector_requirements=[LabelSelectorRequirement('a', LabelOperator.In, values=['value'])],
                    match_labels={'a': 'b'},
                ),
                namespace_selector=LabelSelector(
                    label_selector_requirements=[LabelSelectorRequirement('a', LabelOperator.In, values=['value'])],
                    match_labels={'a': 'b'},
                ),
                namespaces=['a'],
            )
        ],
        weighted_pod_affinities=[
            WeightedPodAffinityTerm(
                weight=1,
                pod_affinity_term=PodAffinityTerm(
                    topology_key='a',
                    label_selector=LabelSelector(
                        label_selector_requirements=[
                            LabelSelectorRequirement('a', LabelOperator.In, values=['value'])
                        ],
                        match_labels={'a': 'b'},
                    ),
                    namespace_selector=LabelSelector(
                        label_selector_requirements=[
                            LabelSelectorRequirement('a', LabelOperator.In, values=['value'])
                        ],
                        match_labels={'a': 'b'},
                    ),
                    namespaces=['a'],
                ),
            )
        ],
    )
    spec = pod_affinity.get_spec()
    assert isinstance(spec, ArgoPodAntiAffinity)
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

    pod_affinity = PodAntiAffinity()
    spec = pod_affinity.get_spec()
    assert spec is None


def test_node_affinity():
    node_affinity = NodeAffinity(
        preferred_scheduling_terms=[
            PreferredSchedulingTerm(
                NodeSelectorTerm(
                    expressions=[Expression('a', LabelOperator.In, ['value'])],
                    fields=[Field('a', LabelOperator.In, ['value'])],
                ),
                1,
            )
        ],
        node_selector=NodeSelector(
            terms=[
                NodeSelectorTerm(
                    expressions=[Expression('a', LabelOperator.In, ['value'])],
                    fields=[Field('a', LabelOperator.In, ['value'])],
                )
            ]
        ),
    )

    spec = node_affinity.get_spec()
    assert isinstance(spec, ArgoNodeAffinity)
    assert spec.preferred_during_scheduling_ignored_during_execution == [
        ArgoPreferredSchedulingTerm(
            preference=ArgoNodeSelectorTerm(
                match_expressions=[
                    ArgoNodeSelectorRequirement(key='a', operator='In', values=['value']),
                ],
                match_fields=[
                    ArgoNodeSelectorRequirement(key='a', operator='In', values=['value']),
                ],
            ),
            weight=1,
        ),
    ]
    assert spec.required_during_scheduling_ignored_during_execution == ArgoNodeSelector(
        node_selector_terms=[
            ArgoNodeSelectorTerm(
                match_expressions=[
                    ArgoNodeSelectorRequirement(key='a', operator='In', values=['value']),
                ],
                match_fields=[
                    ArgoNodeSelectorRequirement(key='a', operator='In', values=['value']),
                ],
            ),
        ]
    )


def test_affinity():
    affinity = Affinity(
        pod_affinity=PodAffinity(
            pod_affinity_terms=[
                PodAffinityTerm(
                    topology_key='a',
                    label_selector=LabelSelector(
                        label_selector_requirements=[
                            LabelSelectorRequirement('a', LabelOperator.In, values=['value'])
                        ],
                        match_labels={'a': 'b'},
                    ),
                    namespace_selector=LabelSelector(
                        label_selector_requirements=[
                            LabelSelectorRequirement('a', LabelOperator.In, values=['value'])
                        ],
                        match_labels={'a': 'b'},
                    ),
                    namespaces=['a'],
                )
            ],
            weighted_pod_affinities=[
                WeightedPodAffinityTerm(
                    weight=1,
                    pod_affinity_term=PodAffinityTerm(
                        topology_key='a',
                        label_selector=LabelSelector(
                            label_selector_requirements=[
                                LabelSelectorRequirement('a', LabelOperator.In, values=['value'])
                            ],
                            match_labels={'a': 'b'},
                        ),
                        namespace_selector=LabelSelector(
                            label_selector_requirements=[
                                LabelSelectorRequirement('a', LabelOperator.In, values=['value'])
                            ],
                            match_labels={'a': 'b'},
                        ),
                        namespaces=['a'],
                    ),
                )
            ],
        ),
        pod_anti_affinity=PodAntiAffinity(
            pod_affinity_terms=[
                PodAffinityTerm(
                    topology_key='a',
                    label_selector=LabelSelector(
                        label_selector_requirements=[
                            LabelSelectorRequirement('a', LabelOperator.In, values=['value'])
                        ],
                        match_labels={'a': 'b'},
                    ),
                    namespace_selector=LabelSelector(
                        label_selector_requirements=[
                            LabelSelectorRequirement('a', LabelOperator.In, values=['value'])
                        ],
                        match_labels={'a': 'b'},
                    ),
                    namespaces=['a'],
                )
            ],
            weighted_pod_affinities=[
                WeightedPodAffinityTerm(
                    weight=1,
                    pod_affinity_term=PodAffinityTerm(
                        topology_key='a',
                        label_selector=LabelSelector(
                            label_selector_requirements=[
                                LabelSelectorRequirement('a', LabelOperator.In, values=['value'])
                            ],
                            match_labels={'a': 'b'},
                        ),
                        namespace_selector=LabelSelector(
                            label_selector_requirements=[
                                LabelSelectorRequirement('a', LabelOperator.In, values=['value'])
                            ],
                            match_labels={'a': 'b'},
                        ),
                        namespaces=['a'],
                    ),
                )
            ],
        ),
        node_affinity=NodeAffinity(
            preferred_scheduling_terms=[
                PreferredSchedulingTerm(
                    NodeSelectorTerm(
                        expressions=[Expression('a', LabelOperator.In, ['value'])],
                        fields=[Field('a', LabelOperator.In, ['value'])],
                    ),
                    1,
                )
            ],
            node_selector=NodeSelector(
                terms=[
                    NodeSelectorTerm(
                        expressions=[Expression('a', LabelOperator.In, ['value'])],
                        fields=[Field('a', LabelOperator.In, ['value'])],
                    )
                ]
            ),
        ),
    )
    assert affinity.get_spec() is not None

    affinity = Affinity()
    assert affinity.get_spec() is None


def test_node_selector_returns_none_on_empty_spec():
    node_selector = NodeSelector()
    assert node_selector.get_spec() is None


def test_node_affinity_returns_none_on_empty_spec():
    node_affinity = NodeAffinity()
    assert node_affinity.get_spec() is None

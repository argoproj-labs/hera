from typing import Dict, List, Tuple

import pytest

from hera.affinity import (
    Affinity,
    Expression,
    Field,
    LabelOperator,
    LabelSelector,
    LabelSelectorRequirement,
    NodeAffinity,
    NodeSelector,
    NodeSelectorTerm,
    PodAffinity,
    PodAffinityTerm,
    PodAntiAffinity,
    PreferredSchedulingTerm,
    WeightedPodAffinityTerm,
)
from hera.artifact import Artifact

# from hera.artifact import InputArtifact, OutputArtifact
from hera.cron_workflow import CronWorkflow
from hera.cron_workflow_service import CronWorkflowService
from hera.workflow import Workflow
from hera.workflow_service import WorkflowService
from hera.workflow_template import WorkflowTemplate
from hera.workflow_template_service import WorkflowTemplateService


@pytest.fixture(scope="session")
def ws():
    yield WorkflowService(host="https://abc.com", token="abc")


@pytest.fixture(scope="function")
def w(ws):
    yield Workflow("w", service=ws)


@pytest.fixture(scope="session")
def wts():
    yield WorkflowTemplateService(host="https://abc.com", token="abc")


@pytest.fixture(scope="function")
def wt(wts):
    yield WorkflowTemplate("wt", service=wts)


@pytest.fixture(scope="function")
def cws():
    yield CronWorkflowService(host="https://abc.com", token="abc")


@pytest.fixture(scope="session")
def schedule():
    yield "* * * * *"


@pytest.fixture(scope="function")
def cw(cws, schedule):
    yield CronWorkflow("cw", schedule, service=cws)


@pytest.fixture(scope="session")
def artifact():
    yield Artifact("test", "/test")


@pytest.fixture(scope="session")
def no_op():
    def _no_op():
        pass

    yield _no_op


@pytest.fixture(scope="session")
def op():
    def _op(a):
        print(a)

    yield _op


@pytest.fixture(scope="session")
def kwarg_op():
    def _kwarg_op(a: int = 42):
        print(a)

    yield _kwarg_op


@pytest.fixture(scope="session")
def kwarg_multi_op():
    def _kwarg_multi_op(a: int = 42, b: int = 43):
        print(a, b)

    yield _kwarg_multi_op


@pytest.fixture(scope="session")
def multi_op():
    def _multi_op(a, b, c):
        print(a, b, c)

    yield _multi_op


@pytest.fixture(scope="session")
def typed_op():
    def _typed_op(a) -> List[Dict[str, Tuple[int, int]]]:
        print(a)
        return [{"a": (a, a)}]

    yield _typed_op


@pytest.fixture(scope="session")
def long_op():
    def _long_op(
        very_long_parameter_name,
        very_very_long_parameter_name,
        very_very_very_long_parameter_name,
        very_very_very_very_long_parameter_name,
        very_very_very_very_very_long_parameter_name,
    ):
        print(42)

    yield _long_op


@pytest.fixture(scope="session")
def affinity():
    yield Affinity(
        pod_affinity=PodAffinity(
            pod_affinity_terms=[
                PodAffinityTerm(
                    topology_key="a",
                    label_selector=LabelSelector(
                        label_selector_requirements=[
                            LabelSelectorRequirement("a", LabelOperator.In, values=["value"])
                        ],
                        match_labels={"a": "b"},
                    ),
                    namespace_selector=LabelSelector(
                        label_selector_requirements=[
                            LabelSelectorRequirement("a", LabelOperator.In, values=["value"])
                        ],
                        match_labels={"a": "b"},
                    ),
                    namespaces=["a"],
                )
            ],
            weighted_pod_affinities=[
                WeightedPodAffinityTerm(
                    weight=1,
                    pod_affinity_term=PodAffinityTerm(
                        topology_key="a",
                        label_selector=LabelSelector(
                            label_selector_requirements=[
                                LabelSelectorRequirement("a", LabelOperator.In, values=["value"])
                            ],
                            match_labels={"a": "b"},
                        ),
                        namespace_selector=LabelSelector(
                            label_selector_requirements=[
                                LabelSelectorRequirement("a", LabelOperator.In, values=["value"])
                            ],
                            match_labels={"a": "b"},
                        ),
                        namespaces=["a"],
                    ),
                )
            ],
        ),
        pod_anti_affinity=PodAntiAffinity(
            pod_affinity_terms=[
                PodAffinityTerm(
                    topology_key="a",
                    label_selector=LabelSelector(
                        label_selector_requirements=[
                            LabelSelectorRequirement("a", LabelOperator.In, values=["value"])
                        ],
                        match_labels={"a": "b"},
                    ),
                    namespace_selector=LabelSelector(
                        label_selector_requirements=[
                            LabelSelectorRequirement("a", LabelOperator.In, values=["value"])
                        ],
                        match_labels={"a": "b"},
                    ),
                    namespaces=["a"],
                )
            ],
            weighted_pod_affinities=[
                WeightedPodAffinityTerm(
                    weight=1,
                    pod_affinity_term=PodAffinityTerm(
                        topology_key="a",
                        label_selector=LabelSelector(
                            label_selector_requirements=[
                                LabelSelectorRequirement("a", LabelOperator.In, values=["value"])
                            ],
                            match_labels={"a": "b"},
                        ),
                        namespace_selector=LabelSelector(
                            label_selector_requirements=[
                                LabelSelectorRequirement("a", LabelOperator.In, values=["value"])
                            ],
                            match_labels={"a": "b"},
                        ),
                        namespaces=["a"],
                    ),
                )
            ],
        ),
        node_affinity=NodeAffinity(
            preferred_scheduling_terms=[
                PreferredSchedulingTerm(
                    NodeSelectorTerm(
                        expressions=[Expression("a", LabelOperator.In, ["value"])],
                        fields=[Field("a", LabelOperator.In, ["value"])],
                    ),
                    1,
                )
            ],
            node_selector=NodeSelector(
                terms=[
                    NodeSelectorTerm(
                        expressions=[Expression("a", LabelOperator.In, ["value"])],
                        fields=[Field("a", LabelOperator.In, ["value"])],
                    )
                ]
            ),
        ),
    )

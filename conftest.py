from typing import Dict, List, Optional, Tuple

import pytest

from hera import set_global_host, set_global_token
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
from hera.cron_workflow import CronWorkflow
from hera.global_config import GlobalConfig
from hera.workflow import Workflow
from hera.workflow_template import WorkflowTemplate


@pytest.fixture
def setup():
    GlobalConfig.host = "https://abc.com"
    GlobalConfig.token = "abc"
    yield GlobalConfig


@pytest.fixture(scope="function")
def global_config():
    yield GlobalConfig
    GlobalConfig.reset()


@pytest.fixture(scope="function")
def w(setup):
    with Workflow("w") as w:
        yield w


@pytest.fixture(scope="function")
def wt(wts):
    yield WorkflowTemplate("wt")


@pytest.fixture(scope="session")
def schedule():
    yield "* * * * *"


@pytest.fixture(scope="function")
def cw(schedule):
    with CronWorkflow("cw", schedule) as w:
        yield w


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
def kwarg_op_bool_default():
    def _kwarg_op_bool_default(a: bool = False):
        print(a)

    yield _kwarg_op_bool_default


@pytest.fixture(scope="session")
def kwarg_op_none_default():
    def _kwarg_op_none_default(a: Optional[str] = None):
        print(a)

    yield _kwarg_op_none_default


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

from dataclasses import dataclass
from typing import Dict, List, Optional

from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1Counter,
    IoArgoprojWorkflowV1alpha1Gauge,
    IoArgoprojWorkflowV1alpha1Histogram,
    IoArgoprojWorkflowV1alpha1MetricLabel,
    IoArgoprojWorkflowV1alpha1Metrics,
    IoArgoprojWorkflowV1alpha1Prometheus,
)


@dataclass
class Counter:
    """Counter metric component used to count specific events based on the given value.

    Notes
    -----
    See: https://argoproj.github.io/argo-workflows/metrics/#grafana-dashboard-for-argo-controller-metrics
    """

    value: str

    def build(self) -> IoArgoprojWorkflowV1alpha1Counter:
        return IoArgoprojWorkflowV1alpha1Counter(self.value)


@dataclass
class Gauge:
    """Gauge metric component used to record intervals based on the given value.

    Notes
    -----
    See: https://argoproj.github.io/argo-workflows/metrics/#grafana-dashboard-for-argo-controller-metrics
    """

    realtime: bool
    value: str

    def build(self) -> IoArgoprojWorkflowV1alpha1Gauge:
        return IoArgoprojWorkflowV1alpha1Gauge(self.realtime, self.value)


@dataclass
class Histogram:
    """Histogram metric that records the value at the specified bucket intervals.

    Notes
    -----
    See: https://argoproj.github.io/argo-workflows/metrics/#grafana-dashboard-for-argo-controller-metrics
    """

    buckets: List[float]
    value: str

    def __post_init__(self):
        assert len(self.buckets) >= 1, "Histogram needs at least one `buckets` specification"

    def build(self) -> IoArgoprojWorkflowV1alpha1Histogram:
        return IoArgoprojWorkflowV1alpha1Histogram(self.buckets, self.value)


@dataclass
class Label:
    """Metric label that identified a specific metric by a key/value pair.

    Notes
    -----
    See: https://argoproj.github.io/argo-workflows/metrics/#grafana-dashboard-for-argo-controller-metrics
    """

    key: str
    value: str

    def build(self) -> IoArgoprojWorkflowV1alpha1MetricLabel:
        return IoArgoprojWorkflowV1alpha1MetricLabel(self.key, self.value)


@dataclass
class Metric:
    """Prometheus metric that can be used at the workflow or task/template level.

    Notes
    -----
    See: https://argoproj.github.io/argo-workflows/metrics/#grafana-dashboard-for-argo-controller-metrics
    """

    name: str
    help: str

    counter: Optional[Counter] = None
    gauge: Optional[Gauge] = None
    histogram: Optional[Histogram] = None
    labels: Optional[List[Label]] = None
    when: Optional[str] = None

    def build(self) -> IoArgoprojWorkflowV1alpha1Prometheus:
        metric = IoArgoprojWorkflowV1alpha1Prometheus(self.help, self.name)
        if self.counter is not None:
            setattr(metric, 'counter', self.counter.build())
        if self.gauge is not None:
            setattr(metric, 'gauge', self.gauge.build())
        if self.histogram is not None:
            setattr(metric, 'histogram', self.histogram.build())
        if self.labels is not None:
            setattr(metric, 'labels', [label.build() for label in self.labels])
        if self.when is not None:
            setattr(metric, 'when', self.when)
        return metric


@dataclass
class Metrics:
    """A collection of Prometheus metrics.

    Notes
    -----
    See: https://argoproj.github.io/argo-workflows/metrics/#grafana-dashboard-for-argo-controller-metrics
    """

    metrics: List[Metric]

    def __post_init__(self):
        """
        Metric definitions must include a name and a help doc string. They can also include any number of labels
        (when defining labels avoid cardinality explosion). Metrics with the same name must always use the same exact
        help string, having different metrics with the same name, but with a different help string will cause an error
        (this is a Prometheus requirement).
        """
        metrics_map: Dict[str, List[Metric]] = {}
        for m in self.metrics:
            metrics_map[m.name] = metrics_map.get(m.name, []) + [m]
            if len(metrics_map[m.name]) > 1:
                initial_help = metrics_map[m.name][0].help
                for repeat_metric in metrics_map[m.name]:
                    assert repeat_metric.help == initial_help, (
                        "Metric definitions that have the same `name` must use the same `help` as well. This is a "
                        "Prometheus requirement"
                    )

    def build(self) -> IoArgoprojWorkflowV1alpha1Metrics:
        return IoArgoprojWorkflowV1alpha1Metrics([m.build() for m in self.metrics])

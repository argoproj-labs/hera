from typing import List, Optional

from hera.shared import BaseMixin
from hera.workflows.models import (
    Counter as _ModelCounter,
    Gauge as _ModelGauge,
    Histogram as _ModelHistogram,
    MetricLabel as _ModelMetricLabel,
    Prometheus as _ModelPrometheus,
)

Label = _ModelMetricLabel


class _BaseMetric(BaseMixin):
    """Base metric wrapper around `hera.workflows.models.Prometheus`"""

    name: str
    help: str
    labels: Optional[List[Label]] = None
    when: Optional[str] = None

    def _build_metric(self) -> _ModelPrometheus:
        raise NotImplementedError


class Counter(_BaseMetric, _ModelCounter):
    """Counter metric component used to count specific events based on the given value.

    Notes
    -----
    See: https://argoproj.github.io/argo-workflows/metrics/#grafana-dashboard-for-argo-controller-metrics
    """

    def _build_metric(self) -> _ModelPrometheus:
        return _ModelPrometheus(
            name=self.name,
            help=self.help,
            labels=self.labels,
            when=self.when,
            counter=_ModelCounter(value=self.value),
        )


class Gauge(_BaseMetric, _ModelGauge):
    """Gauge metric component used to record intervals based on the given value.

    Notes
    -----
    See: https://argoproj.github.io/argo-workflows/metrics/#grafana-dashboard-for-argo-controller-metrics
    """

    def _build_metric(self) -> _ModelPrometheus:
        return _ModelPrometheus(
            name=self.name,
            help=self.help,
            labels=self.labels,
            when=self.when,
            gauge=_ModelGauge(realtime=self.realtime, value=self.value),
        )


class Histogram(_BaseMetric, _ModelHistogram):
    """Histogram metric that records the value at the specified bucket intervals.

    Notes
    -----
    See: https://argoproj.github.io/argo-workflows/metrics/#grafana-dashboard-for-argo-controller-metrics
    """

    def _build_metric(self) -> _ModelPrometheus:
        return _ModelPrometheus(
            name=self.name,
            help=self.help,
            labels=self.labels,
            when=self.when,
            histogram=_ModelHistogram(
                buckets=self.buckets,
                value=self.value,
            ),
        )


class Metric(_BaseMetric):
    """Prometheus metric that can be used at the workflow or task/template level.

    Notes
    -----
    See: https://argoproj.github.io/argo-workflows/metrics/#grafana-dashboard-for-argo-controller-metrics
    """

    counter: Optional[Counter] = None
    gauge: Optional[Gauge] = None
    histogram: Optional[Histogram] = None

    def _build_metric(self) -> _ModelPrometheus:
        return _ModelPrometheus(
            name=self.name,
            help=self.help,
            labels=self.labels,
            when=self.when,
            counter=_ModelCounter(value=self.counter.value) if self.counter else None,
            gauge=_ModelGauge(realtime=self.gauge.realtime, value=self.gauge.value) if self.gauge else None,
            histogram=_ModelHistogram(
                buckets=self.histogram.buckets,
                value=self.histogram.value,
            )
            if self.histogram
            else None,
        )


class Metrics(BaseMixin):
    """A collection of Prometheus metrics.

    Notes
    -----
    See: https://argoproj.github.io/argo-workflows/metrics/#grafana-dashboard-for-argo-controller-metrics
    """

    metrics: List[Metric]

    def _build_metrics(self) -> List[_ModelPrometheus]:
        return [metric._build_metric() for metric in self.metrics]


__all__ = [
    "Label",
    "Counter",
    "Gauge",
    "Histogram",
    "Metric",
    "Metrics",
]

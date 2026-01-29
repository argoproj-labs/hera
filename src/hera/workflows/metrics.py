"""The `hera.workflows.metrics` module implements independent and Prometheus metrics that can be used in Argo."""

from dataclasses import dataclass
from typing import List, Optional, Union

from hera.shared import BaseMixin
from hera.workflows.models import (
    Amount as _ModelAmount,
    Counter as _ModelCounter,
    Gauge as _ModelGauge,
    Histogram as _ModelHistogram,
    MetricLabel as _ModelMetricLabel,
    Prometheus as _ModelPrometheus,
)

Label = _ModelMetricLabel


@dataclass(kw_only=True)
class _BaseMetric:
    """Base metric wrapper around `hera.workflows.models.Prometheus`."""

    name: str
    help: str
    labels: Optional[Union[Label, List[Label]]] = None
    when: Optional[str] = None

    def _build_labels(self) -> Optional[List[_ModelMetricLabel]]:
        if not self.labels:
            return None
        if isinstance(self.labels, Label):
            return [self.labels]
        return self.labels

    def _build_metric(self) -> _ModelPrometheus:
        raise NotImplementedError


@dataclass(kw_only=True)
class Counter(_BaseMetric):
    """Counter metric component used to count specific events based on the given value.

    Notes:
        See <https://argoproj.github.io/argo-workflows/metrics/#grafana-dashboard-for-argo-controller-metrics>
    """

    value: str

    def _build_metric(self) -> _ModelPrometheus:
        return _ModelPrometheus(
            counter=_ModelCounter(value=self.value),
            gauge=None,
            help=self.help,
            histogram=None,
            labels=self._build_labels(),
            name=self.name,
            when=self.when,
        )


@dataclass(kw_only=True)
class Gauge(_BaseMetric):
    """Gauge metric component used to record intervals based on the given value.

    Notes:
        See <https://argoproj.github.io/argo-workflows/metrics/#grafana-dashboard-for-argo-controller-metrics>
    """

    realtime: bool
    value: str
    operation: Optional[str] = None

    def _build_metric(self) -> _ModelPrometheus:
        return _ModelPrometheus(
            counter=None,
            gauge=_ModelGauge(realtime=self.realtime, value=self.value, operation=self.operation),
            help=self.help,
            histogram=None,
            labels=self._build_labels(),
            name=self.name,
            when=self.when,
        )


@dataclass(kw_only=True)
class Histogram(_BaseMetric):
    """Histogram metric that records the value at the specified bucket intervals.

    Notes:
        See <https://argoproj.github.io/argo-workflows/metrics/#grafana-dashboard-for-argo-controller-metrics>
    """

    buckets: List[float | _ModelAmount]
    value: str

    def _build_buckets(self) -> List[_ModelAmount]:
        return [
            bucket if isinstance(bucket, _ModelAmount) else _ModelAmount(__root__=bucket) for bucket in self.buckets
        ]

    def _build_metric(self) -> _ModelPrometheus:
        return _ModelPrometheus(
            counter=None,
            gauge=None,
            help=self.help,
            histogram=_ModelHistogram(
                buckets=self._build_buckets(),
                value=self.value,
            ),
            labels=self._build_labels(),
            name=self.name,
            when=self.when,
        )


@dataclass(kw_only=True)
class Metric(_BaseMetric):
    """Prometheus metric that can be used at the workflow or task/template level.

    Notes:
        See <https://argoproj.github.io/argo-workflows/metrics/#grafana-dashboard-for-argo-controller-metrics>
    """

    counter: Optional[Counter] = None
    gauge: Optional[Gauge] = None
    histogram: Optional[Histogram] = None

    def _build_metric(self) -> _ModelPrometheus:
        return _ModelPrometheus(
            counter=_ModelCounter(value=self.counter.value) if self.counter else None,
            gauge=_ModelGauge(realtime=self.gauge.realtime, value=self.gauge.value) if self.gauge else None,
            help=self.help,
            histogram=_ModelHistogram(
                buckets=self.histogram._build_buckets(),
                value=self.histogram.value,
            )
            if self.histogram
            else None,
            labels=self._build_labels(),
            name=self.name,
            when=self.when,
        )


@dataclass(kw_only=True)
class Metrics(BaseMixin):
    """A collection of Prometheus metrics.

    Notes:
        See <https://argoproj.github.io/argo-workflows/metrics/#grafana-dashboard-for-argo-controller-metrics>
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

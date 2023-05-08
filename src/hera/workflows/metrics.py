from typing import List, Optional

from hera.shared import BaseMixin
from hera.workflows.models import (
    Counter as _ModelCounter,
    Gauge as _ModelGauge,
    Histogram as _ModelHistogram,
    MetricLabel as _ModelMetricLabel,
    Prometheus as _ModelPrometheus,
)


class Label(_ModelMetricLabel):
    key: str
    value: str


class _BaseMetric(BaseMixin):
    name: str
    help: str
    labels: Optional[List[Label]] = None
    when: Optional[str] = None

    def _build_metric(self) -> _ModelPrometheus:
        raise NotImplementedError


class Counter(_BaseMetric, _ModelCounter):
    def _build_metric(self) -> _ModelPrometheus:
        return _ModelPrometheus(
            name=self.name,
            help=self.help,
            labels=self.labels,
            when=self.when,
            counter=_ModelCounter(value=self.value),
        )


class Gauge(_BaseMetric, _ModelGauge):
    def _build_metric(self) -> _ModelPrometheus:
        return _ModelPrometheus(
            name=self.name,
            help=self.help,
            labels=self.labels,
            when=self.when,
            gauge=_ModelGauge(realtime=self.realtime, value=self.value),
        )


class Histogram(_BaseMetric, _ModelHistogram):
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
    counter: Optional[Counter] = None
    gauge: Optional[Gauge] = None
    histogram: Optional[Histogram] = None

    def _build_metric(self) -> _ModelPrometheus:
        return _ModelPrometheus(
            name=self.name,
            help=self.help,
            labels=self.labels,
            when=self.when,
            counter=_ModelCounter(value=self.counter.value),
            gauge=_ModelGauge(realtime=self.gauge.realtime, value=self.gauge.value),
            histogram=_ModelHistogram(
                buckets=self.histogram.buckets,
                value=self.histogram.value,
            ),
        )


class Metrics(BaseMixin):
    metrics: List[Metric]

    def _build_metrics(self) -> List[_ModelPrometheus]:
        return [metric._build_metric() for metric in self.metrics]

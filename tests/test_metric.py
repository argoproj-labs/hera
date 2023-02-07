import pytest
from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1Counter,
    IoArgoprojWorkflowV1alpha1Gauge,
    IoArgoprojWorkflowV1alpha1Histogram,
    IoArgoprojWorkflowV1alpha1MetricLabel,
    IoArgoprojWorkflowV1alpha1Metrics,
    IoArgoprojWorkflowV1alpha1Prometheus,
)

from hera.workflows.metric import Counter, Gauge, Histogram, Label, Metric, Metrics


class TestCounter:
    def test_builds_as_expected(self):
        c = Counter('abc').build()
        assert isinstance(c, IoArgoprojWorkflowV1alpha1Counter)
        assert hasattr(c, 'value')
        assert c.value == 'abc'


class TestGauge:
    def test_builds_as_expected(self):
        g = Gauge(True, 'abc').build()
        assert isinstance(g, IoArgoprojWorkflowV1alpha1Gauge)
        assert hasattr(g, 'realtime')
        assert g.realtime
        assert hasattr(g, 'value')
        assert g.value == 'abc'

        g = Gauge(False, 'abc').build()
        assert isinstance(g, IoArgoprojWorkflowV1alpha1Gauge)
        assert hasattr(g, 'realtime')
        assert not g.realtime
        assert hasattr(g, 'value')
        assert g.value == 'abc'


class TestHistogram:
    def test_post_init_raises(self):
        with pytest.raises(AssertionError) as e:
            Histogram([], "abc")
        assert str(e.value) == "Histogram needs at least one `buckets` specification"

    def test_builds_as_expected(self):
        h = Histogram([1.0, 2.0], "abc").build()
        assert isinstance(h, IoArgoprojWorkflowV1alpha1Histogram)
        assert hasattr(h, 'buckets')
        assert h.buckets == [1.0, 2.0]
        assert hasattr(h, 'value')
        assert h.value == 'abc'


class TestLabel:
    def test_builds_as_expected(self):
        l = Label('k', 'v').build()
        assert isinstance(l, IoArgoprojWorkflowV1alpha1MetricLabel)
        assert hasattr(l, 'key')
        assert l.key == 'k'
        assert hasattr(l, 'value')
        assert l.value == 'v'


class TestMetric:
    def test_builds_as_expected(self):
        m = Metric('a', 'b').build()
        assert isinstance(m, IoArgoprojWorkflowV1alpha1Prometheus)
        assert hasattr(m, 'name')
        assert m.name == 'a'
        assert hasattr(m, 'help')
        assert m.help == 'b'
        assert not hasattr(m, 'counter')
        assert not hasattr(m, 'gauge')
        assert not hasattr(m, 'histogram')
        assert not hasattr(m, 'labels')
        assert not hasattr(m, 'when')

        m = Metric(
            'a',
            'b',
            counter=Counter('c'),
            gauge=Gauge(True, 'g'),
            histogram=Histogram([1.0, 2.0], 'h'),
            labels=[Label('lk', 'lv')],
            when='whenever',
        ).build()
        assert isinstance(m, IoArgoprojWorkflowV1alpha1Prometheus)
        assert hasattr(m, 'name')
        assert m.name == 'a'
        assert hasattr(m, 'help')
        assert m.help == 'b'
        assert hasattr(m, 'counter')
        assert isinstance(m.counter, IoArgoprojWorkflowV1alpha1Counter)
        assert hasattr(m, 'gauge')
        assert isinstance(m.gauge, IoArgoprojWorkflowV1alpha1Gauge)
        assert hasattr(m, 'histogram')
        assert isinstance(m.histogram, IoArgoprojWorkflowV1alpha1Histogram)
        assert hasattr(m, 'labels')
        assert isinstance(m.labels, list)
        assert len(m.labels) == 1
        assert isinstance(m.labels[0], IoArgoprojWorkflowV1alpha1MetricLabel)
        assert hasattr(m, 'when')
        assert m.when == 'whenever'


class TestMetrics:
    def test_post_init_raises(self):
        with pytest.raises(AssertionError) as e:
            Metrics(
                [
                    Metric(
                        'a',
                        'b',
                        counter=Counter('c'),
                        gauge=Gauge(True, 'g'),
                        histogram=Histogram([1.0, 2.0], 'h'),
                        labels=[Label('lk', 'lv')],
                        when='whenever',
                    ),
                    Metric(
                        'a',
                        'c',
                        counter=Counter('c'),
                        gauge=Gauge(True, 'g'),
                        histogram=Histogram([1.0, 2.0], 'h'),
                        labels=[Label('lk', 'lv')],
                        when='whenever',
                    ),
                ]
            )
        assert (
            str(e.value) == "Metric definitions that have the same `name` must use the same `help` as well. "
            "This is a Prometheus requirement"
        )

    def test_builds_as_expected(self):
        ms = Metrics(
            [
                Metric(
                    'a',
                    'b',
                    counter=Counter('c'),
                    gauge=Gauge(True, 'g'),
                    histogram=Histogram([1.0, 2.0], 'h'),
                    labels=[Label('lk', 'lv')],
                    when='whenever',
                ),
                Metric(
                    'c',
                    'd',
                    counter=Counter('c'),
                    gauge=Gauge(True, 'g'),
                    histogram=Histogram([1.0, 2.0], 'h'),
                    labels=[Label('lk', 'lv')],
                    when='whenever',
                ),
            ]
        ).build()
        assert isinstance(ms, IoArgoprojWorkflowV1alpha1Metrics)
        assert hasattr(ms, 'prometheus')
        assert len(ms.prometheus) == 2

        ms = Metrics(
            [
                Metric(
                    'a',
                    'b',
                    counter=Counter('c'),
                    gauge=Gauge(True, 'g'),
                    histogram=Histogram([1.0, 2.0], 'h'),
                    labels=[Label('lk', 'lv')],
                    when='whenever',
                ),
                Metric(
                    'a',
                    'b',
                    counter=Counter('c'),
                    gauge=Gauge(True, 'g'),
                    histogram=Histogram([1.0, 2.0], 'h'),
                    labels=[Label('lk', 'lv')],
                    when='whenever',
                ),
            ]
        ).build()
        assert isinstance(ms, IoArgoprojWorkflowV1alpha1Metrics)
        assert hasattr(ms, 'prometheus')
        assert len(ms.prometheus) == 2

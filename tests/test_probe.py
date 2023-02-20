from hera.workflows.action import ExecAction, GRPCAction, HTTPGetAction, TCPSocketAction
from hera.workflows.probe import ArgoProbe, Probe


class TestProbe:
    def test_probe_build(self):
        p = Probe().build()
        assert isinstance(p, ArgoProbe)
        assert not hasattr(p, "_exec")
        assert not hasattr(p, "failure_threshold")
        assert not hasattr(p, "grpc")
        assert not hasattr(p, "http_get")
        assert not hasattr(p, "initial_delay_seconds")
        assert not hasattr(p, "period_seconds")
        assert not hasattr(p, "success_threshold")
        assert not hasattr(p, "tcp_socket")
        assert not hasattr(p, "termination_grace_period_seconds")
        assert not hasattr(p, "timeout_seconds")

        p = Probe(
            _exec=ExecAction(),
            failure_threshold=42,
            grpc=GRPCAction(443),
            http_get=HTTPGetAction("443"),
            initial_delay_seconds=42,
            period_seconds=42,
            success_threshold=84,
            tcp_socket=TCPSocketAction("443"),
            termination_grace_period_seconds=126,
            timeout_seconds=252,
        ).build()
        assert isinstance(p, ArgoProbe)
        assert hasattr(p, "_exec")
        assert hasattr(p, "failure_threshold")
        assert hasattr(p, "grpc")
        assert hasattr(p, "http_get")
        assert hasattr(p, "initial_delay_seconds")
        assert hasattr(p, "period_seconds")
        assert hasattr(p, "success_threshold")
        assert hasattr(p, "tcp_socket")
        assert hasattr(p, "termination_grace_period_seconds")
        assert hasattr(p, "timeout_seconds")

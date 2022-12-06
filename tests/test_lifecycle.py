from hera.lifecycle import Lifecycle, LifecycleHandler, ArgoLifecycle, ArgoLifecycleHandler
from hera.action import ExecAction, HTTPGetAction, TCPSocketAction


class TestLifecycle:

    def test_lifecycle_handler(self):
        h = LifecycleHandler().build()
        assert isinstance(h, ArgoLifecycleHandler)
        assert not hasattr(h, "_exec")
        assert not hasattr(h, "http_get")
        assert not hasattr(h, "tcp_socket")

        h = LifecycleHandler(
            _exec=ExecAction(),
            http_get=HTTPGetAction("443"),
            tcp_socket=TCPSocketAction("8080")
        ).build()
        assert isinstance(h, ArgoLifecycleHandler)
        assert hasattr(h, "_exec")
        assert hasattr(h, "http_get")
        assert hasattr(h, "tcp_socket")

    def test_lifecycle(self):
        h = Lifecycle().build()
        assert isinstance(h, ArgoLifecycle)
        assert not hasattr(h, "post_start")
        assert not hasattr(h, "pre_stop")

        h = Lifecycle(
            pre_stop=LifecycleHandler(
                _exec=ExecAction(),
                http_get=HTTPGetAction("443"),
                tcp_socket=TCPSocketAction("8080")
            ),
            post_start=LifecycleHandler(
                _exec=ExecAction(),
                http_get=HTTPGetAction("443"),
                tcp_socket=TCPSocketAction("8080")
            ),
        ).build()
        assert isinstance(h, ArgoLifecycle)
        assert hasattr(h, "post_start")
        assert hasattr(h, "pre_stop")

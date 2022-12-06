from hera.action import GRPCAction, HTTPGetAction, HTTPHeader, Scheme, TCPSocketAction, ExecAction
import pytest
from argo_workflows.models import GRPCAction as ArgoGRPCAction, ExecAction as ArgoExecAction, \
    HTTPHeader as ArgoHTTPHeader, HTTPGetAction as ArgoHTTPGetAction, TCPSocketAction as ArgoTCPSocketAction


class TestAction:
    def test_scheme(self):
        assert len(Scheme) == 2
        assert Scheme.http.value == "HTTP"
        assert Scheme.https.value == "HTTPS"

    def test_grpc_action(self):
        with pytest.raises(AssertionError) as e:
            GRPCAction(-1)
        assert str(e.value) == "GRPC port number must be between 1 and 65535"

        a = GRPCAction(443).build()
        assert isinstance(a, ArgoGRPCAction)
        assert not hasattr(a, "service")

        a = GRPCAction(443, service="abc").build()
        assert isinstance(a, ArgoGRPCAction)
        assert hasattr(a, "service")
        assert a.service == "abc"

    def test_exec_action(self):
        a = ExecAction(["a", "b", "c"]).build()
        assert isinstance(a, ArgoExecAction)
        assert hasattr(a, "command")
        assert a.command == ["a", "b", "c"]

        a = ExecAction().build()
        assert isinstance(a, ArgoExecAction)
        assert not hasattr(a, "command")

    def test_http_header(self):
        h = HTTPHeader("a", "123").build()
        assert isinstance(h, ArgoHTTPHeader)
        assert hasattr(h, "name")
        assert h.name == "a"
        assert hasattr(h, "value")
        assert h.value == "123"

    def test_http_get_action(self):
        a = HTTPGetAction("443").build()
        assert isinstance(a, ArgoHTTPGetAction)
        assert hasattr(a, "port")
        assert not hasattr(a, "host")
        assert not hasattr(a, "http_headers")
        assert not hasattr(a, "path")
        assert not hasattr(a, "scheme")

        a = HTTPGetAction("443", host="abc", http_headers=[HTTPHeader("a", "1")], path="/test",
                          scheme=Scheme.https).build()
        assert isinstance(a, ArgoHTTPGetAction)
        assert hasattr(a, "port")
        assert hasattr(a, "host")
        assert hasattr(a, "http_headers")
        assert len(a.http_headers) == 1
        assert a.http_headers[0].name == "a"
        assert a.http_headers[0].value == "1"
        assert hasattr(a, "path")
        assert hasattr(a, "scheme")

    def test_tcp_socket_action(self):
        a = TCPSocketAction("443").build()
        assert isinstance(a, ArgoTCPSocketAction)
        assert hasattr(a, "port")
        assert a.port == "443"
        assert not hasattr(a, "host")

        a = TCPSocketAction("443", host="abc").build()
        assert isinstance(a, ArgoTCPSocketAction)
        assert hasattr(a, "port")
        assert a.port == "443"
        assert hasattr(a, "host")
        assert a.host == "abc"

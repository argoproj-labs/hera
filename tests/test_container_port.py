from hera.port import Protocol, ContainerPort, ArgoContainerPort
import pytest


class TestPort:

    def test_protocol(self):
        assert len(Protocol) == 3
        assert Protocol.udp == "UDP"
        assert Protocol.tcp == "TCP"
        assert Protocol.sctp == "SCTP"

    def test_container_port(self):
        with pytest.raises(AssertionError) as e:
            ContainerPort(-1)
        assert str(e.value) == "`container_port` must be an integer value between 0 and 65535"

        with pytest.raises(AssertionError) as e:
            ContainerPort(443, host_port=-1)
        assert str(e.value) == "`host_port` must be an integer value between 0 and 65535"

        c = ContainerPort(443).build()
        assert isinstance(c, ArgoContainerPort)
        assert hasattr(c, "container_port")
        assert c.container_port == 443
        assert not hasattr(c, "host_ip")
        assert not hasattr(c, "host_port")
        assert not hasattr(c, "name")
        assert not hasattr(c, "protocol")

        c = ContainerPort(443, host_ip="0.0.0.0", host_port=443, name="test", protocol=Protocol.tcp).build()
        assert isinstance(c, ArgoContainerPort)
        assert hasattr(c, "container_port")
        assert c.container_port == 443
        assert hasattr(c, "host_ip")
        assert c.host_ip == "0.0.0.0"
        assert hasattr(c, "host_port")
        assert c.host_port == 443
        assert hasattr(c, "name")
        assert c.name == "test"
        assert hasattr(c, "protocol")
        assert c.protocol == "TCP"

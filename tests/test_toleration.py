from hera import Toleration


def test_toleration_translates():
    hera_t = Toleration(key="a", effect="NoSchedule", operator="Equal", value="value123")
    argo_t = hera_t.build()
    assert hasattr(argo_t, "key")
    assert hera_t.key == getattr(argo_t, "key")
    assert hasattr(argo_t, "effect")
    assert hera_t.effect == getattr(argo_t, "effect")
    assert hasattr(argo_t, "operator")
    assert hera_t.operator == getattr(argo_t, "operator")
    assert hasattr(argo_t, "value")
    assert hera_t.value == getattr(argo_t, "value")

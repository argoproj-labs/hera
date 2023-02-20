from hera.workflows import ImagePullPolicy


class TestImagePullPolicy:
    def test_str_returns_expected_value(self):
        assert str(ImagePullPolicy.Always) == "Always"
        assert str(ImagePullPolicy.Never) == "Never"
        assert str(ImagePullPolicy.IfNotPresent) == "IfNotPresent"
        assert len(ImagePullPolicy) == 3

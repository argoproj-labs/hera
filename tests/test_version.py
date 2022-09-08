from hera import __version__, __version_info__


def test_version():
    version = __version__
    version_info = __version_info__

    assert isinstance(version, str)
    assert len(version_info) == 3
    try:
        int(version_info[0])
        int(version_info[1])
        int(version_info[2])
    except Exception:
        raise

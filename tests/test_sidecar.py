from argo_workflows.models import IoArgoprojWorkflowV1alpha1UserContainer

from hera import (
    ContainerPort,
    Env,
    ImagePullPolicy,
    Lifecycle,
    LifecycleHandler,
    Probe,
    Resources,
    SecretEnvFrom,
    Sidecar,
    TaskSecurityContext,
    VolumeDevice,
    VolumeMount,
)


class TestSideCar:
    def test_builds_expected_container(self):
        s = Sidecar("test").build()
        assert isinstance(s, IoArgoprojWorkflowV1alpha1UserContainer)
        assert hasattr(s, "name")
        assert s.name == "test"
        assert not hasattr(s, "args")
        assert not hasattr(s, "command")
        assert not hasattr(s, "env")
        assert not hasattr(s, "env_from")
        assert not hasattr(s, "image")
        assert not hasattr(s, "image_pull_policy")
        assert not hasattr(s, "lifecycle")
        assert not hasattr(s, "liveness_probe")
        assert not hasattr(s, "mirror_volume_mounts")
        assert not hasattr(s, "ports")
        assert not hasattr(s, "readiness_probe")
        assert not hasattr(s, "resources")
        assert not hasattr(s, "security_context")
        assert not hasattr(s, "startup_probe")
        assert not hasattr(s, "stdin")
        assert not hasattr(s, "stdin_once")
        assert not hasattr(s, "termination_message_path")
        assert not hasattr(s, "termination_message_policy")
        assert not hasattr(s, "tty")
        assert not hasattr(s, "volume_devices")
        assert not hasattr(s, "volume_mounts")
        assert not hasattr(s, "working_dir")

        s = Sidecar(
            "test",
            args=["a", "b", "c"],
            command=["test"],
            env=[Env("e", value="test")],
            env_from=[SecretEnvFrom("abc")],
            image="python:3.7",
            image_pull_policy=ImagePullPolicy.Always,
            lifecycle=Lifecycle(post_start=LifecycleHandler(), pre_stop=LifecycleHandler()),
            liveness_probe=Probe(),
            mirror_volume_mounts=True,
            ports=[ContainerPort(443)],
            readiness_probe=Probe(),
            resources=Resources(),
            security_context=TaskSecurityContext(),
            startup_probe=Probe(),
            stdin=True,
            stdin_once=True,
            termination_message_path="/log",
            termination_message_policy="File",
            tty=True,
            volume_devices=[VolumeDevice("v", "/test")],
            volume_mounts=[VolumeMount("/mnt/test")],
            working_dir="/",
        ).build()
        assert isinstance(s, IoArgoprojWorkflowV1alpha1UserContainer)
        assert hasattr(s, "name")
        assert hasattr(s, "args")
        assert hasattr(s, "command")
        assert hasattr(s, "env")
        assert hasattr(s, "env_from")
        assert hasattr(s, "image")
        assert hasattr(s, "image_pull_policy")
        assert hasattr(s, "lifecycle")
        assert hasattr(s, "liveness_probe")
        assert hasattr(s, "mirror_volume_mounts")
        assert hasattr(s, "ports")
        assert hasattr(s, "readiness_probe")
        assert hasattr(s, "resources")
        assert hasattr(s, "security_context")
        assert hasattr(s, "startup_probe")
        assert hasattr(s, "stdin")
        assert hasattr(s, "stdin_once")
        assert hasattr(s, "termination_message_path")
        assert hasattr(s, "termination_message_policy")
        assert hasattr(s, "tty")
        assert hasattr(s, "volume_devices")
        assert hasattr(s, "volume_mounts")
        assert hasattr(s, "working_dir")

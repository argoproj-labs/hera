from hera.global_config import _GlobalConfig
from hera.task import Task
from hera.workflow import Workflow


class TestGlobalConfig:
    def test_host(self):
        c = _GlobalConfig()
        assert c.host is None
        c.host = '123'
        assert c.host == '123'
        c.reset()

    def test_token(self):
        c = _GlobalConfig()
        assert c.token is None
        c.token = '123'
        assert c.token == '123'
        c.token = lambda: '123'
        assert c.token == '123'
        c.reset()

    def test_verify_ssl(self):
        c = _GlobalConfig()
        assert c.verify_ssl
        c.verify_ssl = False
        assert not c.verify_ssl
        c.reset()

    def test_api_version(self):
        c = _GlobalConfig()
        assert c.api_version == "argoproj.io/v1alpha1"
        c.api_version = "123"
        assert c.api_version == "123"
        c.reset()

    def test_namespace(self):
        c = _GlobalConfig()
        assert c.namespace == "default"
        c.namespace = "123"
        assert c.namespace == "123"
        c.reset()

    def test_image(self):
        c = _GlobalConfig()
        assert c.image == "python:3.7"
        c.image = "123"
        assert c.image == "123"
        c.reset()

    def test_service_account_name(self):
        c = _GlobalConfig()
        assert c.service_account_name is None
        c.service_account_name = "123"
        assert c.service_account_name == "123"
        c.reset()

    def test_task_post_init_hooks(self):
        c = _GlobalConfig()
        assert c.task_post_init_hooks == ()

        def hook1(t: Task) -> None:
            t.name = '123'

        def hook2(t: Task) -> None:
            t.image = "abc"

        c.task_post_init_hooks = [hook1, hook2]
        assert len(c.task_post_init_hooks) == 2

        c.task_post_init_hooks = [hook1, hook2]
        assert len(c.task_post_init_hooks) == 4
        c.reset()

    def test_workflow_post_init_hooks(self):
        c = _GlobalConfig()
        assert c.workflow_post_init_hooks == ()

        def hook1(w: Workflow) -> None:
            w.name = '123'

        def hook2(w: Workflow) -> None:
            w.service_account_name = "abc"

        c.workflow_post_init_hooks = [hook1, hook2]
        assert len(c.workflow_post_init_hooks) == 2

        c.workflow_post_init_hooks = [hook1, hook2]
        assert len(c.workflow_post_init_hooks) == 4
        c.reset()

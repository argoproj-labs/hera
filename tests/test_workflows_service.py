from hera.workflows.service import WorkflowsService


class TestWorkflowsService:
    def test_token_is_none_when_not_specified(self):
        service = WorkflowsService()
        assert service.token is None

        service = WorkflowsService(token=None)
        assert service.token is None

    def test_adds_bearer_suffix_to_token(self, global_config_fixture):
        global_config_fixture.token = "token"
        service = WorkflowsService()
        assert service.token == "Bearer token"

        global_config_fixture.token = lambda: "lambda-token"
        service = WorkflowsService()
        assert service.token == "Bearer lambda-token"

        service = WorkflowsService(token="token")
        assert service.token == "Bearer token"

    def test_does_not_add_bearer_suffix_if_already_present(self, global_config_fixture):
        global_config_fixture.token = "Bearer token"
        service = WorkflowsService()
        assert service.token == "Bearer token"

        service = WorkflowsService(token="Bearer token")
        assert service.token == "Bearer token"

    def test_adds_custom_token(self):
        service = WorkflowsService(token="something token")
        assert service.token == "something token"

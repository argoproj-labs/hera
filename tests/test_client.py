from argo_workflows.api_client import ApiClient as ArgoApiClient

from hera import Client, Config


def test_client_has_expected_fields():
    config = Config(host="localhost")
    header_name = "Authorization"
    header_value = "Bearer token"
    expected = ArgoApiClient(configuration=config.config, header_name=header_name, header_value=header_value)
    actual = Client(config, "token").api_client
    assert actual.configuration == expected.configuration
    assert actual.default_headers[header_name] == expected.default_headers[header_name] == header_value

"""A collection of scripts and objects that are used to construct the Hera services for workflows and events."""

import builtins
import inspect
import re
import sys
from pathlib import Path
from typing import List, Optional

import requests

from hera.events import models as events_models
from hera.workflows import models as workflows_models

model_types = {"workflows", "events"}


class Parameter:
    """A representation of a function parameter."""

    def __init__(self, name: str, field: str, in_: str, type_: type, required: bool) -> None:
        """Instantiates a parameter.

        Args:
            name: (str) the name of the parameter.
            field: (str) the body field that this parameter is used on.
            in_: (str) the type of request object this parameter is used in - body, query, or path.
            type_: (type) the proper `type` of the parameter.
            required: (bool) whether the `Parameter` is required.
        """
        self.name = name
        self.field = field
        self.in_ = in_  # body, query, path
        self.type_ = type_
        self.required = required

    def __str__(self) -> str:
        """Returns the string representation of the parameter, with its name + type."""
        if self.required:
            return f"{self.name}: {self.type_.__name__}"
        else:
            return f"{self.name}: Optional[{self.type_.__name__}] = None"


class Response:
    """The request response type."""

    def __init__(self, ref: str) -> None:
        """Instantiate a response.

        Args:
            ref: (str) the reference of the return type.
        """
        self.ref = ref

    def __str__(self) -> str:
        """Return the string representation of the response type."""
        return f"{self.ref}"


class ServiceEndpoint:
    """A response endpoint representation for Argo service endpoints."""

    def __init__(
        self,
        url: str,
        method: str,
        name: str,
        params: List[Parameter],
        response: Response,
        summary: Optional[str] = "API Documentation.",
        consumes: str = "application/json",
        produces: str = "application/json",
    ) -> None:
        """Instantiate a service endpoint.

        Args:
            url: (str) the relative URL of the endpoint.
            method: (str) the method of the endpoint: put, end, post.
            name: (str) the name of the endpoint. Used to create the service API definitions.
            params: (List[Parameter]) the parameters of the endpoint. Used to create the service API definitions.
            response: (Response) the response of the endpoint. Used to create the service API definitions.
            summary: (Optional[str] = None) summary documentation of the endpoint, if available.
            consumes: (str = "application/json") the consumption payload type of the endpoint.
            produces: (str = "application/json") the response payload type of the endpoint.
        """
        self.url = self.parse_url(url)
        self.method = method
        self.name = name
        # these need to be sorted as they are used to create the function signature. Required parameters must be
        # prioritized. Note that we set `reverse=True` since `False` will be sorted before `True`
        self.params = sorted(params, key=lambda p: p.required, reverse=True)
        self.response = response
        self.summary = summary
        self.consumes = consumes
        self.produces = produces

    def parse_url(self, url: str) -> str:
        """Parses the given URL and returns the path only."""
        if url[0] == "/":
            return url[1:]
        return url

    def __str__(self) -> str:
        """Builds the entire string signature of the service endpoints."""
        if len(self.params) == 0:
            signature = f"def {self.name}(self) -> {self.response}:"
        else:
            signature = "def {name}(self, {params}) -> {ret}:"
            params = ", ".join([str(p) for p in self.params])
            signature = signature.format(
                name=self.name,
                params=params,
                ret=str(self.response),
            )

        # docstring
        signature = f"""{signature}
        \"\"\"{self.summary}\"\"\""""

        # url
        path_params = [p for p in self.params if p.in_ == "path"]
        if len(path_params) == 0:
            req_url = f"urljoin(self.host, '{self.url}')"
        else:
            # note that here we have a condition on `namespace` because `namespace` can be a global configuration. So,
            # we either take it from the endpoint (prioritized just in case users rely on the service to use
            # generated models but not Hera models) or from the global configuration
            req_url_params = []
            for p in path_params:
                if p.name == "namespace":
                    req_url_params.append("namespace=namespace if namespace is not None else self.namespace")
                else:
                    req_url_params.append(f"{p.field}={p.name}")
            req_url = f"urljoin(self.host, '{self.url}').format({', '.join(req_url_params)})"

        # query params
        query_params = [p for p in self.params if p.in_ == "query"]
        if len(query_params) > 0:
            params = "{" + ", ".join([f"'{p.field}': {p.name}" for p in query_params]) + "}"
        else:
            params = "None"

        # headers
        headers = "{'Authorization': self.token"
        if self.method.lower() == "post" or self.method.lower() == "put":
            headers += f", 'Content-Type': '{self.consumes}'"
        headers += "}"

        # body/data
        body_params = [p for p in self.params if p.in_ == "body"]
        assert len(body_params) <= 1, str(body_params)
        if len(body_params) == 0:
            body = "None"
        else:
            bp = body_params[0]
            assert bp.name == "req", bp.name
            body = (
                "req.json("
                "exclude_none=True, "
                "by_alias=True, "
                "skip_defaults=True, "
                "exclude_unset=True, "
                "exclude_defaults=True"
                ")"
            )

        # return value
        if self.response.ref == "str":
            ret_val = "str(resp.content)"
        elif "Response" in self.response.ref and "InfoResponse" not in self.response.ref:
            ret_val = f"{self.response}()"
        else:
            ret_val = f"{self.response}(**resp.json())"

        return f"""
    {signature}
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.{self.method}(
            url={req_url},
            params={params},
            headers={headers},
            data={body},
            verify=self.verify_ssl,
            cert=self.client_certs,
        )

        if resp.ok:
            return {ret_val}
        
        raise exception_from_server_response(resp)
"""


def get_models_type() -> str:
    """Gets the model type to generate from argv and returns it. This is either `workflows` or `events`."""
    assert len(sys.argv) == 3, "Expected two argv arguments - the Argo OpenAPI spec URL and [workflows|events]"
    arg = sys.argv[2]
    assert arg in model_types, f"Unsupported model type {arg}, expected one of {model_types}"
    return arg


def get_openapi_spec_url() -> str:
    """Gets the OpenAPI spec URL from argv and returns it."""
    assert len(sys.argv) == 3, "Expected a single argv argument - the Argo OpenAPI spec URL"
    return sys.argv[1]


def fetch_openapi_spec(url: str) -> dict:
    """Fetches the OpenAPI specification at the given URI."""
    response = requests.get(url)
    if response.ok:
        return response.json()
    raise ValueError(
        f"Did not receive an ok response from fetching the OpenAPI spec payload from url {url}, "
        f"status {response.status_code}"
    )


def get_consumes(payload: dict) -> str:
    """Gets the OpenAPI `consumes` field."""
    consumes = payload.get("consumes")
    assert isinstance(consumes, list), f"Expected `consumes` to be of list type, received {type(consumes)}"
    assert len(consumes) == 1, "Expected `consumes` payload to contain a single item e.g. 'application/json'"
    return consumes[0]


def get_produces(payload: dict) -> str:
    """Gets the OpenAPI `produces` field."""
    produces = payload.get("produces")
    assert isinstance(produces, list), f"Expected `produces` to be of list type, received {type(produces)}"
    assert len(produces) == 1, "Expected `produces` payload to contain a single item e.g. 'application/json'"
    return produces[0]


def get_paths(payload: dict) -> dict:
    """Gets the OpenAPI `paths` field."""
    paths = payload.get("paths")
    assert isinstance(paths, dict), f"Expected `paths` to be of dictionary type, received {type(paths)}"
    return paths


def camel_to_snake(s: str) -> str:
    """Converts the given string from camel case to snake cased."""
    return re.sub(r"(?<!^)(?=[A-Z])", "_", s)


def snake_to_camel(s: str) -> str:
    """Converts the given string from snake case to camel cased."""
    components = s.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def parse_operation_id(operation_id: str) -> str:
    """Parses the given operation ID into a service endpoint definition."""
    if "UID" in operation_id:
        operation_id = operation_id.replace("UID", "Uid")
    operation = operation_id.split("_")[-1]
    operation_snake_case = camel_to_snake(operation).lower()
    return operation_snake_case.lower()


def get_class(cls_name: str, models_type: str) -> type:
    """Returns the Argo Workflows/Events class association based on the specified models type.

    This intentionally has an empty return to catch cases when the class it not found. This will cause dep
    code to fail so users know service generation failed.
    """
    switch = {"workflows": workflows_models, "events": events_models}
    modules = inspect.getmembers(switch.get(models_type))
    for module in modules:
        curr_cls = module[1]
        if inspect.isclass(curr_cls) and curr_cls.__name__ == cls_name:
            return curr_cls


def parse_builtin(f: str) -> str:
    """Parses built in statements to dunder representations."""
    if f in dir(builtins) or f in ["continue", "pass", "in"]:
        return f"{f}_"
    return f


def parse_parameter(parameter: dict, models_type: str) -> Parameter:
    """Parses the given dictionary of a `Parameter` into a proper `Parameter` type based on model type."""
    openapi_type_switch = {
        "string": str,
        "number": float,
        "integer": int,
        "boolean": bool,
        "array": list,
        "object": object,
    }
    name_ = parameter.get("name").split(".")[-1]
    name = parameter.get("name")
    required = parameter.get("required", False)
    in_ = parameter.get("in")

    # there are some parameter name exceptions due to aliases in Hera
    if "type" in parameter:
        type_ = openapi_type_switch.get(parameter.get("type"))
    elif "schema" in parameter:
        type_ = get_class(parameter.get("schema").get("$ref").split(".")[-1], models_type)
    else:
        raise ValueError(f"Unrecognized parameter type from parameter {parameter}")

    if name_ == "body":
        name_ = "req"
    if "TLS" in name_:
        name_ = name_.replace("TLS", "Tls")

    name_ = camel_to_snake(name_)
    name_ = parse_builtin(name_)
    name_ = name_.lower()

    # a lot of endpoints use a parameter called `namespace`. The Hera service uses `namespace` as an optional keyword
    # because it's actually set on the service itself. Here, we check for `namespace` and intentionally make
    # it optional
    if name_ == "namespace":
        return Parameter(name_, name, in_, type_, False)
    return Parameter(name_, name, in_, type_, required)


def parse_response(parameter: dict) -> Response:
    """Parses the return parameter into a proper `Response`."""
    responses = parameter.get("responses")
    ok_resp = responses.get("200")

    schema = ok_resp.get("schema")
    if "$ref" in schema:
        ref = schema.get("$ref").split(".")[-1]
    elif "properties" in schema:
        properties = schema.get("properties")
        result = properties.get("result")
        ref = result.get("$ref").split(".")[-1]
    elif "type" in schema and "format" in schema and schema.get("format") == "binary":
        ref = "str"
    else:
        raise ValueError(f"Unrecognized schema {schema}")
    return Response(ref)


def get_endpoints(
    paths: dict,
    models_type: str,
    consumes: str = "application/json",
    produces: str = "application/json",
) -> List[ServiceEndpoint]:
    """Assembles a series of endpoints for the service definition."""
    switch = {
        "workflows": ["events", "event", "eventsource", "sensor"],
        "events": ["workflow", "workflows"],
    }
    exceptions = switch.get(models_type)
    endpoints = []
    for url, config in paths.items():
        found = False
        for exception in exceptions:
            if exception in url:
                found = True
        if found:
            continue

        for method, params in config.items():
            empty_param = False
            operation_id = parse_operation_id(params.get("operationId"))
            endpoint_params = []
            for parameter in params.get("parameters", []):
                param = parse_parameter(parameter, models_type)
                if param.type_ is None:
                    empty_param = True
                endpoint_params.append(param)
            response = parse_response(params)
            summary = params.get("summary", "API documentation.")
            if empty_param:
                continue  # skip this endpoint

            # exceptions for events
            if operation_id == "event_sources_logs" and response.ref == "LogEntry":
                response.ref = "EventsourceLogEntry"
            if operation_id == "sensors_logs" and response.ref == "LogEntry":
                response.ref = "SensorLogEntry"

            endpoints.append(
                ServiceEndpoint(
                    url,
                    method,
                    operation_id,
                    endpoint_params,
                    response,
                    summary,
                    consumes=consumes,
                    produces=produces,
                )
            )
    return endpoints


def get_service_def() -> str:
    """Assembles the service definition string/code representation."""
    return """
\"\"\"Interact with the REST service.\"\"\"
# [DO NOT MODIFY] Auto-generated by `hera.scripts.service.py`
from urllib.parse import urljoin
import requests
import os
from hera.{module}.models import {imports}
from hera.shared import global_config
from hera.exceptions import exception_from_server_response
from typing import Optional, Tuple, cast

def valid_host_scheme(host: str) -> bool:
    \"\"\"Validates the the given `host` starts with either `http` or `https`.\"\"\"
    return host.startswith("http://") or host.startswith("https://")    

class {models_type}Service:
    \"\"\"The core {doc_models_type} service for interacting with the Argo server.\"\"\"
    def __init__(
        self,
        host: Optional[str] = None,
        verify_ssl: Optional[bool] = None,
        token: Optional[str] = None,
        client_certs: Optional[Tuple[str, str]] = None,
        namespace: Optional[str] = None,
    ) -> None:
        \"\"\"{models_type} service constructor.\"\"\"
        self.host = cast(str, host or global_config.host)
        self.verify_ssl = verify_ssl if verify_ssl is not None else global_config.verify_ssl
        self.client_certs = client_certs if client_certs is not None else global_config.client_certs

        # some users reported in https://github.com/argoproj-labs/hera/issues/1016 that it can be a bit awkward for 
        # Hera to assume a `Bearer` prefix on behalf of users. Some might pass it and some might not. Therefore, Hera
        # only prefixes the token with `Bearer ` if it's not already specified and lets the uses specify it otherwise.
        # Note that the `Bearer` token can be specified through the global configuration as well. In order to deliver 
        # a fix on Hera V5 without introducing breaking changes, we have to support both
        global_config_token = global_config.token  # call only once because it can be a user specified function!
        
        def format_token(t):
            parts = t.strip().split()
            if len(parts) == 1:
                return "Bearer " + t
            return t

        if token:
            self.token: Optional[str] = format_token(token)
        elif global_config_token:
            self.token = format_token(global_config_token)
        else:
            self.token = None

        self.namespace = namespace or global_config.namespace
"""


def add_get_workflow_link(service_def: str) -> str:
    """Adds a custom method to the service for fetching a workflow link."""
    return (
        service_def
        + """
    def get_workflow_link(self, name: str) -> str:
        \"\"\"Returns the workflow link for the given workflow name.\"\"\"
        return os.path.join(self.host, f"workflows/{self.namespace}/{name}?tab=workflow")
"""
    )


def add_get_cron_workflow_link(service_def: str) -> str:
    """Adds a custom method to the service for fetching a cron workflow link."""
    return (
        service_def
        + """
    def get_cron_workflow_link(self, name: str) -> str:
        \"\"\"Returns the link for the given cron workflow name.\"\"\"
        return os.path.join(self.host, f"cron-workflows/{self.namespace}/{name}")
"""
    )


def make_service(service_def: str, endpoints: List[ServiceEndpoint], models_type: str) -> str:
    """Makes the service definitions based on the given endpoints for the given model type."""
    result = service_def
    for endpoint in endpoints:
        result = result + f"{endpoint}\n"

    if models_type in {"workflows"}:
        result = add_get_workflow_link(result)
        result = add_get_cron_workflow_link(result)
    result += f"\n\n__all__ = ['{models_type.capitalize()}Service']"
    return result


def write_service(service: str, path: Path) -> None:
    """Writes the service code to the specified path."""
    with open(str(path), "w+") as f:
        f.write(service)


def get_imports(endpoints: List[ServiceEndpoint]) -> List[str]:
    """Assembles a series of imports, which are dependencies of the given endpoints."""
    result = []
    builtins = dir(__builtins__)
    for endpoint in endpoints:
        for param in endpoint.params:
            try:
                if param.type_.__module__ == "builtins":
                    continue
                result.append(param.type_.__name__)
            except Exception:
                raise

        if endpoint.response.ref in builtins:
            continue
        result.append(endpoint.response.ref)
    return list(set(result))


if __name__ == "__main__":
    url = get_openapi_spec_url()
    models_type = get_models_type()
    payload = fetch_openapi_spec(url)
    consumes = get_consumes(payload)
    produces = get_produces(payload)
    paths = get_paths(payload)
    endpoints = get_endpoints(paths, models_type, consumes=consumes, produces=produces)
    imports = get_imports(endpoints)
    service_def = get_service_def()
    service_def = service_def.format(
        imports=", ".join(imports),
        module=models_type,
        models_type=models_type.capitalize(),
        doc_models_type=models_type.lower(),
    )
    result = make_service(service_def, endpoints, models_type)

    if models_type == "workflows":
        result = result.replace("LogEntry", "V1alpha1LogEntry")

    path = Path(__name__).parent / f"src/hera/{models_type}/service.py"
    write_service(result, path)

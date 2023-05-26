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
    """A representation of a function parameter.

    Parameters
    ----------
    name: str
        The name of the parameter.
    field: str
        The body field that this parameter is used on.
    in_: str
        The type of request object this parameter is used in - body, query, or path.
    type_: type
        The proper `type` of the parameter.
    required: bool
        Whether the `Parameter` is required.
    """

    def __init__(self, name: str, field: str, in_: str, type_: type, required: bool) -> None:
        self.name = name
        self.field = field
        self.in_ = in_  # body, query, path
        self.type_ = type_
        self.required = required

    def __str__(self) -> str:
        if self.required:
            return f"{self.name}: {self.type_.__name__}"
        else:
            return f"{self.name}: Optional[{self.type_.__name__}] = None"


class Response:
    """The response type of a request"""

    def __init__(self, ref: str) -> None:
        self.ref = ref

    def __str__(self) -> str:
        return f"{self.ref}"


class ServiceEndpoint:
    """A response endpoint representation for Argo service endpoints.

    Parameters
    ----------
    url: str
        The relative URL of the endpoint.
    method: str
        The method of the endpoint: put, end, post.
    name: str
        The name of the endpoint. Used to create the service API definitions.
    params: List[Parameter]
        The parameters of the endpoint. Used to create the service API definitions.
    response: Response
        The response of the endpoint. Used to create the service API definitions.
    summary: Optional[str] = None
        Summary documentation of the endpoint, if available.
    consumes: str = "application/json"
        The consumption payload type of the endpoint.
    produces: str = "application/json"
        The response payload type of the endpoint.
    """

    def __init__(
        self,
        url: str,
        method: str,
        name: str,
        params: List[Parameter],
        response: Response,
        summary: Optional[str] = None,
        consumes: str = "application/json",
        produces: str = "application/json",
    ) -> None:
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

    def parse_url(self, url) -> str:
        if url[0] == "/":
            return url[1:]
        return url

    def __str__(self) -> str:
        # signature
        if len(self.params) == 0:
            signature = f"def {self.name}(self) -> {self.response}:"
        else:
            signature = "def {name}(self, {params}) -> {ret}:"
            params = ", ".join([str(p) for p in self.params])
            signature = signature.format(
                name=self.name,
                params=params,
                ret=str(self.response),
                summary=self.summary,
            )

        # docstring
        if self.summary is not None:
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
        headers = "{'Authorization': f'Bearer {self.token}'}"

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
        elif "Response" in self.response.ref:
            ret_val = f"{self.response}()"
        elif "CronWorkflow" in self.response.ref:
            # when users schedule cron workflows that have not executed the moment they are scheduled, the response
            # does contain `CronWorkflowStatus` but its fields are empty. However, the `CronWorkflowStatus` object,
            # while option on `CronWorkflow`, has *required* fields. Here, we overwrite the response with a special
            # case that handles setting the `CronWorkflowStatus` to `None` if the response is empty.
            return f"""
    {signature}
        resp = requests.{self.method}(
            url={req_url},
            params={params},
            headers={headers},
            data={body},
            verify=self.verify_ssl
        )

        if resp.ok:
            resp_json = resp.json()
            if "status" in resp_json and resp_json["status"]['active'] is None and resp_json["status"]['lastScheduledTime'] is None and resp_json["status"]['conditions'] is None:
                # this is a necessary special case as the status fields cannot be empty on the `CronWorkflowStatus`
                # object. So, we overwrite the response with a value that allows the response to pass through safely.
                # See `hera.scripts.service.ServiceEndpoint.__str__` for more details.
                resp_json['status'] = None
            return {self.response}(**resp_json)
        raise exception_from_status_code(
            resp.status_code, 
            f"Server returned status code {{resp.status_code}} with error: {{resp.json()}}",
        )
        """
        else:
            ret_val = f"{self.response}(**resp.json())"

        return f"""
    {signature}
        resp = requests.{self.method}(
            url={req_url},
            params={params},
            headers={headers},
            data={body},
            verify=self.verify_ssl
        )

        if resp.ok:
            return {ret_val}
        raise exception_from_status_code(
            resp.status_code, 
            f"Server returned status code {{resp.status_code}} with error: {{resp.json()}}",
        )
"""


def get_models_type() -> str:
    """Gets the model type to generate from argv and returns it. This is either `workflows` or `events`"""
    assert len(sys.argv) == 3, "Expected two argv arguments - the Argo OpenAPI spec URL and [workflows|events]"
    arg = sys.argv[2]
    assert arg in model_types, f"Unsupported model type {arg}, expected one of {model_types}"
    return arg


def get_openapi_spec_url() -> str:
    """Gets the OpenAPI spec URL from argv and returns it"""
    assert len(sys.argv) == 3, "Expected a single argv argument - the Argo OpenAPI spec URL"
    return sys.argv[1]


def fetch_openapi_spec(url: str) -> dict:
    """Fetches the OpenAPI specification at the given URI"""
    response = requests.get(url)
    if response.ok:
        return response.json()
    raise ValueError(
        f"Did not receive an ok response from fetching the OpenAPI spec payload from url {url}, "
        f"status {response.status_code}"
    )


def get_consumes(payload: dict) -> str:
    """Gets the OpenAPI `consumes` field"""
    consumes = payload.get("consumes")
    assert isinstance(consumes, list), f"Expected `consumes` to be of list type, received {type(consumes)}"
    assert len(consumes) == 1, "Expected `consumes` payload to contain a single item e.g. 'application/json'"
    return consumes[0]


def get_produces(payload: dict) -> str:
    """Gets the OpenAPI `produces` field"""
    produces = payload.get("produces")
    assert isinstance(produces, list), f"Expected `produces` to be of list type, received {type(produces)}"
    assert len(produces) == 1, "Expected `produces` payload to contain a single item e.g. 'application/json'"
    return produces[0]


def get_paths(payload: dict) -> dict:
    """Gets the OpenAPI `paths` field"""
    paths = payload.get("paths")
    assert isinstance(paths, dict), f"Expected `paths` to be of dictionary type, received {type(paths)}"
    return paths


def camel_to_snake(s: str) -> str:
    """Converts the given string from camel case to snake cased"""
    return re.sub(r"(?<!^)(?=[A-Z])", "_", s)


def snake_to_camel(s: str) -> str:
    """Converts the given string from snake case to camel cased"""
    components = s.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def parse_operation_id(operation_id: str) -> str:
    """Parses the given operation ID into a service endpoint definition"""
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
    """Parses built in statements to dunder representations"""
    if f in dir(builtins) or f in ["continue", "pass", "in"]:
        return f"{f}_"
    return f


def parse_parameter(parameter: dict, models_type: str) -> Parameter:
    """Parses the given dictionary representation of a `Parameter` into a proper `Parameter` type based on model type"""
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
    """Parses the return parameter into a proper `Response`"""
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
    """Assembles a series of endpoints for the service definition"""
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
            summary = params.get("summary")
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
    """Assembles the service definition string/code representation"""
    return """
from urllib.parse import urljoin
import requests
from hera.{module}.models import {imports}
from hera.shared import global_config
from hera.shared.exceptions import exception_from_status_code
from typing import Optional, cast

class {models_type}Service:
    def __init__(
        self,
        host: Optional[str] = None,
        verify_ssl: Optional[bool] = None,
        token: Optional[str] = None,
        namespace: Optional[str] = None,
    ):
        self.host = cast(str, host or global_config.host)
        self.verify_ssl = verify_ssl if verify_ssl is not None else global_config.verify_ssl
        self.token = token or global_config.token
        self.namespace = namespace or global_config.namespace
"""


def make_service(service_def: str, endpoints: List[ServiceEndpoint], models_type: str) -> str:
    """Makes the service definitions based on the given endpoints for the given model type"""
    result = service_def
    for endpoint in endpoints:
        result = result + f"{endpoint}\n"
    result = result + f"\n\n__all__ = ['{models_type.capitalize()}Service']"
    return result


def write_service(service: str, path: Path) -> None:
    """Writes the service code to the specified path"""
    with open(str(path), "w+") as f:
        f.write(service)


def get_imports(endpoints: List[ServiceEndpoint]) -> List[str]:
    """Assembles a series of imports, which are dependencies of the given endpoints"""
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
    )
    result = make_service(service_def, endpoints, models_type)

    if models_type == "workflows":
        result = result.replace("LogEntry", "V1alpha1LogEntry")
    elif models_type == "events":
        result = result.replace("LogEntry", "LogEntry")

    path = Path(__name__).parent / f"src/hera/{models_type}/service.py"
    write_service(result, path)

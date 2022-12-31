import builtins
import inspect
import re
import sys
from pathlib import Path
from typing import List, Optional

import requests

from hera import models


class Parameter:
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
    def __init__(self, ref: str) -> None:
        self.ref = ref

    def __str__(self) -> str:
        return f"{self.ref}"


class ServiceEndpoint:
    def __init__(
        self,
        url,
        method: str,
        name: str,
        params: List[Parameter],
        response: Response,
        summary: Optional[str] = None,
        consumes: str = "application/json",
        produces: str = "application/json",
    ) -> None:
        self.url = url
        self.method = method
        self.name = name
        self.params = params
        self.response = response
        self.summary = summary
        self.consumes = consumes
        self.produces = produces

    def __str__(self) -> str:
        # signature
        if len(self.params) == 0:
            signature = f"def {self.name}(self) -> {self.response}:"
        else:
            signature = "def {name}(self, {params}) -> {ret}:"
            params = ", ".join([str(p) for p in self.params])
            signature = signature.format(name=self.name, params=params, ret=str(self.response), summary=self.summary)

        # docstring
        if self.summary is not None:
            signature = f"""{signature}
        \"\"\"{self.summary}\"\"\""""

        # url
        path_params = [p for p in self.params if p.in_ == "path"]
        if len(path_params) == 0:
            req_url = f"os.path.join(self.host, '{self.url}')"
        else:
            req_url_params = ", ".join([f"{p.field}={p.name}" for p in path_params])
            req_url = f"os.path.join(self.host, '{self.url}').format({req_url_params})"

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
            body = "req.json()"

        # return value
        if self.response.ref == "str":
            ret_val = "str(resp.content)"
        elif "Response" in self.response.ref:
            ret_val = f"{self.response}()"
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
        else:
            resp.raise_for_status()
"""


def get_openapi_spec_url() -> str:
    assert len(sys.argv) == 2, "Expected a single argv arguments - the Argo OpenAPI spec URL"
    return sys.argv[1]


def get_openapi_spec(url: str) -> dict:
    response = requests.get(url)
    if response.ok:
        return response.json()
    raise ValueError(
        f"Did not receive an ok response from fetching the OpenAPI spec payload from url {url}, "
        f"status {response.status_code}"
    )


def get_consumes(payload: dict) -> str:
    consumes = payload.get("consumes")
    assert isinstance(consumes, list), f"Expected `consumes` to be of list type, received {type(consumes)}"
    assert len(consumes) == 1, "Expected `consumes` payload to contain a single item e.g. 'application/json'"
    return consumes[0]


def get_produces(payload: dict) -> str:
    produces = payload.get("produces")
    assert isinstance(produces, list), f"Expected `produces` to be of list type, received {type(produces)}"
    assert len(produces) == 1, "Expected `produces` payload to contain a single item e.g. 'application/json'"
    return produces[0]


def get_paths(payload: dict) -> dict:
    paths = payload.get("paths")
    assert isinstance(paths, dict), f"Expected `paths` to be of dictionary type, received {type(paths)}"
    return paths


def camel_to_snake(s: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", s)


def snake_to_camel(s: str) -> str:
    components = s.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def parse_operation_id(operation_id: str) -> str:
    if "UID" in operation_id:
        operation_id = operation_id.replace("UID", "Uid")
    operation = operation_id.split("_")[-1]
    operation_snake_case = camel_to_snake(operation).lower()
    return operation_snake_case.lower()


def get_workflow_class(cls_name: str) -> type:
    modules = inspect.getmembers(models)
    for module in modules:
        curr_cls = module[1]
        if inspect.isclass(curr_cls) and curr_cls.__name__ == cls_name:
            return curr_cls
    print(cls_name)


def parse_builtin(f: str) -> str:
    if f in dir(builtins) or f in ["continue", "pass", "in"]:
        return f"{f}_"
    return f


def parse_parameter(parameter: dict) -> Parameter:
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

    if "type" in parameter:
        type_ = openapi_type_switch.get(parameter.get("type"))
    elif "schema" in parameter:
        type_ = get_workflow_class(parameter.get("schema").get("$ref").split(".")[-1])
    else:
        raise ValueError(f"Unrecognized parameter type from parameter {parameter}")

    if name_ == "body":
        name_ = "req"
    if "TLS" in name_:
        name_ = name_.replace("TLS", "Tls")

    name_ = camel_to_snake(name_)
    name_ = parse_builtin(name_)
    name_ = name_.lower()
    return Parameter(name_, name, in_, type_, required)


def parse_response(parameter: dict) -> Response:
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
    paths: dict, consumes: str = "application/json", produces: str = "application/json"
) -> List[ServiceEndpoint]:
    endpoints = []
    for url, config in paths.items():
        for method, params in config.items():
            operation_id = parse_operation_id(params.get("operationId"))
            endpoint_params = []
            for parameter in params.get("parameters", []):
                endpoint_params.append(parse_parameter(parameter))
            response = parse_response(params)
            summary = params.get("summary")
            endpoints.append(
                ServiceEndpoint(
                    url, method, operation_id, endpoint_params, response, summary, consumes=consumes, produces=produces
                )
            )
    return endpoints


def get_service_def() -> str:
    return """
import requests
import os
from hera.models import *
from hera.new.config import GlobalConfig
from typing import Optional    

class Service:
    def __init__(
        self,
        host: Optional[str] = None,
        verify_ssl: bool = True,
        token: Optional[str] = None,
        namespace: Optional[str] = None,
    ):
        self.host = host or GlobalConfig.host
        self.verify_ssl = verify_ssl or GlobalConfig.verify_ssl
        self.token = token or GlobalConfig.token
        self.namespace = namespace or GlobalConfig.namespace
"""


def make_service(service_def: str, endpoints: List[ServiceEndpoint]) -> str:
    result = service_def
    for endpoint in endpoints:
        result = result + f"{endpoint}\n"
    return result


def write_service(service: str, path: Path) -> None:
    with open(str(path), "w+") as f:
        f.write(service)


def create_service() -> None:
    url = get_openapi_spec_url()
    payload = get_openapi_spec(url)
    consumes = get_consumes(payload)
    produces = get_produces(payload)
    paths = get_paths(payload)
    endpoints = get_endpoints(paths, consumes=consumes, produces=produces)
    service_def = get_service_def()
    result = make_service(service_def, endpoints)
    path = Path(__name__).parent / "src/hera/new/service.py"
    write_service(result, path)


if __name__ == "__main__":
    create_service()

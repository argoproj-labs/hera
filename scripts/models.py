"""This helps parse out the workflow models from the OpenAPI schema and creates an init only for those models"""

# we want the init of `workflows.models` to have a filtered import of Workflow models
# we can parse out the JSON using the old code and filter on Workflow objects
from datetime import datetime, timezone
import sys
import requests
from pathlib import Path

model_types = {'workflows', 'events'}


def get_openapi_spec_url() -> str:
    """Gets the OpenAPI spec URL from argv and returns it"""
    assert len(sys.argv) == 3, "Expected two argv arguments - the Argo OpenAPI spec URL and [workflows|events]"
    return sys.argv[1]


def get_models_type() -> str:
    """Gets the model type to generate from argv and returns it. This is either `workflows` or `events`"""
    assert len(sys.argv) == 3, "Expected two argv arguments - the Argo OpenAPI spec URL and [workflows|events]"
    arg = sys.argv[2]
    assert arg in model_types, f"Unsupported model type {arg}, expected one of {model_types}"
    return arg


def fetch_openapi_spec(url: str) -> dict:
    """Fetches the OpenAPI specification at the given URI"""
    response = requests.get(url)
    if response.ok:
        return response.json()
    raise ValueError(
        f"Did not receive an ok response from fetching the OpenAPI spec payload from url {url}, "
        f"status {response.status_code}"
    )


def get_openapi_definitions(spec: dict) -> dict:
    """Extracts the OpenAPI definitions from the given OpenAPI spec"""
    assert "definitions" in spec, "Expected `definitions` to be part of the spec"
    return spec['definitions']


def get_refs_from_openapi_definitions(defs: dict) -> list:
    """Extracts the OpenAPI references from the given OpenAPI definitions"""
    return list(defs.keys())


def filter_refs_on_models_type(refs: list, models_type: str) -> list:
    """Filters the given list of references using the given model type"""
    # TODO: maybe this logic can be a bit more sophisticated
    inclusions = ['events', 'event', 'eventsource', 'sensor']

    filtered = refs
    events = []
    for inclusion in inclusions:
        if models_type == 'events':
            for ref in refs:
                if inclusion in ref:
                    events.append(ref)
        else:
            exclusions = [
                'io.k8s.api.core.v1.Event',
                'io.k8s.api.core.v1.EventSeries',
                'io.k8s.api.core.v1.EventSource',
            ]
            filtered = list(filter(lambda r: inclusion not in r and r not in exclusions, filtered))
    if models_type == 'events':
        return list(set(events))
    return list(set(filtered))


def assemble_root_path_from_models_type(m_type: str) -> str:
    """Assembles the Hera root path from the given models type"""
    return f"hera.{m_type}.models"


def get_import_paths_from_refs(refs: list, root_path: str) -> list:
    """Assembles the Hera import paths from the given list of references"""
    result = []
    for ref in refs:
        split = ref.split(".")
        path, obj = '.'.join(split[:-1]), split[-1]
        # these are duplicate objects and cause collisions, so we use extra flags from the import path to denote
        # the differences between them, which helps users avoid import errors
        if obj in ['HTTPHeader', 'LogEntry']:
            alias = f'{split[-2]}{obj}'
            upper_alias = alias[0].upper() + alias[1:]
            obj = f'{obj} as {upper_alias}'

        result.append(f"from {root_path}.{path} import {obj}")
    return result


def write_imports(imports: list, models_type: str, openapi_spec_url: str) -> None:
    """Writes the given imports to the `root_path` models"""
    path = Path(__name__).parent.parent / 'src' / 'hera' / models_type / 'models' / '__init__.py'
    with open(str(path), 'w+') as f:
        now = datetime.now(timezone.utc)
        f.write(
            f'"""[DO NOT EDIT MANUALLY]\n\n'
            f'Auto-generated by Hera via `make {models_type}-models` on: {now}\n'
            f'OpenAPI spec URL: {openapi_spec_url}\n'
            f'"""\n\n'
        )
        for imp in imports:
            f.write(f"{imp}\n")


if __name__ == "__main__":
    models_type = get_models_type()
    openapi_spec_url = get_openapi_spec_url()
    openapi_spec = fetch_openapi_spec(openapi_spec_url)
    definitions = get_openapi_definitions(openapi_spec)
    refs = get_refs_from_openapi_definitions(definitions)
    filtered_refs = filter_refs_on_models_type(refs, models_type)
    root_path = assemble_root_path_from_models_type(models_type)
    imports = get_import_paths_from_refs(filtered_refs, root_path)
    write_imports(imports, models_type, openapi_spec_url)

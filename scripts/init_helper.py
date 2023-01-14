import inspect
import os
import pathlib
import sys

from hera import (
    _base_model,
    _context,
    _version,
    artifact,
    cron_workflow,
    dag,
    env,
    env_from,
    gc_strategy,
    global_config,
    models,
    operator,
    parameter,
    resources,
    retry_strategy,
    sequence,
    service,
    task,
    validators,
    volumes,
    workflow,
    workflow_status,
    workflow_template,
)

models_final_imports = []
models_members = set([m[0] for m in inspect.getmembers(models) if inspect.isclass(m[1])])
hera_modules = [
    gc_strategy,
    service,
    cron_workflow,
    task,
    _base_model,
    env,
    artifact,
    _version,
    retry_strategy,
    sequence,
    global_config,
    validators,
    workflow_status,
    dag,
    operator,
    volumes,
    _context,
    workflow_template,
    env_from,
    resources,
    workflow,
    parameter,
]
str_hera_modules = [
    "gc_strategy",
    "service",
    "cron_workflow",
    "task",
    "_base_model",
    "env",
    "artifact",
    "_version",
    "retry_strategy",
    "sequence",
    "global_config",
    "validators",
    "workflow_status",
    "dag",
    "operator",
    "volumes",
    "_context",
    "workflow_template",
    "env_from",
    "resources",
    "workflow",
    "parameter",
]
all_hera_modules = []
for hera_module in hera_modules:
    members = set(list(filter(lambda m: m[0] == "__all__", inspect.getmembers(hera_module)))[0][1])
    all_hera_modules.extend(members)
diff = models_members.difference(set(all_hera_modules))
models_final_imports.extend(list(diff))
with open(pathlib.Path(os.getcwd()) / "src" / "hera" / "__init__.py", "w+") as init_file:
    init_file.write("# [DO NOT EDIT] generated via `make init` on: 2023-01-14 17:13:49.818752\n")
    str_imports = ", ".join(models_final_imports)
    init_file.write(f"from hera.models import {str_imports}\n")
    for str_hera_module in str_hera_modules:
        init_file.write(f"from hera.{str_hera_module} import *\n")
    init_file.write("__version__ = version\n")
    init_file.write("__version_info__ = version.split('.')")

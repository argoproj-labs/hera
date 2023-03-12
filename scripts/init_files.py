import importlib
import pkgutil
from pathlib import Path

import hera.workflows as hera_workflows

workflow_modules = [
    name
    for _, name, _ in pkgutil.iter_modules(hera_workflows.__path__)
    if name != "models" and not name.startswith("_")
]

header = """
# [DO NOT EDIT MANUALLY]
# Auto-generated by Hera via `make init-files`
# In order to add objects to the hera.workflows namespace
# add them to the __all__ list in the relevant module.
"""

hera_workflows_init = Path(hera_workflows.__file__)

exports = []

outputs = [header]

for module_name in workflow_modules:
    module = importlib.import_module(f"hera.workflows.{module_name}")
    for export in getattr(module, "__all__", []):
        if export in exports:
            raise ValueError(f"Duplicate export {export}")
        exports.append(export)
        outputs.append(f"from hera.workflows.{module_name} import {export}")

outputs.append(f"__all__ = {repr(list(sorted(exports)))}")

hera_workflows_init.write_text("\n".join(outputs))

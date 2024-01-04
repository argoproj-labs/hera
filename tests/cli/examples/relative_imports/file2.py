from hera.workflows import Workflow

from .file1 import on_exit

with Workflow(name="relative_import", on_exit=on_exit) as workflow:
    workflow._add_sub(on_exit)

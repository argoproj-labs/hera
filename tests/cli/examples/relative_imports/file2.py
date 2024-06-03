from hera.workflows import Workflow

from .file1 import on_exit

workflow = Workflow(name="relative_import", on_exit=on_exit, templates=[on_exit])

"""Hera is a Python framework for constructing and submitting Argo Workflows.
The main goal of Hera is to make the Argo ecosystem accessible by simplifying
workflow construction and submission. Hera presents an intuitive Python interface
to the underlying API of Argo, with custom classes making use of context managers
and callables, empowering users to focus on their own executable payloads rather
than workflow setup.
"""

from hera._version import version

__version__ = version
__version_info__ = version.split(".")

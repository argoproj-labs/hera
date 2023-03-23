.. Hera documentation master file, created by
   sphinx-quickstart on Thu Oct 27 15:09:17 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Hera's documentation!
================================

Hera is a Python framework for constructing and submitting Argo Workflows. The main goal of Hera is to make the Argo ecosystem accessible by simplifying workflow construction and submission. Hera presents an intuitive Python interface to the underlying API of Argo, with custom classes making use of context managers and callables, empowering users to focus on their own executable payloads rather than workflow setup. Hera allows power users of Argo to use Python if preferred, by ensuring feature parity with Argo and a fallback option through an OpenAPI generated Python module found at `hera.workflows.models`.

.. toctree::
   :glob:
   :maxdepth: 2
   :caption: Hera Modules

   src/*

.. toctree::
   :caption: Expr Transpilation

   expr

.. toctree::
   :glob:
   :maxdepth: 2
   :caption: Hera Workflow Examples

   examples/workflows/*

.. toctree::
   :glob:
   :maxdepth: 2
   :caption: Hera - Argo Workflow Examples Replication

   examples/workflows/upstream/*

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

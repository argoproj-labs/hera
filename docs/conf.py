import os
import sys

sys.path.insert(0, os.path.abspath(".."))

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Hera"
copyright = "2023, Flaviu Vadan, Sambhav Kothari, Elliot Gunton"
author = "Flaviu Vadan, Sambhav Kothari, Elliot Gunton"
language = "en"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "myst_parser",
    "autoapi.extension",
]
master_doc = "index"

autoapi_type = "python"
autoapi_dirs = ["../src"]
autoapi_file_pattern = "*.py"
autoapi_python_use_implicit_namespaces = True
autoapi_add_toctree_entry = False

templates_path = ["_templates"]
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "conftest.py",
    "tests",
    "\.github",
]
numpydoc_show_inherited_class_members = True
numpydoc_show_class_members = False

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_book_theme"
html_static_path = ["_static"]

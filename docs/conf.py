import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath('..'))

root_path = Path(__file__).parent.parent

with open(root_path / 'pyproject.toml', 'r') as f:
    for line in f.readlines():
        if line.startswith('version'):
            release = line.strip().split(" ")[-1].replace("\"", "")
            version = ".".join(release.split(".")[:-1])
            break

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Hera'
copyright = '2022, Flaviu Vadan, Asgeir Berland'
author = 'Flaviu Vadan, Asgeir Berland'
language = 'en'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'myst_parser'
]
master_doc = 'index'

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', 'conftest.py', 'tests', '\.github']
numpydoc_show_inherited_class_members = True
numpydoc_show_class_members = False

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_book_theme'
html_static_path = ['_static']

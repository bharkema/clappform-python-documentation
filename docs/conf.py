"""Clappform documentation build configuration file."""
# pylint: disable=redefined-builtin,wrong-import-position
# flake8: noqa=E402
import os
import sys

sys.path.insert(0, os.path.abspath("../src"))
import clappform

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Clappform"
copyright = f"2022, {clappform.__author__}"
author = clappform.__author__
version = clappform.__version__
release = clappform.__version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc", "sphinx.ext.intersphinx"]
intersphinx_mapping = {"python": ("https://docs.python.org/3.10", None)}

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_static_path = ["_static"]

# -- Options for Autodoc output ----------------------------------------------
autodoc_member_order = "bysource"

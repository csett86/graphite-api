#!/usr/bin/env python3
# coding: utf-8

import os
import re
import sys

from sphinx.ext import autodoc

sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir))

# Read version from pyproject.toml (requires python 3.11+ for tomllib)
import tomllib

_pyproject_path = os.path.join(os.path.dirname(__file__), os.pardir, 'pyproject.toml')

with open(_pyproject_path, 'rb') as f:
    _version = tomllib.load(f)['project']['version']

extensions = [
    'sphinx.ext.autodoc',
]

# Mock imports for dependencies not needed for documentation
autodoc_mock_imports = [
    'cairocffi',
    'flask',
    'pyparsing',
    'structlog',
    'tzlocal',
    'werkzeug',
    'yaml',
    'packaging',
]

templates_path = ['_templates']

source_suffix = {
    '.rst': 'restructuredtext',
}

root_doc = 'index'

project = 'Graphite-Render'
copyright = u'2014, Bruno Renié'

version = _version
release = _version

exclude_patterns = ['_build']

pygments_style = 'sphinx'

html_theme = 'alabaster'

htmlhelp_basename = 'Graphite-Renderdoc'

latex_elements = {
}

latex_documents = [
    ('index', 'Graphite-Render.tex', 'Graphite-Render Documentation',
     'Bruno Renié', 'manual'),
]

man_pages = [
    ('index', 'graphite-render', 'Graphite-Render Documentation',
     ['Bruno Renié'], 1)
]

texinfo_documents = [
    ('index', 'Graphite-Render', 'Graphite-Render Documentation',
     'Bruno Renié', 'Graphite-Render', 'One line description of project.',
     'Miscellaneous'),
]


class RenderFunctionDocumenter(autodoc.FunctionDocumenter):
    priority = 10

    @classmethod
    def can_document_member(cls, member, membername, isattr, parent):
        return autodoc.FunctionDocumenter.can_document_member(
            member, membername, isattr, parent
        ) and parent.name == 'graphite_render.functions'

    def format_args(self):
        args = super(RenderFunctionDocumenter, self).format_args()
        if args is not None:
            return re.sub('requestContext, ', '', args)


suppress_warnings = ['app.add_directive', 'autodoc.import_object']


def setup(app):
    app.add_autodocumenter(RenderFunctionDocumenter)


add_module_names = False

# -*- coding: utf-8 -*-
#
# SimplePlugin documentation build configuration file, created by
# sphinx-quickstart on Sun Jan 17 20:39:22 2016.

import re
import sys
import os

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, os.path.join(basedir, 'script.module.simpleplugin3', 'libs'))
sys.path.insert(0, basedir)
import tests

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinx.ext.autosummary',
]

autodoc_member_order = 'bysource'
autodoc_default_flags = ['members', 'show-inheritance']
autosummary_generate = True

templates_path = ['_templates']

source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'SimplePlugin'
copyright = u'2016, Roman Miroshnychenko'
author = u'Roman Miroshnychenko'

with open(os.path.join(basedir, 'script.module.simpleplugin3', 'addon.xml'), 'rb') as addon_xml:
    version = re.search(r'(?<!xml )version="(.+?)"', addon_xml.read()).group(1)

release = version

language = None

exclude_patterns = ['_build']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

todo_include_todos = False

html_theme = 'alabaster'

html_theme_options = {
    'github_button': True,
    'github_type': 'star&v=2',  ## Use v2 button
    'github_user': 'romanvm',
    'github_repo': 'script.module.simpleplugin',
    'github_banner': True,
    'travis_button': True,
    'codecov_button': True,
    'description': 'A plugin micro-framework for Kodi mediacenter',
    'font_family': 'Georgia',
}

html_sidebars = {
    '**': [
        'about.html',
        'navigation.html',
        'searchbox.html',
    ]
}

html_static_path = ['_static']

html_show_sourcelink = True

html_show_sphinx = True

htmlhelp_basename = 'SimplePlugindoc'

latex_documents = [
    (master_doc, 'SimplePlugin.tex', u'SimplePlugin Documentation',
     u'Roman Miroshnychenko', 'manual'),
]

man_pages = [
    (master_doc, 'simpleplugin', u'SimplePlugin Documentation',
     [author], 1)
]

texinfo_documents = [
    (master_doc, 'SimplePlugin', u'SimplePlugin Documentation',
     author, 'SimplePlugin', 'One line description of project.',
     'Miscellaneous'),
]

intersphinx_mapping = {'https://docs.python.org/2.7': None,
                       'http://romanvm.github.io/Kodistubs/': None}

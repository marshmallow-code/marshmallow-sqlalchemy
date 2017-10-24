# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime as dt
import os
import sys

import alabaster
try:
    from marshmallow.compat import OrderedDict
except ImportError:
    from collections import OrderedDict
sys.path.insert(0, os.path.abspath('..'))
import marshmallow_sqlalchemy  # noqa

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinx_issues',
]

primary_domain = 'py'
default_role = 'py:obj'

intersphinx_mapping = {
    'python': ('https://python.readthedocs.io/en/latest/', None),
    'marshmallow': ('https://marshmallow.readthedocs.io/en/latest/', None),
    'sqlalchemy': ('http://www.sqlalchemy.org/docs/', None),
}

issues_github_path = 'marshmallow-code/marshmallow-sqlalchemy'

source_suffix = '.rst'
master_doc = 'index'
project = 'marshmallow-sqlalchemy'
copyright = 'Steven Loria, Joshua Carp, and contributors {0:%Y}'.format(dt.datetime.utcnow())

version = release = marshmallow_sqlalchemy.__version__

exclude_patterns = ['_build']

html_theme_path = [alabaster.get_path()]
html_theme = 'alabaster'
html_static_path = ['_static']
templates_path = ['_templates']
html_show_sourcelink = False

html_theme_options = {
    'logo': 'marshmallow-sqlalchemy-logo.png',
    'description': 'SQLAlchemy integration with the marshmallow (de)serialization library',
    'description_font_style': 'italic',
    'github_user': 'marshmallow-code',
    'github_repo': 'marshmallow-sqlalchemy',
    'github_banner': True,
    'github_button': False,
    'code_font_size': '0.85em',
    'warn_bg': '#FFC',
    'warn_border': '#EEE',
    # Used to populate the useful-links.html template
    'extra_nav_links': OrderedDict([
        ('marshmallow-sqlalchemy @ PyPI',
            'http://pypi.python.org/pypi/marshmallow-sqlalchemy'),
        ('marshmallow-sqlalchemy @ GitHub',
            'http://github.com/marshmallow-code/marshmallow-sqlalchemy'),
        ('Issue Tracker',
            'http://github.com/marshmallow-code/marshmallow-sqlalchemy/issues'),
    ])
}

html_sidebars = {
    'index': [
        'about.html', 'useful-links.html', 'searchbox.html'
    ],
    '**': ['about.html', 'useful-links.html',
           'localtoc.html', 'relations.html', 'searchbox.html']
}

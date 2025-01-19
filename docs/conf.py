import importlib.metadata

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autodoc.typehints",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx_issues",
    "sphinxext.opengraph",
]

primary_domain = "py"
default_role = "py:obj"

intersphinx_mapping = {
    "python": ("https://python.readthedocs.io/en/latest/", None),
    "marshmallow": ("https://marshmallow.readthedocs.io/en/latest/", None),
    "sqlalchemy": ("http://www.sqlalchemy.org/docs/", None),
}

issues_github_path = "marshmallow-code/marshmallow-sqlalchemy"

source_suffix = ".rst"
master_doc = "index"

project = "marshmallow-sqlalchemy"
copyright = "Steven Loria and contributors"  # noqa: A001

version = release = importlib.metadata.version("marshmallow-sqlalchemy")

exclude_patterns = ["_build"]

# THEME

html_theme = "furo"
html_logo = "_static/marshmallow-sqlalchemy-logo.png"
html_theme_options = {
    "source_repository": "https://github.com/marshmallow-code/marshmallow-sqlalchemy",
    "source_branch": "dev",
    "source_directory": "docs/",
    "sidebar_hide_name": True,
    "light_css_variables": {
        # Serif system font stack: https://systemfontstack.com/
        "font-stack": "Iowan Old Style, Apple Garamond, Baskerville, Times New Roman, Droid Serif, Times, Source Serif Pro, serif, Apple Color Emoji, Segoe UI Emoji, Segoe UI Symbol;",
    },
    "top_of_page_buttons": ["view"],
}
pygments_dark_style = "lightbulb"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_show_sourcelink = False
ogp_image = "_static/marshmallow-sqlalchemy-logo.png"

# Strip the dollar prompt when copying code
# https://sphinx-copybutton.readthedocs.io/en/latest/use.html#strip-and-configure-input-prompts-for-code-cells
copybutton_prompt_text = "$ "

autodoc_typehints = "description"
autodoc_member_order = "bysource"

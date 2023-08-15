"""Configure Sphinx documentation builder."""

import datetime
import inspect
import os
import sys

import predictably

# -- Project information ---------------------------------------------------
current_year = datetime.datetime.now().year
if current_year > 2023:
    current_year = f"2023-{current_year}"

org = "predict-ably"
project = "predictably"
copyright = "{current_year}, {org} developers (BSD-3 License)"
author = "predict-ably developers"

release = predictably.__version__

version = predictably.__version__
github_tag = f"v{version}"

# -- Path setup --------------------------------------------------------------

# When we build the docs on readthedocs, we build the package and want to
# use the built files in order for sphinx to be able to properly read the
# Cython files. Hence, we do not add the source code path to the system path.
env_rtd = os.environ.get("READTHEDOCS")
# Check if on Read the docs
if not env_rtd == "True":
    print("Not on ReadTheDocs")
    sys.path.insert(0, os.path.abspath("../.."))
else:
    rtd_version = os.environ.get("READTHEDOCS_VERSION")
    if rtd_version == "latest":
        github_tag = "main"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.linkcode",  # link to GitHub source code via linkcode_resolve()
    "myst_parser",
    "numpydoc",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx_issues",
]

myst_enable_extensions = ["colon_fence"]
myst_heading_anchors = 2

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "**.ipynb_checkpoints"]

# -- Internationalization ------------------------------------------------
# specifying the natural language populates some key tags
language = "en"

# Use bootstrap CSS from theme.
panels_add_bootstrap_css = False

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# The main toctree document.
master_doc = "index"

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# Members and inherited-members default to showing methods and attributes from
# a class or those inherited.
# Member-order orders the documentation in the order of how the members are
# defined in the source code.
autodoc_default_options = {
    "members": True,
    "inherited-members": True,
    "member-order": "bysource",
}

# generate autosummary even if no references
autosummary_generate = True

# If true, '()' will be appended to :func: etc. cross-reference text.
add_function_parentheses = False

# Link to GitHub repo for github_issues extension
issues_github_path = f"{org}/{project}"


def linkcode_resolve(domain, info):
    """Return URL to source code corresponding.

    Parameters
    ----------
    domain : str
    info : dict

    Returns
    -------
    url : str
    """

    def find_source():
        # try to find the file and line number, based on code from numpy:
        # https://github.com/numpy/numpy/blob/main/doc/source/conf.py#L286
        obj = sys.modules[info["module"]]
        for part in info["fullname"].split("."):
            obj = getattr(obj, part)

        fn = inspect.getsourcefile(obj)
        fn = os.path.relpath(fn, start=os.path.dirname(predictably.__file__))
        source, lineno = inspect.getsourcelines(obj)
        return fn, lineno, lineno + len(source) - 1

    if domain != "py" or not info["module"]:
        return None
    try:
        filename = "{project}/%s#L%d-L%d" % find_source()
    except Exception:
        filename = info["module"].replace(".", "/") + ".py"
    return f"https://github.com/{org}/{project}/blob/{version_match}/{filename}"


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"

# Define the json_url for our version switcher.
json_url = "https://predictably.readthedocs.io/en/latest/_static/switcher.json"

# This uses code from the py-data-sphinx theme's own conf.py
# Define the version we use for matching in the version switcher.
version_match = os.environ.get("READTHEDOCS_VERSION")

# If READTHEDOCS_VERSION doesn't exist, we're not on RTD
# If it is an integer, we're in a PR build and the version isn't correct.
if not version_match or version_match.isdigit():
    # For local development, infer the version to match from the package.
    if "dev" in release or "rc" in release:
        version_match = "latest"
        # We want to keep the relative reference if we are in dev mode
        # but we want the whole url if we are effectively in a released version
        json_url = "_static/switcher.json"
    else:
        version_match = "v" + release

html_theme_options = {
    "logo": {
        "text": "predictably",
        "alt_text": "predictably",
    },
    "icon_links": [
        {
            "name": "GitHub",
            "url": f"https://github.com/{org}/{project}",
            "icon": "fab fa-github",
        },
        {
            "name": "Slack",
            "url": f"https://join.slack.com/t/{org}/shared_invite/zt-21ezi33ip-WGJCUBCWc5yVrr6FOsARaw",  # noqa: E501
            "icon": "fab fa-slack",
        },
        {
            "name": "PyPI",
            "url": f"https://pypi.org/project/{project}",
            "icon": "fa-solid fa-box",
        },
    ],
    "icon_links_label": "Quick Links",
    "show_nav_level": 1,
    "show_prev_next": False,
    "use_edit_page_button": False,
    "navbar_start": ["navbar-logo", "version-switcher"],
    "navbar_center": ["navbar-nav"],
    "switcher": {
        "json_url": json_url,
        "version_match": version_match,
    },
    "header_links_before_dropdown": 6,
}

html_context = {
    "github_user": f"{org}",
    "github_repo": f"{project}",
    "github_version": "main",
    "doc_path": "docs/source/",
    "default_mode": "light",
}
html_sidebars = {"**": ["sidebar-nav-bs.html", "sidebar-ethical-ads.html"]}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# -- Options for HTMLHelp output ---------------------------------------------
# Output file base name for HTML help builder.
htmlhelp_basename = "predictablydoc"


# -- Options for LaTeX output ------------------------------------------------
latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    # 'papersize': 'letterpaper',
    # The font size ('10pt', '11pt' or '12pt').
    # 'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    # 'preamble': '',
    # Latex figure (float) alignment
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (
        master_doc,
        "predictably.tex",
        "predictably Documentation",
        "predict-ably developers",
        "manual",
    ),
]

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        master_doc,
        "predictably",
        "predictably Documentation",
        author,
        "predictably",
        "Cross-language timeseries forecasting.",
        "Miscellaneous",
    ),
]

# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(master_doc, "predictably", "predictably Documentation", [author], 1)]

# -- Extension configuration -------------------------------------------------
# -- Options for numpydoc extension ------------------------------------------
# see http://stackoverflow.com/q/12206334/562769
numpydoc_show_class_members = True
# this is needed for some reason...
# see https://github.com/numpy/numpydoc/issues/69
numpydoc_class_members_toctree = False

numpydoc_validation_checks = {"all", "GL01", "SA01", "EX01"}

# -- Options for sphinx-copybutton extension----------------------------------
copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True

# -- Options for intersphinx extension ---------------------------------------

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    "python": (f"https://docs.python.org/{sys.version_info.major}", None),
    "numpy": ("https://docs.scipy.org/doc/numpy/", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/reference", None),
    "pandas": ("https://pandas.pydata.org/pandas-docs/stable/", None),
    "scikit-learn": ("https://scikit-learn.org/stable/", None),
    "sktime": ("https://www.sktime.net/en/stable/", None),
}

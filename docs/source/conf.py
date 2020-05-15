# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import sphinx_gallery
from sphinx_gallery.sorting import ExplicitOrder
import os
import sys
sys.path.insert(0, os.path.abspath('.'))

# -- Project information -----------------------------------------------------

project = 'mplsoccer'
copyright = '2020, Andrew Rowlinson'
author = 'Andrew Rowlinson'

# The full version, including alpha/beta/rc tags
release = '0.0.4'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.autosummary',
              'sphinx.ext.imgmath',
              'sphinx.ext.viewcode',
              'sphinx_gallery.gen_gallery',
              'sphinx.ext.napoleon',
              'numpydoc']


# this is needed for some reason...
# see https://github.com/numpy/numpydoc/issues/69
numpydoc_class_members_toctree = False

napoleon_google_docstring = False
napoleon_use_param = False
napoleon_use_ivar = True

# generate autosummary even if no references
autosummary_generate = True
# order api docs by order they appear in the code
autodoc_member_order = 'bysource'

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build']

# sphinx gallery
sphinx_gallery_conf = {
    'examples_dirs': ['../../examples'],
    'gallery_dirs': ['gallery'],
    'subsection_order': ExplicitOrder(['../../examples/plots',
                                       '../../examples/statsbomb',
                                       '../../examples/pitch_setup',])}


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

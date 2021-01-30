import os, sys
sys.path.insert(0, os.path.abspath('..'))

import artiruno
release = artiruno.__version__

extensions = [
     'sphinx.ext.autodoc',
     'sphinx.ext.intersphinx']

exclude_patterns = ['_build']

smartquotes = False
nitpicky = True

intersphinx_mapping = dict(
    py = ('https://docs.python.org/3/', None),
    py2 = ('https://docs.python.org/2/', None),
    graphviz = ('https://graphviz.readthedocs.io/en/stable', None))

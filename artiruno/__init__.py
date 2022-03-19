# Ensure that each module can accessed explicitly as `m`; e.g.,
# `artiruno.m.vda` will get the `vda` module. This is useful because
# `artiruno.vda` will be set to a function instead of the module.
import artiruno.util, artiruno.preorder, artiruno.vda, artiruno.interactive
class C: pass
m = C()
for s in ('util', 'preorder', 'vda', 'interactive'):
    setattr(m, s, getattr(artiruno, s))

# Only import `artiruno.web` on Pyodide, since its own imports will
# fail on CPython.
import platform
if platform.system() == 'Emscripten':
   from artiruno.web import initialize_web_interface

# Now do the ordinary imports.
from artiruno._version import __version__
from artiruno.util import *
from artiruno.preorder import (
    PreorderedSet, Relation, IC, EQ, LT, GT, ContradictionError)
from artiruno.vda import vda, avda

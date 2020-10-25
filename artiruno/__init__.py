# Ensure that each module can accessed explicitly as `m`; e.g.,
# `artiruno.m.vda` will get the `vda` module. This is useful because
# `artiruno.vda` will be set to a function instead of the module.
import importlib
class C: pass
m = C()
for s in ('util', 'preorder', 'vda', 'interactive'):
    setattr(m, s, importlib.import_module('artiruno.' + s))

# Now do the ordinary imports.
from artiruno.util import *
from artiruno.preorder import (
    PreorderedSet, IC, EQ, LT, GT, ContradictionError)
from artiruno.vda import vda

# Ensure that each module can accessed explicitly as `m`; e.g.,
# `artiruno.m.vda` will get the `vda` module. This is useful because
# `artiruno.vda` will be set to a function instead of the module.
import artiruno.preorder, artiruno.vda, artiruno.util
class C: pass
m = C()
for s in ('preorder', 'vda', 'util'):
    setattr(m, s, getattr(artiruno, s))

# Now do the ordinary imports.
from artiruno.preorder import (
    PreorderedSet, IC, EQ, LT, GT, ContradictionError)
from artiruno.vda import vda, Goal
from artiruno.util import *

"Partly known totally preordered sets."

import itertools
from artiruno.util import choose2

UN, LT, EQ, GT = None, -1, 0, 1

def invert_rel(rel):
    return (
        LT if rel == GT else
        GT if rel == LT else
        rel)

def simprel(a, b, rel):
    # Re-express GT relations as LT.
    return (b, a, LT) if rel == GT else (a, b, rel)

class ContradictionError(Exception):
    def __init__(self, k, was, claimed):
        super().__init__("{}: known to be {}, now claimed to be {}".format(k, was, claimed))

class PKTPS:
    "Partly known totally preordered set."

    def __init__(self, elements, relations = None):
        self.elements = frozenset(elements)
        self.relations = relations or {(a, b): UN
            for a, b in choose2(sorted(self.elements))}

    def copy(self):
        return type(self)(self.elements, self.relations.copy())

    def cmp(self, a, b):
        if a == b:
            assert a in self.elements
            return EQ
        k = (a, b) if a <= b else (b, a)
        return self.relations[k] if a <= b else invert_rel(self.relations[k])

    def extrema(self, among = None, mins = False):
        return frozenset(x
            for x in among or self.elements
            if all(
                self.cmp(x, a) in (LT if mins else GT, EQ)
                for a in among or self.elements))

    def maxes(self, among = None):
        return self.extrema(among, mins = False)
    def mins(self, among = None):
        return self.extrema(among, mins = True)

    def set(self, a, b, rel):
      # Returns true if a change was made.
        assert rel != UN

        if a == b:
             assert a in self.elements
             if rel != EQ:
                 raise ContradictionError(k, EQ, rel)
             return False

        k = (a, b)
        if b < a:
           k, rel = (b, a), invert_rel(rel)

        if self.relations[k] == UN:
            self.relations[k] = rel
            return True
        elif self.relations[k] == rel:
            return False
        else:
            raise ContradictionError(k, self.relations[k], rel)

    def learn(self, a, b, rel):
        if changed := self.set(a, b, rel):
            self._update()
        return changed

    def get_subset(self, elements):
        elements = frozenset(elements)
        assert elements.issubset(self.elements)
        return type(self)(elements, {(a, b): r
            for (a, b), r in self.relations.items()
            if {a, b}.issubset(elements)})

    def _update(self):
        # Expand the known relations into their transitive closure.
        changed = True
        while changed:
            changed = False
            for (a, b, r1), (c, d, r2) in choose2(
                    simprel(a, b, r)
                    for (a, b), r in self.relations.items()
                    if r != UN):
                if r1 == r2 == LT:
                    if b == c or a == d:
                        changed = changed or self.set(
                            a if b == c else c,
                            d if b == c else b,
                            LT)
                elif {a, b} & {c, d}:
                    if r1 != EQ:
                        ((a, b), r1), ((c, d), r2) = ((c, d), r2), ((a, b), r1)
                    changed = changed or self.set(
                        b if c == a else a if c == b else c,
                        b if d == a else a if d == b else d,
                        r2)

    def _summary(self):
        return " ".join(
            "{}{}{}".format(a, {EQ: "=", LT: "<"}[rel], b)
            for a, b, rel in sorted(
                simprel(a, b, rel)
                for (a, b), rel in self.relations.items()
                if rel != UN))

    def graph(self):
        import subprocess
        import graphviz

        g = graphviz.Digraph()

        # Collect groups of equivalent items into nodes.
        nodes = []
        for a in sorted(self.elements):
            for node in nodes:
                if self.cmp(a, node[0]) == EQ:
                    node.append(a)
                    break
            else:
                nodes.append([a])

        # Add the nodes to the graph.
        def node_repr(node):
            return " / ".join(map(str, sorted(node)))
        for node in nodes:
            g.node(node_repr(node))

        # Add edges.
        for a, b in itertools.product(nodes, nodes):
            if self.cmp(a[0], b[0]) == LT:
                g.edge(node_repr(b), node_repr(a))

        # Render to Graphviz source code, transform to the transitive
        # reduction with `tred`, and redigest the graph.
        return graphviz.Source(subprocess
            .Popen(["tred"], stdin = subprocess.PIPE, stdout = subprocess.PIPE)
            .communicate(g.source.encode('UTF-8'))[0].decode('UTF-8'))

    def render(self, *args, **kwargs):
        return self.graph().render(*args, **kwargs)

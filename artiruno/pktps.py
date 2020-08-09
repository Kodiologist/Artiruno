"Partly known totally preordered sets."

import itertools
from artiruno.util import choose2

UN, LT, EQ, GT = None, -1, 0, 1

def invert_rel(rel):
    return (
        LT if rel == GT else
        GT if rel == LT else
        rel)

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
        return self.relations[a, b] if a < b else invert_rel(self.relations[b, a])

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

    def _set(self, a, b, rel):
      # Returns true if a change was made.
        assert rel in (LT, EQ, GT)

        if a == b:
             assert a in self.elements
             if rel != EQ:
                 raise ContradictionError((a, b), EQ, rel)
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
        if not self._set(a, b, rel):
            return False
        # Use a modification of Warshall's algorithm to update the transitive
        # closure.
        # https://web.archive.org/web/2013/https://cs.winona.edu/lin/cs440/ch08-2.pdf
        for k, i, j in itertools.product((a, b), self.elements, self.elements):
            r1, r2 = self.cmp(i, k), self.cmp(k, j)
            if (r1 != UN and r2 == EQ) or (r1 == LT == r2):
                self._set(i, j, r1)
        return True

    def get_subset(self, elements):
        elements = frozenset(elements)
        assert elements.issubset(self.elements)
        return type(self)(elements, {(a, b): r
            for (a, b), r in self.relations.items()
            if {a, b}.issubset(elements)})

    def _summary(self):
        return " ".join(
            "{}{}{}".format(a, {EQ: "=", LT: "<"}[rel], b)
            for a, b, rel in sorted(
                (b, a, LT) if rel == GT else (a, b, rel)
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

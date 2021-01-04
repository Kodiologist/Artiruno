import itertools
from collections import Counter
from artiruno.util import choose2

IC, LT, EQ, GT = None, -1, 0, 1
  # The types of relations: incomparable, less than, equivalent, greater than

def invert_rel(rel):
    return (
        LT if rel == GT else
        GT if rel == LT else
        rel)

class ContradictionError(Exception):
    def __init__(self, k, was, claimed):
        super().__init__("{}: known to be {}, now claimed to be {}".format(k, was, claimed))

class PreorderedSet:
    '''A set equipped with a preorder. Elements can be added to
    the set, and the order can be updated to make previously
    incomparable elements comparable.'''

    def __init__(self, elements = (), relations = (), raw_relations = None):
        self.elements = set(elements)
        self.relations = raw_relations or {(a, b): IC
            for a, b in choose2(sorted(self.elements))}
        for a, b, rel in relations:
            self.learn(a, b, rel)

    def copy(self):
        return type(self)(self.elements.copy(),
            raw_relations = self.relations.copy())

    def add(self, x):
        if x in self.elements:
            return
        for a in self.elements:
            self.relations[(a, x) if a < x else (x, a)] = IC
        self.elements.add(x)

    def cmp(self, a, b):
        if a == b:
            assert a in self.elements and b in self.elements
            return EQ
        return self.relations[a, b] if a < b else invert_rel(self.relations[b, a])

    def extreme(self, n, among = None, bottom = False):
        rel = GT if bottom else LT
          # Work around https://github.com/brython-dev/brython/issues/1535
        return frozenset(x
            for x in among or self.elements
            for cmps in [Counter(
                self.cmp(x, a) for a in among or self.elements)]
            if cmps[IC] == 0 and cmps[rel] < n)

    def maxes(self, among = None):
        return self.extreme(1, among, bottom = False)
    def mins(self, among = None):
        return self.extreme(1, among, bottom = True)

    def _set(self, a, b, rel):
        'Return true if a change was made.'
        assert rel in (LT, EQ, GT)

        if a == b:
             assert a in self.elements
             if rel != EQ:
                 raise ContradictionError((a, b), EQ, rel)
             return False

        k = (a, b)
        if b < a:
           k, rel = (b, a), invert_rel(rel)

        if self.relations[k] == IC:
            self.relations[k] = rel
            return True
        elif self.relations[k] == rel:
            return False
        else:
            raise ContradictionError(k, self.relations[k], rel)

    def learn(self, a, b, rel):
        '''Update the ordering. Return a list of pairs that were updated.
        Raise ContradictionError if the new assertion isn't consistent
        with the preexisting non-IC relations.'''
        if not self._set(a, b, rel):
            return []
        # Use a modification of Warshall's algorithm to update the transitive
        # closure.
        # https://web.archive.org/web/2013/https://cs.winona.edu/lin/cs440/ch08-2.pdf
        changed = [(a, b) if a < b else (b, a)]
        for k, i, j in itertools.product((a, b), self.elements, self.elements):
            r1, r2 = self.cmp(i, k), self.cmp(k, j)
            if (r1 != IC and r2 == EQ) or (r1 == LT == r2):
                if self._set(i, j, r1):
                    changed.append((i, j) if i < j else (j, i))
        return changed

    def get_subset(self, elements):
        elements = frozenset(elements)
        assert elements.issubset(self.elements)
        return type(self)(elements, raw_relations = {(a, b): r
            for (a, b), r in self.relations.items()
            if {a, b}.issubset(elements)})

    def _summary(self):
        return " ".join(
            "{}{}{}".format(a, {EQ: "=", LT: "<"}[rel], b)
            for a, b, rel in sorted(
                (b, a, LT) if rel == GT else (a, b, rel)
                for (a, b), rel in self.relations.items()
                if rel != IC))

    def graph(self, namer = str):
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
            return " / ".join(map(namer, sorted(node)))
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

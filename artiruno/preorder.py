import itertools, enum
from collections import Counter
from artiruno.util import cmp, choose2

class Relation(enum.Enum):
    'An :class:`enum.Enum` representing the order relation between two objects.'

    IC = None  #: Incomparable (true relation not yet known)
    LT = -1    #: Less than
    EQ = 0     #: Equal or equivalent to
    GT = 1     #: Greater than

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    def __bool__(self):
        ':const:`LT` and :const:`GT` are true. :const:`IC` and :const:`EQ` are false.'
        return bool(self.value)

    def __neg__(self):
        'Swap :const:`LT` and :const:`GT`. Return :const:`IC` or :const:`EQ` unchanged.'
        return (
            LT if self == GT else
            GT if self == LT else
            self)

    @classmethod
    def cmp(cls, a, b):
        "Return the :class:`Relation` between ``a`` and ``b`` corresponding to Python's built-in comparison operators."
        return cls(cmp(a, b))

IC, LT, EQ, GT = Relation.IC, Relation.LT, Relation.EQ, Relation.GT

class ContradictionError(Exception):
    'Represents an attempt to build an inconsistent order.'
    def __init__(self, k, was, claimed):
        super().__init__('{}: known to be {}, now claimed to be {}'.format(k, was, claimed))

class PreorderedSet:
    '''A set equipped with a `preorder <https://en.wikipedia.org/wiki/Preorder>`_. Elements can be added to the set, and the order can be updated to make previously incomparable elements comparable.

    :param elements: An iterable of hashable objects to be ordered.
    :param relations: An iterable of triples ``(a, b, rel)``, where ``a`` and ``b`` are objects in ``elements``, and ``rel`` is a :class:`Relation`. By default, all elements are incomparable to each other.
    :param raw_relations: Used internally.'''

    def __init__(self, elements = (), relations = (), raw_relations = None):
        self.elements = set(elements)
        self.relations = raw_relations or {(a, b): IC
            for a, b in choose2(sorted(self.elements))}
        for a, b, rel in relations:
            self.learn(a, b, rel)

    def __repr__(self):
        return f'PreorderedSet({self.elements!r}, {self.relations!r})'

    def copy(self):
        'Return a copy of the object.'
        return type(self)(self.elements.copy(),
            raw_relations = self.relations.copy())

    def add(self, x):
        "Add ``x`` to the set; a no-op if it's already there. ``x`` is initially incomparable to all other elements."
        if x in self.elements:
            return
        for a in self.elements:
            self.relations[(a, x) if a < x else (x, a)] = IC
        self.elements.add(x)

    def cmp(self, a, b):
        'Return the :class:`Relation` between ``a`` and ``b``.'
        if a == b:
            assert a in self.elements and b in self.elements
            return EQ
        return self.relations[a, b] if a < b else -self.relations[b, a]

    def extreme(self, n, among = None, bottom = False):
        '''Return the top-``n`` subset (or bottom-``n`` subset, if ``bottom`` is true) of the items in the set ``among``, or of the whole set if ``among`` is not provided.

        We define the *top-n subset* of a preordered set ``S`` to be the set of all elements ``x ∈ S`` such that

        - ``x`` is comparable to all elements of ``S``, and
        - there are at most ``n - 1`` distinct elements ``a ∈ S`` such that ``a > x``.

        We define the bottom-``n`` subset similarly, with the inequality in the other direction. Notice that the top-``n`` subset may contain more or less than ``n`` items.'''

        return frozenset(x
            for x in among or self.elements
            for cmps in [Counter(
                self.cmp(x, a) for a in among or self.elements)]
            if cmps[IC] == 0 and cmps[GT if bottom else LT] < n)

    def maxes(self, among = None):
        'Return all the maxima among the items in ``among``, or the whole set if ``among`` is not provided. The maxima are defined as the top-1 subset, per :meth:`extreme`.'
        return self.extreme(1, among, bottom = False)
    def mins(self, among = None):
        'As ``maxes``, but for minima.'
        return self.extreme(1, among, bottom = True)

    def _set(self, a, b, rel):
        # Return true if a change was made.
        assert rel in (LT, EQ, GT)

        if a == b:
             assert a in self.elements
             if rel != EQ:
                 raise ContradictionError((a, b), EQ, rel)
             return False

        k = (a, b)
        if b < a:
           k, rel = (b, a), -rel

        if self.relations[k] == IC:
            self.relations[k] = rel
            return True
        elif self.relations[k] == rel:
            return False
        else:
            raise ContradictionError(k, self.relations[k], rel)

    def learn(self, a, b, rel):
        '''Update the ordering such that ``a`` and ``b`` are related by ``rel``, a :class:`Relation` other than :const:`IC <Relation.IC>`. Any other relations that can be inferred by transitivity will be added to the set.

        Return a list of pairs that were actually updated. If the relation between ``a`` and ``b`` was already known, the list will be empty. If we made inferences for other pairs, these pairs will be included in the list.

        Raise :class:`ContradictionError` if the new relation isn't consistent with the preexisting relations (other than incomparability).'''

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
        'Return a new :class:`PreorderedSet` that contains only the requested ``elements``.'

        elements = frozenset(elements)
        assert elements.issubset(self.elements)
        return type(self)(elements, raw_relations = {(a, b): r
            for (a, b), r in self.relations.items()
            if {a, b}.issubset(elements)})

    def summary(self, namer = str):
        'Describe all the relations with a string like "A<B C<D E=F". ``namer`` should be a callback that returns a name for an element, as a string.'
        return ' '.join(
            '{}{}{}'.format(
                namer(a), {EQ: '=', LT: '<'}[rel], namer(b))
            for a, b, rel in sorted(
                (b, a, LT) if rel == GT else (a, b, rel)
                for (a, b), rel in self.relations.items()
                if rel != IC))

    def graph(self, namer = str):
        'Return the set represented as a :class:`graphviz.Source` object. Requires the Python package ``graphviz``. ``namer`` should be a callback that returns a name for an element, as a string.'

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
            return ' / '.join(map(namer, sorted(node)))
        for node in nodes:
            g.node(node_repr(node))

        # Add edges.
        for a, b in itertools.product(nodes, nodes):
            if self.cmp(a[0], b[0]) == LT:
                g.edge(node_repr(b), node_repr(a))

        # Render to Graphviz source code, transform to the transitive
        # reduction with `tred`, and redigest the graph.
        return graphviz.Source(subprocess
            .Popen(['tred'], stdin = subprocess.PIPE, stdout = subprocess.PIPE)
            .communicate(g.source.encode('UTF-8'))[0].decode('UTF-8'))

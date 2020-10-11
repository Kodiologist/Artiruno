import itertools, functools, math, enum
from artiruno.preorder import PreorderedSet, IC, LT, EQ, GT
from artiruno.util import cmp, choose2

Goal = enum.Enum('Goal', 'FIND_BEST RANK_ALTS RANK_SPACE')

class Jump(Exception):
    def __init__(self, value):
        self.value = value

def vda(criteria, alts = (), asker = None, goal = Goal.FIND_BEST, max_dev = 2):
    """
- `criteria` is an iterable of iterables specifying the levels of
  each criterion. Within a criterion, we assume that later levels are
  better.
- `alts` is a list of the alternatives, each represented
  as a tuple of the criteria.
- `asker` should be a callable object f(a, b) that returns
    GT (1) if a is better
    LT (-1) if b is better
    0 (EQ) if they're equally good
- `max_dev` sets the maximum number of criteria on which hypothetical
  items can deviate from the reference item when asking the user to
  make choices. It's summed across both items; e.g., `max_dev == 5`
  allows 4 deviant criteria compared to 1 deviant criterion."""

    criteria, alts, prefs = _setup(criteria, alts, goal)
    assert 2 <= max_dev <= 2*len(criteria)

    def get_pref(a, b):
        add_items(criteria, prefs, [a, b])
        if (rel := prefs.cmp(a, b)) is None:
            prefs.learn(a, b, rel := asker(a, b))
        return rel

    def dev_from_ref(dev_criteria, vector):
        '''Return a vector in the item space that deviates from the
        best possible item on the given criteria with the given
        values.'''
        return tuple(
           vector[i] if i in dev_criteria else c[-1]
           for i, c in enumerate(criteria))

    def num_item(item):
        '''Represent criterion values as integers. This prevents us
        from behaving differently depending on the default sort order
        of the criterion values. (We're still sensitive to the order
        of criteria, though.)'''
        return tuple(criteria[i].index(v) for i, v in enumerate(item))

    for allowed_pairs in itertools.accumulate(
           [(big, small), (small, big)]
           for deviation in range(1, max_dev)
           for big in range(deviation, deviation // 2, -1)
           for small in [deviation + 1 - big]
           if small <= len(criteria)):

        to_try = set(choose2(sorted(alts, key = num_item)))

        while True:

            if goal == Goal.FIND_BEST and len(prefs.maxes(alts)):
                return prefs

            # Don't ask about pairs we already know.
            to_try = {x for x in to_try if prefs.cmp(*x) == IC}

            if goal == Goal.FIND_BEST:
                # Don't compare alternatives that can't be the best.
                not_best = {x
                    for x in alts
                    if any(prefs.cmp(x, a) == LT for a in alts)}
                to_try = {(a, b)
                    for a, b in to_try
                    if a not in not_best and b not in not_best}

            if not to_try:
                if any(prefs.cmp(a, b) == IC for a, b in choose2(alts)):
                    break
                return prefs

            a, b = max(to_try, key = lambda pair:
                (num_item(pair[0]), num_item(pair[1])))
            to_try.remove((a, b))

            cs = frozenset({ci
                for ci in range(len(criteria))
                if a[ci] != b[ci]})
            try:
                def f(rel, cs1, cs2):
                    if not cs1:
                        raise Jump(rel)
                    for size1, size2 in allowed_pairs[
                            # In the topmost call of `f`, force use of the
                            # new allowed_pairs, to save pointless iterations.
                            -2 if len(cs1) == len(criteria) else 0:]:
                        if (len(cs1) - size1 < 0 or len(cs2) - size2 < 0 or
                                (len(cs1) - size1 == 0) != (len(cs2) - size2 == 0)):
                            continue
                        for c1 in itertools.combinations(sorted(cs1), size1):
                            for c2 in itertools.combinations(sorted(cs2), size2):
                                p = get_pref(dev_from_ref(c1, a), dev_from_ref(c2, b))
                                if rel == EQ or p in (EQ, rel):
                                    f(rel or p, cs1.difference(c1), cs2.difference(c2))
                f(EQ, cs, cs)
            except Jump as j:
                prefs.learn(a, b, j.value)

    return prefs

def _setup(criteria, alts = (), goal = Goal.FIND_BEST):
    "Some initial VDA logic put into its own function so it can be tested separately."

    assert isinstance(goal, Goal)

    criteria = tuple(map(tuple, criteria))
    assert len(criteria)
    assert all(
        len(c) > 0 and len(c) == len(set(c))
        for c in criteria)

    if goal == Goal.RANK_SPACE:
        alts = tuple(itertools.product(*criteria))
    else:
        alts = tuple(map(tuple, alts))
        assert all(
            len(a) == len(criteria) and all(
                a[i] in criteria[i]
                for i in range(len(a)))
            for a in alts)
        assert len(alts) == len(set(alts))

    # Define the user's preferences as a preorder, with `a < b` if `b`
    # is preferred to `a`, and `a` and `b` incomparable if the user's
    # preference isn't yet known.
    prefs = PreorderedSet()
    add_items(criteria, prefs, alts)

    return criteria, alts, prefs

def add_items(criteria, prefs, items):
    # Enforce the assumption that on any single criterion, bigger
    # values are better.
    for x in set(items) - prefs.elements:
        prefs.add(x)
        for a in prefs.elements - {x}:
            cmps = [
                cmp(criteria[ci].index(x[ci]),
                    criteria[ci].index(a[ci]))
                for ci in range(len(criteria))]
            if not (LT in cmps and GT in cmps):
                # One item dominates the other. (We know that `cmps`
                # isn't all EQ because `x` and `a` are different.)
                prefs.learn(x, a, LT if LT in cmps else GT)

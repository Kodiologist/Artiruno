import itertools, math, enum
from artiruno.pktps import PKTPS, UN, LT, EQ, GT
from artiruno.util import cmp, choose2

Goal = enum.Enum('Goal', 'FIND_BEST RANK_ALTS RANK_SPACE')

def vda(criteria, alts, asker, goal):
    """
- `criteria` is an iterable of iterables specifying the levels of
  each criterion. With a criterion, we assume that later levels are
  better.
- `alts` is a list of the alternatives, each represented
  as a tuple of the criteria.
- `asker` should be a callable object f(a, b) that returns
    GT (1) if a is better
    LT (-1) if b is better
    0 (EQ) if they're equally good"""

    assert isinstance(goal, Goal)
    criteria = tuple(map(tuple, criteria))
    assert all(
        len(c) > 0 and len(c) == len(set(c))
        for c in criteria)
    alts = tuple(map(tuple, alts))
    assert all(
        len(a) == len(criteria) and all(
            a[i] in criteria[i]
            for i in range(len(a)))
        for a in alts)

    def dev_from_ref(criterion, value):
      # Return a vector in the item space that deviates from the best
      # possible item on the given criterion with the given value.
        return tuple(
           value if i == criterion else c[-1]
           for i, c in enumerate(criteria))

    # Define the user's preferences as a PKTPS, with `a < b` if `b` is
    # preferred to `a`. We initialize it with the assumption that on
    # any single criterion, bigger values are better.
    item_space = tuple(itertools.product(*criteria))
    prefs = PKTPS(item_space)
    for a, b in choose2(item_space):
        if sum(l := [x != y for x, y in zip(a, b)]) == 1:
            ci = l.index(True)
            prefs.learn(a, b, cmp(
                criteria[ci].index(a[ci]),
                criteria[ci].index(b[ci])))

    def get_pref(a, b):
        if (rel := prefs.cmp(a, b)) is not None:
            return rel
        rel = asker(a, b)
        assert rel in (LT, EQ, GT)
        prefs.learn(a, b, rel)
        return rel

    to_try = set(choose2(
        item_space if goal == Goal.RANK_SPACE else alts))
    focus = None

    while not (goal == Goal.FIND_BEST and len(prefs.maxes(alts)) == 1):

        # Don't ask about pairs we already know.
        to_try = {x for x in to_try if prefs.cmp(*x) == UN}

        if goal == Goal.FIND_BEST:
            # Don't compare alternatives that can't be the best.
            not_best = {x
                for x in alts
                if any(prefs.cmp(x, a) == LT for a in alts)}
            to_try = {(a, b)
                for a, b in to_try
                if a not in not_best and b not in not_best}

        if not to_try:
            break

        a, b = max(to_try, key = lambda pair: (focus in pair, pair))
        to_try.remove((a, b))

        result = {}
        for v1, v2 in ((a, b), (b, a)):
            # Implement a strict version of the "rule of comparison"
            # from Larichev and Moshkovieh (1995), p. 506:
            #   For any vectors yi, yj,
            #   if for each component yik of yi,
            #     there exists yjp ∈ yj with yjp ≯ yik, (i.e., yjp ≤ yik)
            #   then yi ≮ yj (i.e., yj ≤ yi)
            ps = [
                max(get_pref(dev_from_ref(c1, v1[c1]), dev_from_ref(c2, v2[c2]))
                    for c2 in range(len(criteria)))
                for c1 in range(len(criteria))]
            result[v1, v2] = all(p in (EQ, GT) for p in ps) and GT in ps
        if sum(result.values()) == 1:
            prefs.learn(a, b, GT if result[a, b] else LT)

        if goal == Goal.FIND_BEST:
            focus = (
                a if prefs.cmp(a, b) == GT else
                b if prefs.cmp(a, b) == LT else
                focus)

    return prefs

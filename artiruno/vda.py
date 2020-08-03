import itertools, math, enum
from artiruno.pktps import PKTPS, UN, LT, EQ, GT
from artiruno.util import cmp, choose2

Goal = enum.Enum('Goal', 'FIND_BEST RANK_ALTS RANK_SPACE')

def vda(criteria, alts, asker, goal):
    """
- `criteria` specifies how many levels each criterion has.
  We assume that higher levels are better, and represent each
  as an integer, starting from 0.
- `alts` is a list of the alternatives, each represented
  as a tuple of the criteria.
- `asker` should be a callable object f(a, b) that returns
    GT (1) if a is better
    LT (-1) if b is better
    0 (EQ) if they're equally good"""

    assert isinstance(goal, Goal)
    assert all(
        type(n) is int and n >= 0
        for n in criteria)
    assert all(
        len(a) == len(criteria) and all(
            type(a[i]) is int and 0 <= a[i] < criteria[i]
            for i in range(len(a)))
        for a in alts)

    def dev_from_ref(criterion, value):
      # Return a vector in the item space that deviates from the best
      # possible item on the given criterion with the given value.
        return tuple(
           value if i == criterion else n - 1
           for i, n in enumerate(criteria))

    # Define the user's preferences as a PKTPS, with a < b if `b` is
    # preferred to `a`. We initialize it with the assumption that on
    # any single criterion, bigger values are better.
    item_space = list(itertools.product(*(range(n) for n in criteria)))
    prefs = PKTPS(item_space)
    for a, b in choose2(item_space):
        if sum(x != y for x, y in zip(a, b)) == 1:
            prefs.learn(a, b, cmp(a, b))

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

    while to_try and (goal != Goal.FIND_BEST or len(prefs.maxes(alts)) != 1):
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
                b if prefs.cmp(a, b) == -1 else
                a if prefs.cmp(a, b) == 1 else
                focus)

    return prefs

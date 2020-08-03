import itertools
from artiruno.pktps import UN, LT, EQ, GT
from artiruno.vda import vda, Goal
from artiruno.util import cmp, choose2

def test_appendixD():
    # Appendix D of Larichev and Moshkovich (1995).

    criteria = [3, 3, 3]
    alts = [(1,2,3), (2,3,1), (3,1,2)]
    dm_ranking = [(2,1,1), (1,1,2), (1,2,1), (1,3,1), (3,1,1), (1,1,3)]
    def dm_asker(a, b):
        assert {a, b}.issubset(dm_ranking)
        return cmp(dm_ranking.index(a), dm_ranking.index(b))

    # Translate to 0-based, greater-is-better.
    alts = [tuple(3 - n for n in v) for v in alts]
    dm_ranking = [tuple(3 - n for n in v) for v in reversed(dm_ranking)]

    Proposal1, Proposal2, Proposal3 = alts

    for goal in (Goal.FIND_BEST, Goal.RANK_ALTS, Goal.RANK_SPACE):
        prefs = vda(
            criteria = criteria,
            alts = alts,
            asker = dm_asker,
            goal = goal)
        assert prefs.maxes(among = alts) == {Proposal2}
        if goal == Goal.RANK_SPACE:
            for v1, v2 in choose2(dm_ranking):
                assert prefs.cmp(v1, v2) == cmp(
                    dm_ranking.index(v1), dm_ranking.index(v2))
        if goal != Goal.FIND_BEST:
            assert prefs.cmp(Proposal2, Proposal1) == GT
            assert prefs.cmp(Proposal2, Proposal3) == GT
            assert prefs.cmp(Proposal3, Proposal1) == GT

def test_lexicographic():

    criteria = [3, 3, 3]
    alts = [
      # I think I got these items from a paper, but now I've forgotten
      # which. D'oh.
        (0, 1, 1),
        (1, 1, 0),
        (2, 0, 1),
        (0, 2, 0),
        (1, 0, 2),
        (2, 1, 1),
        (2, 1, 0),
        (2, 2, 0),
        (1, 0, 1)]

    def p(a): return vda(
        criteria = criteria,
        alts = alts,
        asker = a,
        goal = Goal.FIND_BEST)

    prefs = p(lambda a, b: cmp(a[::-1], b[::-1]))
    assert prefs.maxes() == {(2, 2, 2)}
    assert prefs.maxes(among = alts) == {(1, 0, 2)}

    prefs = p(lambda a, b: cmp(a, b))
    assert prefs.maxes() == {(2, 2, 2)}
    assert prefs.maxes(among = alts) == {(2, 2, 0)}

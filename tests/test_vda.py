import itertools
import artiruno
from artiruno import IC, LT, EQ, GT, vda, Goal, cmp, choose2

def test_assumptions():
    # Test the preferences that we should assume purely from the
    # criteria definitions, without having asked the user anything
    # yet.

    *_, prefs = artiruno.m.vda._setup(
        criteria = ['abcd', ('bad', 'okay', 'good')],
        goal = Goal.RANK_SPACE)

    assert prefs.cmp(('a', 'bad'), ('c', 'bad')) == LT
    assert prefs.cmp(('a', 'okay'), ('a', 'good')) == LT
    assert prefs.cmp(('d', 'good'), ('a', 'bad')) == GT
    assert prefs.cmp(('c', 'okay'), ('b', 'bad')) == GT
    assert prefs.cmp(('b', 'good'), ('c', 'okay')) == IC

def test_appendixD():
    # Appendix D of Larichev and Moshkovich (1995).

    criteria = [(3,2,1)] * 3
    alts = [(1,2,3), (2,3,1), (3,1,2)]
    dm_ranking = [(2,1,1), (1,1,2), (1,2,1), (1,3,1), (3,1,1), (1,1,3)]
    def dm_asker(a, b):
        assert {a, b}.issubset(dm_ranking)
        return -cmp(dm_ranking.index(a), dm_ranking.index(b))

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
                assert prefs.cmp(v1, v2) == -cmp(
                    dm_ranking.index(v1), dm_ranking.index(v2))
        if goal != Goal.FIND_BEST:
            assert prefs.cmp(Proposal2, Proposal1) == GT
            assert prefs.cmp(Proposal2, Proposal3) == GT
            assert prefs.cmp(Proposal3, Proposal1) == GT

def test_lexicographic():

    criteria = [(0, 1, 2)] * 3
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

def test_simple_strings():

    criteria = [['bad', 'good'], ['expensive', 'cheap']]
    alts = [
        ('bad', 'cheap'), ('good', 'expensive'),
        ('bad', 'expensive')]

    def asker(a, b):
       # We prefer good to bad, but when that criterion is the same,
       # we prefer cheap to expensive.
        if a[0] == b[0]:
            if a[1] == b[1]:
                return EQ
            elif a[1] == 'cheap':
                return GT
            else:
                return LT
        elif a[0] == 'good':
            return GT
        else:
            return LT

    for goal in (Goal.FIND_BEST, Goal.RANK_SPACE):
        prefs = vda(
            criteria = criteria,
            alts = alts,
            asker = asker,
            goal = goal)
        assert prefs.maxes(among = alts) == {('good', 'expensive')}
        if goal == Goal.RANK_SPACE:
            assert prefs.maxes() == {('good', 'cheap')}
            ranking = (
                ('bad', 'expensive'), ('bad', 'cheap'),
                ('good', 'expensive'), ('good', 'cheap'))
            for (ai, a), (bi, b) in choose2(enumerate(ranking)):
                assert prefs.cmp(a, b) == cmp(ai, bi)

def test_big_item_space():
    n_criteria = 10
    n_levels = 20

    criteria = [list(range(n_levels))] * n_criteria
    alts = [[n_levels - 1] * n_criteria for _ in range(2)]
    alts[0][3] = 15
    alts[0][6] = 14
    alts[1][7] = 8
    alts[1][9] = 4

    prefs = vda(
        criteria = criteria,
        alts = alts,
        asker = cmp,
        goal = Goal.FIND_BEST)
    assert prefs.cmp(tuple(alts[0]), tuple(alts[1])) == LT

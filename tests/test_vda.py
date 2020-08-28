import random, itertools
from collections import Counter
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

    *_, prefs = artiruno.m.vda._setup(
        criteria = [range(3) for _ in range(3)],
        alts = ((1, 1, 1), (2, 1, 2)))
    assert prefs.cmp((1, 1, 1), (2, 1, 2)) == LT

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

def all_choice_seqs(choices, criteria, alts):

    alts = tuple(map(tuple, alts))
    queue = [(c,) for c in choices]
    result = []

    def asker(a, b):
        result[-1]['questions'].append((a, b))
        i = len(result[-1]['questions']) - 1
        if i == len(queue[0]):
            for c in choices[1:]:
                queue.append(queue[0] + (c,))
            queue[0] += (choices[0],)
        return queue[0][i]

    while queue:
        result.append(dict(questions = []))
        prefs = vda(
            criteria = criteria,
            alts = alts,
            asker = asker,
            goal = Goal.FIND_BEST)
        result[-1]['choices'] = queue[0]
        result[-1]['prefs'] = prefs
        result[-1]['maxes'] = prefs.maxes(alts)
        queue.pop(0)

    return result

def test_conclusivity(diag):
    # Look at what Artiruno concludes (i.e., the obtained maximum from
    # Goal.FIND_BEST) from every possible sequence of LT and GT
    # choices, given a fixed set of criteria and alternatives

    result = all_choice_seqs(
        choices = (LT, GT),
        # These criteria and alternatives are from Ashikhmin and
        # Furems (2005).
        criteria = (
            (1700, 1550, 1450, 1300),
            ('DVO', 'SVO-2'),
            ('0000', '0800', '1435', '1100')),
        alts = (
            (1550, 'SVO-2', '0800'),
            (1450, 'SVO-2', '1435'),
            (1300, 'DVO', '0000'),
            (1700, 'DVO', '1100')))

    # Every sequence of LT or GT choices should lead to a single best
    # item.
    assert all(len(r['maxes']) == 1 for r in result)

    # If changes to Artiruno result in having to ask less questions,
    # change this test. Having to ask more questions is a regression.
    assert (Counter(len(r['questions']) for r in result) ==
        Counter({4: 6, 3: 3, 2: 1}))

    if diag:
        print('Maxima:', Counter(r['maxes'] for r in result))

def test_recode_criteria():
    # Renaming criterion values shouldn't change the questions asked
    # or the results.

    criteria = tuple(
        tuple('abc'[i] + str(j) for j in range(3)) for i in range(3))
    alts = (
        ('a2', 'b2', 'c0'),
        ('a2', 'b0', 'c1'),
        ('a1', 'b0', 'c2'),
        ('a0', 'b2', 'c1'))

    r1 = all_choice_seqs((LT, EQ, GT), criteria, alts)

    crev = tuple(c[::-1] for c in criteria)
    def revitem(item):
        return tuple(crev[c][criteria[c].index(v)] for c, v in enumerate(item))
    r2 = all_choice_seqs((LT, EQ, GT), crev, tuple(map(revitem, alts)))

    assert len(r1) == len(r2)
    for d1, d2 in zip(r1, r2):
        assert d2['questions'] == [(revitem(a), revitem(b))
            for a, b in d1['questions']]
        assert d2['maxes'] == set(map(revitem, d1['maxes']))

def test_irrelevant_criteria():
    for d in all_choice_seqs(
            (LT, EQ, GT),
            criteria = ('ab', 'pq', 'xy'),
            alts = ('aqx', 'apy')):
        if set(map(tuple, ('aqx', 'apy', 'bqx', 'bpy'))) <= d['prefs'].elements:
            cmps = [
               d['prefs'].cmp(tuple(a), tuple(b))
               for a, b in (('aqx', 'apy'), ('bqx', 'bpy'))]
            assert cmps[0] == cmps[1]

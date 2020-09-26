import random, itertools
from collections import Counter
import artiruno
from artiruno import IC, LT, EQ, GT, vda, Goal, cmp, choose2
import pytest

def test_assumptions():
    '''Test the preferences that we should assume purely from the
    criteria definitions, without having asked the user anything
    yet.'''

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
    '''Appendix D of Larichev and Moshkovich (1995).'''

    criteria = [(3,2,1)] * 3
      # 3 is worst and 1 is best.
    alts = [(1,2,3), (2,3,1), (3,1,2)]
    dm_ranking = [(2,1,1), (1,1,2), (1,2,1), (1,3,1), (3,1,1), (1,1,3)]
      # The first element is the best, so we negate `cmp` in the
      # asker.
    def asker(a, b):
        return -cmp(dm_ranking.index(a), dm_ranking.index(b))

    Proposal1, Proposal2, Proposal3 = alts

    for goal in (Goal.FIND_BEST, Goal.RANK_ALTS, Goal.RANK_SPACE):
        prefs = vda(
            criteria = criteria,
            alts = alts,
            asker = asker,
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

def asker_stub(a, b):
    raise ValueError

def test_one_criterion():
    '''When there's only one criterion, we should never need to ask
    questions, because the rule of dominance suffices to infer all
    preferences.'''

    for criterion_length in range(2, 10):
        prefs = artiruno.vda(
           criteria = [tuple(range(criterion_length))],
           asker = asker_stub,
           goal = Goal.RANK_SPACE)
        for i, j in choose2(range(criterion_length)):
            assert prefs.cmp((i,), (j,)) == LT

def test_dominant_maximum():
    '''Under Goal.FIND_BEST, if there's an alternative that dominates
    all the others, we shouldn't need to ask any questions.'''

    criteria = tuple(tuple(range(5)) for _ in range(4))
    alts = [
        (2, 3, 1, 4),
        (2, 1, 3, 3),
        (2, 4, 1, 3),
        (3, 0, 2, 3),
        (4, 4, 3, 4)]
    prefs = artiruno.vda(criteria, alts, asker_stub, Goal.FIND_BEST)
    assert prefs.maxes(among = alts) == {(4, 4, 3, 4)}

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

def all_choice_seqs(
        criteria, alts = (), goal = Goal.FIND_BEST,
        max_dev = 2):

    choices = (LT, EQ, GT)
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
            goal = goal,
            max_dev = max_dev)
        result[-1]['choices'] = queue[0]
        result[-1]['prefs'] = prefs
        result[-1]['maxes'] = prefs.maxes(alts)
        queue.pop(0)

    return result

def test_recode_criteria():

    criteria = tuple(
        tuple('abc'[i] + str(j) for j in range(3)) for i in range(3))
    alts = (
        ('a2', 'b2', 'c0'),
        ('a2', 'b0', 'c1'),
        ('a1', 'b0', 'c2'),
        ('a0', 'b2', 'c1'))

    r1 = all_choice_seqs(criteria, alts, max_dev = 5)

    # Renaming criterion values shouldn't change the questions asked
    # or the results.
    crev = tuple(c[::-1] for c in criteria)
    def revitem(item):
        return tuple(crev[c][criteria[c].index(v)] for c, v in enumerate(item))
    r2 = all_choice_seqs(
        criteria = crev,
        alts = tuple(map(revitem, alts)),
        max_dev = 5)

    assert len(r1) == len(r2)
    for d1, d2 in zip(r1, r2):
        assert d2['questions'] == [(revitem(a), revitem(b))
            for a, b in d1['questions']]
        assert d2['maxes'] == set(map(revitem, d1['maxes']))

    # Similarly for adding a criterion on which all alternatives
    # are the same.
    def addc(item):
        return item + ('d1',)
    r3 = all_choice_seqs(
        criteria = criteria + (('d0', 'd1', 'd2'),),
        alts = map(addc, alts),
        max_dev = 5)

    assert len(r1) == len(r3)
    for d1, d3 in zip(r1, r3):
        assert d3['questions'] == [(a + ('d2',), b + ('d2',))
            for a, b in d1['questions']]
        assert d1['choices'] == d3['choices']
        assert d3['maxes'] == set(map(addc, d1['maxes']))

@pytest.mark.slow
def test_irrelevant_criteria():
    for d in all_choice_seqs(
            criteria = ('abc', 'pqr', 'xyz'),
            goal = Goal.RANK_SPACE):
        def p(a, b):
            return d['prefs'].cmp(tuple(a), tuple(b))
        assert p('aqx', 'apy') == p('bqx', 'bpy') == p('cqx', 'cpy')

def test_lex_small():
    'A scenario with lexicographic preferences.'
    criteria = [(0, 1)] * 3
    alts = [(1, 0, 0), (0, 1, 1)]
    prefs = vda(
        criteria = criteria, alts = alts,
        asker = cmp,
        goal = Goal.RANK_SPACE,
        max_dev = 3)
    assert prefs.cmp(*alts) == cmp(*alts)

def test_lex_big():

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
        goal = Goal.FIND_BEST,
        max_dev = 3)

    prefs = p(lambda a, b: cmp(a[::-1], b[::-1]))
    assert prefs.maxes() == {(2, 2, 2)}
    assert prefs.maxes(among = alts) == {(1, 0, 2)}

    prefs = p(lambda a, b: cmp(a, b))
    assert prefs.maxes() == {(2, 2, 2)}
    assert prefs.maxes(among = alts) == {(2, 2, 0)}

@pytest.mark.parametrize('criteria',
    [(2,2), (3,4), (5,5), (2,2,2), (3,2,2), (3,3,3), (2,) * 5, (5,) * 5])
def test_lex_generalized(criteria, run_slow_tests):
    '''Randomly generate alternatives and an underlying ranking for
    the criteria. Check that the concluded preferences equal the
    underlying preferences.'''

    if len(criteria) > 3 and not run_slow_tests:
        pytest.skip()

    R = random.Random(criteria)
    criteria = tuple(tuple(range(n)) for n in criteria)
    item_space = tuple(itertools.product(*criteria))

    criterion_order = []
    def asker(a, b):
        return cmp(*(
            tuple(v[i] for i in criterion_order)
            for v in (a, b)))

    for trial in range(20):
        alts = R.sample(item_space,
            min(len(item_space), R.randint(2, 8)))
        criterion_order = R.sample(range(len(criteria)), len(criteria))
        goal = R.choice([Goal.FIND_BEST, Goal.RANK_ALTS])
        prefs = vda(
            criteria, alts, asker, goal, max_dev = 2*len(criteria) + 1)
        if goal == Goal.FIND_BEST:
            assert prefs.maxes(among = alts) == {
                a
                for a in alts
                if all(prefs.cmp(a, b) in (GT, EQ) for b in alts)}
        else:
            for a, b in choose2(alts):
                assert prefs.cmp(a, b) == asker(a, b)

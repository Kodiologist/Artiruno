import random, itertools, inspect, asyncio
from collections import Counter
import artiruno
from artiruno import Relation, IC, LT, EQ, GT, vda, avda, cmp, choose2
import pytest

def test_assumptions():
    '''Test the preferences that we should assume purely from the
    criteria definitions, without having asked the user anything
    yet.'''

    *_, prefs = artiruno.m.vda._setup(
        criteria = ['abcd', ('bad', 'okay', 'good')])
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
        return -Relation.cmp(dm_ranking.index(a), dm_ranking.index(b))

    Proposal1, Proposal2, Proposal3 = alts

    for goal in ('find_best', 'rank_alts', 'rank_space'):
        prefs = vda(
            criteria = criteria,
            alts = (None if goal == 'rank_alts' else alts),
            asker = asker,
            find_best = goal == 'find_best' and 1)
        assert prefs.maxes(among = alts) == {Proposal2}
        if goal == 'rank_alts':
            for v1, v2 in choose2(dm_ranking):
                assert prefs.cmp(v1, v2) == -Relation.cmp(
                    dm_ranking.index(v1), dm_ranking.index(v2))
        if goal != 'find_best':
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

    for find_best in (1, 2, None):
        prefs = vda(
            criteria = criteria,
            alts = alts if find_best else None,
            asker = asker,
            find_best = find_best)
        assert prefs.maxes(among = alts) == {('good', 'expensive')}
        if find_best == 2:
            assert prefs.extreme(2, among = alts) == {
                ('good', 'expensive'), ('bad', 'cheap')}
        elif not find_best:
            assert prefs.maxes() == {('good', 'cheap')}
            ranking = (
                ('bad', 'expensive'), ('bad', 'cheap'),
                ('good', 'expensive'), ('good', 'cheap'))
            for (ai, a), (bi, b) in choose2(enumerate(ranking)):
                assert prefs.cmp(a, b) == Relation.cmp(ai, bi)

async def test_async():
    criteria = ((0, 1), (0, 1))
    alts = ((0, 1), (1, 0))
    l = []

    async def f():
        queue = asyncio.Queue()
        async def asker(a, b):
            l.append('start')
            queue.put_nowait(1)
            await queue.join()
            l.append('done')
            return Relation.cmp(a, b)
        async def other():
            await queue.get()
            l.append('in other')
            queue.task_done()
        return (await asyncio.gather(
            other(),
            avda(
                criteria = criteria,
                alts = alts,
                asker = asker,
                find_best = 1)))[1]

    assert (await f()).maxes(alts) == {(1, 0)}
    assert l == ['start', 'in other', 'done']

def asker_stub(a, b):
    raise ValueError

def test_one_criterion():
    '''When there's only one criterion, we should never need to ask
    questions, because the rule of dominance suffices to infer all
    preferences.'''

    for criterion_length in range(2, 10):
        prefs = artiruno.vda(
           criteria = [tuple(range(criterion_length))],
           asker = asker_stub)
        for i, j in choose2(range(criterion_length)):
            assert prefs.cmp((i,), (j,)) == LT

def test_dominant_maximum():
    '''Under `find_best = 1`, if there's an alternative that dominates
    all the others, we shouldn't need to ask any questions.'''

    criteria = tuple(tuple(range(5)) for _ in range(4))
    alts = [
        (2, 3, 1, 4),
        (2, 1, 3, 3),
        (2, 4, 1, 3),
        (3, 0, 2, 3),
        (4, 4, 3, 4)]
    prefs = artiruno.vda(criteria, alts, asker_stub, find_best = 1)
    assert prefs.maxes(among = alts) == {(4, 4, 3, 4)}

def test_big_item_space():
    n_criteria = 10
    n_levels = 20

    criteria = [list(range(n_levels))] * n_criteria
    alts = [[17] * n_criteria for _ in range(2)]
    alts[0][3] = 15
    alts[0][6] = 14
    alts[1][7] = 8
    alts[1][9] = 4

    prefs = vda(
        criteria = criteria,
        alts = alts,
        asker = Relation.cmp,
        find_best = True,
        max_dev = 3)
    assert prefs.cmp(tuple(alts[0]), tuple(alts[1])) == LT

def all_choice_seqs(
        criteria, alts = None, find_best = 1,
        max_dev = 2):

    choices = (LT, EQ, GT)
    if alts:
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
            find_best = find_best,
            max_dev = max_dev)
        result[-1]['choices'] = queue[0]
        result[-1]['prefs'] = prefs
        result[-1]['maxes'] = prefs.maxes(alts)
        queue.pop(0)

    return result

@pytest.mark.slow
def test_recode_criteria():
    '''Renaming criterion values shouldn't change the questions asked
    or the results.'''

    criteria = tuple(
        tuple('abc'[i] + str(j) for j in range(3)) for i in range(3))
    alts = (
        ('a2', 'b2', 'c0'),
        ('a2', 'b0', 'c2'),
        ('a1', 'b2', 'c1'),
        ('a0', 'b1', 'c2'))

    r1 = all_choice_seqs(criteria, alts, max_dev = 5)

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

@pytest.mark.slow
def test_irrelevant_criteria():
    for d in all_choice_seqs(
            criteria = ('abc', 'pqr', 'xyz'),
            find_best = None):
        def p(a, b):
            return d['prefs'].cmp(tuple(a), tuple(b))
        assert p('aqx', 'apy') == p('bqx', 'bpy') == p('cqx', 'cpy')

def test_lex_small():
    'A scenario with lexicographic preferences.'
    criteria = [(0, 1)] * 3
    alts = [(1, 0, 0), (0, 1, 1)]
    prefs = vda(
        criteria = criteria, alts = alts,
        asker = Relation.cmp,
        max_dev = 3)
    assert prefs.cmp(*alts) == Relation.cmp(*alts)

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

    def p(find_best, max_dev, a): return vda(
        criteria = criteria,
        alts = alts,
        asker = a,
        find_best = find_best,
        max_dev = max_dev)

    prefs = p(1, 3, lambda a, b: Relation.cmp(a[::-1], b[::-1]))
    assert prefs.maxes() == {(2, 2, 2)}
    assert prefs.maxes(among = alts) == {(1, 0, 2)}

    prefs = p(1, 3, lambda a, b: Relation.cmp(a, b))
    assert prefs.maxes() == {(2, 2, 2)}
    assert prefs.maxes(among = alts) == {(2, 2, 0)}

    prefs = p(3, 4, lambda a, b: Relation.cmp(a, b))
    assert prefs.extreme(3, among = alts) == {
        (2, 2, 0), (2, 1, 1), (2, 1, 0)}

def random_scenarios(f):
    '''For each of several trials, randomly generate alternatives, and
    call `f` to randomly generate an asker. Check that the preferences
    Artiruno concludes are consistent with the asker.'''

    trials = 20
    criteria_fast = [(2,2), (3,4), (5,5), (2,2,2), (3,2,2), (3,3,3)]
    criteria_slow = [(2,) * 5, (5,) * 5]
    criteria_all = criteria_fast + criteria_slow

    @pytest.mark.parametrize('criteria', criteria_all)
    def out(criteria, run_slow_tests):
        if criteria in criteria_slow and not run_slow_tests:
            pytest.skip()

        questions_asked = 0
        expect_questions_asked = (
            inspect.signature(f).parameters['n_questions'].default)[
                criteria_all.index(criteria)]

        criteria = tuple(tuple(range(n)) for n in criteria)
        item_space = tuple(itertools.product(*criteria))

        for trial in range(trials):
            R = random.Random(repr((criteria, trial)))
            alts = R.sample(item_space,
                min(len(item_space), R.randint(2, 8)))
            find_best = R.choice([True, None])
            if find_best is True:
                find_best = R.choice(
                    [i for i in [1, 2, 3] if i < len(alts)])
            asker = f(criteria, R)
            def counting_asker(a, b):
                nonlocal questions_asked
                questions_asked += 1
                return asker(a, b)
            prefs = vda(
                criteria, alts, counting_asker, find_best,
                max_dev = 2*len(criteria))
            if find_best:
                assert prefs.extreme(find_best, among = alts) == {
                    a
                    for a in alts
                    for cmps in [Counter(asker(a, b) for b in alts)]
                    if cmps[IC] == 0 and cmps[LT] < find_best}
            else:
                for a, b in choose2(alts):
                    assert prefs.cmp(a, b) == asker(a, b)

        assert questions_asked == expect_questions_asked
           # If questions_asked < expect_questions_asked, that's an
           # improvement, so update expect_questions_asked.
           # If questions_asked > expect_questions_asked, that's a
           # regression, so fix it.

    return out

@random_scenarios
def test_lex_generalized(criteria, R,
        n_questions = (15, 39, 54, 34, 47, 80, 105, 642)):
    '''Artiruno should be able to reproduce lexicographic preferences,
    in which the criteria have a defined order of importance.'''
    criterion_order = R.sample(range(len(criteria)), len(criteria))
    return lambda a, b: Relation.cmp(*(
        tuple(v[i] for i in criterion_order)
        for v in (a, b)))

@random_scenarios
def test_value_function(criteria, R,
        n_questions = (15, 50, 53, 35, 43, 94, 72, 905)):
    '''Artiruno should be able to reproduce preferences defined by an
    additive value function, in which each criterion increment adds a
    certain positive amount of utility.'''
    values = tuple(
       tuple(0 if i == 0 else R.randint(1, 4)
           for i in range(len(c)))
       for c in criteria)
    return lambda a, b: Relation.cmp(*(
       sum(sum(values[ci][: cl + 1])
           for ci, cl in enumerate(item))
       for item in (a, b)))

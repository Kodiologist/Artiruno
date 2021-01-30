import itertools

def cmp(a, b):
    "As Python 2's :func:`py2:cmp`."
    return (a > b) - (a < b)

def choose2(x):
    'Shortcut for ``itertools.combinations(x, 2)``.'
    return itertools.combinations(x, 2)

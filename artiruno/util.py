import itertools

def cmp(a, b):
    # As Python 2: https://docs.python.org/2/library/functions.html#cmp
    return (a > b) - (a < b)

def choose2(x):
    return itertools.combinations(x, 2)

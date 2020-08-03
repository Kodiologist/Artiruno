from artiruno.pktps import PKTPS, UN, LT, EQ, GT, ContradictionError
import pytest

def test_simple():
    x = PKTPS(range(2))
    assert x._summary() == ""
    x.learn(0, 1, LT)
    assert x._summary() == "0<1"
    with pytest.raises(ContradictionError):
        x.learn(1, 0, LT)

    x = PKTPS(range(2))
    x.learn(1, 0, EQ)
    assert x._summary() == "0=1"

def test_trans():
    x = PKTPS("abc")

    x.learn("a", "b", LT)
    x.learn("c", "b", GT)
    assert x._summary() == "a<b a<c b<c"

def test_long_trans():
    x = PKTPS(set(range(20)) - {10})
    for s in list(range(10)), list(range(11, 20)):
        for a, b in zip(s, s[1:]):
            x.learn(a, b, LT)
    assert x.cmp(8, 9) == LT
    assert x.cmp(11, 12) == LT
    assert x.cmp(9, 11) == UN
    assert x.cmp(0, 19) == UN
    y = x.copy()

    x.learn(9, 11, LT)
    assert x.cmp(9, 11) == LT
    assert x.cmp(0, 19) == LT

    y.learn(9, 11, EQ)
    assert y.cmp(9, 11) == EQ
    assert y.cmp(0, 19) == LT

def test_complex():
    x = PKTPS("abcwxyz")

    x.learn("a", "b", LT)
    x.learn("c", "b", GT)
    x.learn("b", "w", EQ)
    assert x._summary() == "a<b a<c a<w b<c b=w w<c"
    was = x._summary()

    x.learn("x", "y", LT)
    x.learn("y", "z", LT)
    assert x._summary() == was + " x<y x<z y<z"

    y = x.copy()

    x.learn("b", "y", LT)
    assert x._summary() == "a<b a<c a<w a<y a<z b<c b=w b<y b<z w<c w<y w<z x<y x<z y<z"

    y.learn("b", "y", EQ)
    print(y.cmp("b", "z"))
    assert y._summary() == "a<b a<c a<w a<y a<z b<c b=w b=y b<z w<c w=y w<z x<b x<c x<w x<y x<z y<c y<z"

    return x

def test_extrema():
    x = PKTPS(range(4))
    x.learn(0, 1, LT)
    x.learn(1, 2, LT)
    assert x.mins() == x.maxes() == set()
    x.learn(2, 3, EQ)
    assert x.mins() == {0}
    assert x.maxes() == {2, 3}
    assert x.maxes(among = {0, 1, 3}) == {3}


def graph_example():
    x = test_complex()
    x.learn("a", "x", LT)
    x.render("/tmp/graph", format = 'png', view = True)

if __name__ == '__main__':
    graph_example()

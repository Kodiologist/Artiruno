from artiruno import (
    PreorderedSet, Relation, IC, LT, EQ, GT, ContradictionError, cmp, choose2)
import pytest

def test_simple():
    x = PreorderedSet(range(2))
    assert x.summary() == ""
    x.learn(0, 1, LT)
    assert x.summary() == "0<1"
    with pytest.raises(ContradictionError):
        x.learn(1, 0, LT)
    with pytest.raises(ContradictionError):
        x.learn(0, 0, LT)

    x = PreorderedSet(range(2))
    x.learn(1, 0, EQ)
    assert x.summary() == "0=1"

def test_trans():
    x = PreorderedSet("abc")
    x.learn("a", "b", LT)
    x.learn("c", "b", GT)

    y = PreorderedSet("abc", [["a", "b", LT], ["c", "b", GT]])

    for s in x, y:
        assert s.summary() == "a<b a<c b<c"
        with pytest.raises(ContradictionError):
            s.learn("c", "a", LT)

def test_long_trans():
    x = PreorderedSet(set(range(20)) - {10})
    for s in list(range(10)), list(range(11, 20)):
        for a, b in zip(s, s[1:]):
            x.learn(a, b, LT)
    assert x.cmp(8, 9) == LT
    assert x.cmp(11, 12) == LT
    assert x.cmp(9, 11) == IC
    assert x.cmp(0, 19) == IC
    y = x.copy()

    x.learn(9, 11, LT)
    assert x.cmp(9, 11) == LT
    assert x.cmp(0, 19) == LT

    y.learn(9, 11, EQ)
    assert y.cmp(9, 11) == EQ
    assert y.cmp(0, 19) == LT

def test_complex():
    x = PreorderedSet("abcwxyz")

    x.learn("a", "b", LT)
    x.learn("c", "b", GT)
    x.learn("b", "w", EQ)
    assert x.summary() == "a<b a<c a<w b<c b=w w<c"
    was = x.summary()

    x.learn("x", "y", LT)
    x.learn("y", "z", LT)
    assert x.summary() == was + " x<y x<z y<z"

    y = x.copy()

    x.learn("b", "y", LT)
    assert x.summary() == "a<b a<c a<w a<y a<z b<c b=w b<y b<z w<c w<y w<z x<y x<z y<z"

    y.learn("b", "y", EQ)
    assert y.summary() == "a<b a<c a<w a<y a<z b<c b=w b=y b<z w<c w=y w<z x<b x<c x<w x<y x<z y<c y<z"

    return x  # For `graph_example`.

def test_big():
    x = PreorderedSet(range(25))
    for a, b, r in [[6, 16, EQ], [16, 5, LT], [21, 11, EQ], [8, 10, EQ], [11, 20, LT], [8, 3, EQ], [1, 18, EQ], [2, 3, GT], [0, 2, LT], [12, 23, EQ], [1, 20, EQ], [23, 1, GT], [16, 13, LT], [14, 6, EQ], [1, 22, GT], [13, 2, GT], [24, 5, LT], [16, 3, EQ], [7, 16, EQ], [19, 16, EQ], [4, 17, LT], [4, 0, GT], [3, 7, EQ], [15, 16, EQ]]:
        x.learn(a, b, r)
    assert x.summary() == '0<2 0<4 0<13 0<17 1<12 1=18 1=20 1<23 2<13 3<2 3<5 3=6 3=7 3=8 3=10 3<13 3=14 3=15 3=16 3=19 4<17 6<2 6<5 6=7 6=8 6=10 6<13 6=14 6=15 6=16 6=19 7<2 7<5 7=8 7=10 7<13 7=14 7=15 7=16 7=19 8<2 8<5 8=10 8<13 8=14 8=15 8=16 8=19 10<2 10<5 10<13 10=14 10=15 10=16 10=19 11<1 11<12 11<18 11<20 11=21 11<23 12=23 14<2 14<5 14<13 14=15 14=16 14=19 15<2 15<5 15<13 15=16 15=19 16<2 16<5 16<13 16=19 18<12 18=20 18<23 19<2 19<5 19<13 20<12 20<23 21<1 21<12 21<18 21<20 21<23 22<1 22<12 22<18 22<20 22<23 24<5'

def test_extrema():
    x = PreorderedSet(range(4))
    x.learn(0, 1, LT)
    x.learn(1, 2, LT)
    assert x.mins() == x.maxes() == set()
    x.learn(2, 3, EQ)
    assert x.mins() == {0}
    assert x.maxes() == {2, 3}
    assert x.maxes(among = {0, 1, 3}) == {3}
    assert x.extreme(n = 2) == {2, 3}
    assert x.extreme(n = 3) == {1, 2, 3}

def test_extreme_n():
    x = PreorderedSet(l + str(i)
        for l in "wxyz"
        for i in range(3))
    for a, b in choose2(x.elements):
        x.learn(a, b, Relation.cmp(a[0], b[0]))

    assert (x.maxes() == x.extreme(2) == x.extreme(3) ==
        {"z0", "z1", "z2"})
    assert (x.extreme(4) == x.extreme(5) == x.extreme(6) ==
        {"z0", "z1", "z2", "y0", "y1", "y2"})
    def xb(n):
        return x.extreme(n, bottom = True)
    assert (x.mins() == xb(2) == xb(3) ==
        {"w0", "w1", "w2"})
    assert (xb(4) == xb(5) == xb(6) ==
        {"w0", "w1", "w2", "x0", "x1", "x2"})

def test_get_subset():
    x = PreorderedSet(("a", "b1", "b2", "c", "d"), (
        ("a", "b1", LT), ("a", "b2", LT),
        ("b1", "c", LT), ("b2", "c", LT),
        ("c", "d", LT)))
    y = x.get_subset(("a", "b2", "d"))
    assert x.summary() == "a<b1 a<b2 a<c a<d b1<c b1<d b2<c b2<d c<d"
    assert y.elements == {"a", "b2", "d"}
    assert y.summary() == "a<b2 a<d b2<d"

def test_add():
    x = PreorderedSet()
    x.add('a')
    x.add('z')
    assert x.cmp('a', 'z') == IC
    x.learn('a', 'z', LT)
    assert x.cmp('a', 'z') == LT
    x.add('f')
    x.learn('f', 'a', LT)
    assert x.cmp('f', 'a') == LT
    assert x.cmp('f', 'z') == LT

def test_learn_return_value():
    x = PreorderedSet((1, 2, 3))
    assert x.learn(1, 2, LT) == [(1, 2)]
    assert x.learn(2, 3, LT) == [(2, 3), (1, 3)]
    assert x.learn(1, 2, LT) == []


def graph_example():
    x = test_complex()
    x.learn("a", "x", LT)
    x.graph().render("/tmp/graph", format = 'png', view = True)

if __name__ == '__main__':
    graph_example()

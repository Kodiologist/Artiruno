from artiruno.pktps import PKTPS, UN, LT, EQ, GT, ContradictionError
import pytest

def test_simple():
    x = PKTPS(range(2))
    assert x._summary() == ""
    x.learn(0, 1, LT)
    assert x._summary() == "0<1"
    with pytest.raises(ContradictionError):
        x.learn(1, 0, LT)
    with pytest.raises(ContradictionError):
        x.learn(0, 0, LT)

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

def test_big():
    x = PKTPS(range(25))
    for a, b, r in [[6, 16, EQ], [16, 5, LT], [21, 11, EQ], [8, 10, EQ], [11, 20, LT], [8, 3, EQ], [1, 18, EQ], [2, 3, GT], [0, 2, LT], [12, 23, EQ], [1, 20, EQ], [23, 1, GT], [16, 13, LT], [14, 6, EQ], [1, 22, GT], [13, 2, GT], [24, 5, LT], [16, 3, EQ], [7, 16, EQ], [19, 16, EQ], [4, 17, LT], [4, 0, GT], [3, 7, EQ], [15, 16, EQ]]:
        x.learn(a, b, r)
    assert x._summary() == '0<2 0<4 0<13 0<17 1<12 1=18 1=20 1<23 2<13 3<2 3<5 3=6 3=7 3=8 3=10 3<13 3=14 3=15 3=16 3=19 4<17 6<2 6<5 6=7 6=8 6=10 6<13 6=14 6=15 6=16 6=19 7<2 7<5 7=8 7=10 7<13 7=14 7=15 7=16 7=19 8<2 8<5 8=10 8<13 8=14 8=15 8=16 8=19 10<2 10<5 10<13 10=14 10=15 10=16 10=19 11<1 11<12 11<18 11<20 11=21 11<23 12=23 14<2 14<5 14<13 14=15 14=16 14=19 15<2 15<5 15<13 15=16 15=19 16<2 16<5 16<13 16=19 18<12 18=20 18<23 19<2 19<5 19<13 20<12 20<23 21<1 21<12 21<18 21<20 21<23 22<1 22<12 22<18 22<20 22<23 24<5'

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

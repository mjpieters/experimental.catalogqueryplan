import unittest

from BTrees.IIBTree import intersection, difference
from BTrees.IIBTree import IISet, IITreeSet, IIBTree


class TestIntersection(unittest.TestCase):
    def test_empty(self):
        empty = IISet()
        self.failUnlessEqual(intersection(None, None), None)
        self.failUnlessEqual(intersection(empty, empty), empty)

        s1 = IISet([1])
        s2 = IISet([2])
        self.failUnlessEqual(list(intersection(s1, empty)), [])
        self.failUnlessEqual(list(intersection(empty, s2)), [])
        self.failUnlessEqual(list(intersection(s1, s2)), [])
        self.failUnlessEqual(list(intersection(s2, s1)), [])

        ts1 = IITreeSet([1])
        ts2 = IITreeSet([2])
        self.failUnlessEqual(list(intersection(ts1, empty)), [])
        self.failUnlessEqual(list(intersection(empty, ts2)), [])
        self.failUnlessEqual(list(intersection(ts1, ts2)), [])
        self.failUnlessEqual(list(intersection(ts2, ts1)), [])

        self.failUnlessEqual(list(intersection(ts1, s2)), [])
        self.failUnlessEqual(list(intersection(s1, ts2)), [])

        bt1 = IIBTree({1:1})
        bt2 = IIBTree({2:2})
        self.failUnlessEqual(list(intersection(bt1, empty)), [])
        self.failUnlessEqual(list(intersection(empty, bt2)), [])
        self.failUnlessEqual(list(intersection(bt1, bt2)), [])
        self.failUnlessEqual(list(intersection(bt2, bt1)), [])

        self.failUnlessEqual(list(intersection(bt1, s2)), [])
        self.failUnlessEqual(list(intersection(s1, bt2)), [])

        self.failUnlessEqual(list(intersection(bt1, ts2)), [])
        self.failUnlessEqual(list(intersection(ts1, bt2)), [])

    def test_simple(self):
        s1 = IISet([1,2,3,4])
        s2 = IISet([3,4,5,6])
        self.failUnlessEqual(list(intersection(s1, s2)), [3,4])
        self.failUnlessEqual(list(intersection(s2, s1)), [3,4])

        ts1 = IITreeSet([1,2,3,4])
        ts2 = IITreeSet([3,4,5,6])
        self.failUnlessEqual(list(intersection(ts1, ts2)), [3,4])
        self.failUnlessEqual(list(intersection(ts2, ts1)), [3,4])

        self.failUnlessEqual(list(intersection(s1, ts2)), [3,4])
        self.failUnlessEqual(list(intersection(ts1, s2)), [3,4])

        bt1 = IIBTree(dict.fromkeys([1,2,3,4], 0))
        bt2 = IIBTree(dict.fromkeys([3,4,5,6], 0))
        self.failUnlessEqual(list(intersection(bt1, bt2)), [3,4])
        self.failUnlessEqual(list(intersection(bt2, bt1)), [3,4])

        self.failUnlessEqual(list(intersection(ts1, bt2)), [3,4])
        self.failUnlessEqual(list(intersection(bt1, ts2)), [3,4])

        self.failUnlessEqual(list(intersection(s1, bt2)), [3,4])
        self.failUnlessEqual(list(intersection(bt1, s2)), [3,4])


    def test_largesmall(self):
        s1 = IISet([5000])
        s2 = IISet(range(0,10000))
        self.failUnlessEqual(list(intersection(s1, s2)), [5000])
        self.failUnlessEqual(list(intersection(s2, s1)), [5000])

        ts1 = IITreeSet([5000])
        ts2 = IITreeSet(range(0,10000))
        self.failUnlessEqual(list(intersection(ts1, ts2)), [5000])
        self.failUnlessEqual(list(intersection(ts2, ts1)), [5000])

        self.failUnlessEqual(list(intersection(s1, ts2)), [5000])
        self.failUnlessEqual(list(intersection(ts1, s2)), [5000])

        bt1 = IIBTree({5000:5000})
        bt2 = IIBTree(dict.fromkeys(range(0,10000), 0))
        self.failUnlessEqual(list(intersection(bt1, bt2)), [5000])
        self.failUnlessEqual(list(intersection(bt2, bt1)), [5000])

        self.failUnlessEqual(list(intersection(ts1, bt2)), [5000])
        self.failUnlessEqual(list(intersection(bt1, ts2)), [5000])

        self.failUnlessEqual(list(intersection(s1, bt2)), [5000])
        self.failUnlessEqual(list(intersection(bt1, s2)), [5000])


class TestDifference(unittest.TestCase):
    def test_empty(self):
        self.failUnlessEqual(difference(None, None), None)
        empty = IISet()
        self.failUnlessEqual(difference(None, empty), None)
        self.failUnlessEqual(difference(empty, None), empty)
        self.failUnlessEqual(difference(empty, empty), empty)

        s1 = IISet([1])
        self.failUnlessEqual(list(difference(empty, s1)), [])

        ts1 = IITreeSet([1])
        self.failUnlessEqual(list(difference(empty, ts1)), [])

        bt1 = IIBTree(dict.fromkeys([1],0))
        self.failUnlessEqual(list(difference(empty, bt1)), [])

    def test_single(self):
        empty = IISet()
        s1 = IISet([1])
        s2 = IISet([2])
        self.failUnlessEqual(list(difference(s1, empty)), [1])
        self.failUnlessEqual(list(difference(s1, s2)), [1])
        self.failUnlessEqual(list(difference(s2, s1)), [2])

        ts1 = IITreeSet([1])
        ts2 = IITreeSet([2])
        self.failUnlessEqual(list(difference(ts1, empty)), [1])
        self.failUnlessEqual(list(difference(ts1, ts2)), [1])
        self.failUnlessEqual(list(difference(ts2, ts1)), [2])

        bt1 = IIBTree(dict.fromkeys([1],0))
        bt2 = IIBTree(dict.fromkeys([2],0))
        self.failUnlessEqual(list(difference(bt1, empty)), [1])
        self.failUnlessEqual(list(difference(bt1, bt2)), [1])
        self.failUnlessEqual(list(difference(bt2, bt1)), [2])

    def test_simple(self):
        empty = IISet()
        s1 = IISet([1,2,3,4])
        s2 = IISet([3,4,5,6])
        self.failUnlessEqual(list(difference(s1, empty)), [1,2,3,4])
        self.failUnlessEqual(list(difference(s1, s2)), [1,2])
        self.failUnlessEqual(list(difference(s2, s1)), [5,6])

        ts1 = IITreeSet([1,2,3,4])
        ts2 = IITreeSet([3,4,5,6])
        self.failUnlessEqual(list(difference(ts1, empty)), [1,2,3,4])
        self.failUnlessEqual(list(difference(ts1, ts2)), [1,2])
        self.failUnlessEqual(list(difference(ts2, ts1)), [5,6])

        bt1 = IIBTree(dict.fromkeys([1,2,3,4],0))
        bt2 = IIBTree(dict.fromkeys([3,4,5,6],0))
        self.failUnlessEqual(list(difference(bt1, empty)), [1,2,3,4])
        self.failUnlessEqual(list(difference(bt1, bt2)), [1,2])
        self.failUnlessEqual(list(difference(bt2, bt1)), [5,6])

    def test_largesmall(self):
        empty = IISet()
        s1 = IISet([5000])
        s2 = IISet(range(0,10000))
        self.failUnlessEqual(list(difference(s1, empty)), list(s1))
        self.failUnlessEqual(list(difference(s1, s2)), [])
        self.failUnlessEqual(list(difference(s2, s1)), [x for x in s2 if x != 5000])

        ts1 = IITreeSet([5000])
        ts2 = IITreeSet(range(0,10000))
        self.failUnlessEqual(list(difference(ts1, empty)), list(s1))
        self.failUnlessEqual(list(difference(ts1, ts2)), [])
        self.failUnlessEqual(list(difference(ts2, ts1)), [x for x in s2 if x != 5000])

        bt1 = IIBTree(dict.fromkeys([5000],0))
        bt2 = IIBTree(dict.fromkeys(range(0,10000),0))
        self.failUnlessEqual(list(difference(bt1, empty)), list(s1))
        self.failUnlessEqual(list(difference(bt1, bt2)), [])
        self.failUnlessEqual(list(difference(bt2, bt1)), [x for x in s2 if x != 5000])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestIntersection))
    suite.addTest(makeSuite(TestDifference))
    return suite

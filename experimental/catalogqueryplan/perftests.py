from time import time
import unittest

from BTrees.IIBTree import intersection, _old_intersection
from BTrees.IIBTree import IISet, IITreeSet, IIBTree

SMALLSETSIZE = 100
BIGSETSIZE = 100000

class TestIntersection(unittest.TestCase):

    def pytiming(self, small, large):
        py = 0.0
        for i in xrange(10):
            start = time()
            res = small.intersection(large)
            py+=(time()-start)

        print '\nPy x10:  %.6f' % (py)

    def timing(self, small, large):
        new = 0.0
        old = 0.0
        for i in xrange(10):
            start = time()
            res = _old_intersection(small, large)
            old+=(time()-start)

            start = time()
            res = intersection(small, large)
            new+=(time()-start)

        print 'Old x10: %.6f' % (old)
        print 'New x10: %.6f' % (new)

    def test_heavy_start(self):
        bigsize = BIGSETSIZE
        smallsize = SMALLSETSIZE
        small = IISet(xrange(smallsize))
        large = IITreeSet(xrange(bigsize))
        print '\nSmall set low values + large treeset'
        self.timing(small, large)

        small = IISet(xrange(smallsize))
        large = IISet(xrange(bigsize))
        print '\nSmall set low values + large set'
        self.timing(small, large)

        small = set(xrange(smallsize))
        large = set(xrange(bigsize))
        self.pytiming(small, large)

    def test_heavy_end(self):
        bigsize = BIGSETSIZE
        smallsize = SMALLSETSIZE
        small = IISet(xrange(bigsize-smallsize,bigsize))
        large = IITreeSet(xrange(bigsize))
        print '\nSmall set high values + large treeset'
        self.timing(small, large)

        small = IISet(xrange(bigsize-smallsize,bigsize))
        large = IISet(xrange(bigsize))
        print '\nSmall set high values + large set'
        self.timing(small, large)

        small = set(xrange(bigsize-smallsize,bigsize))
        large = set(xrange(bigsize))
        self.pytiming(small, large)

    def test_even_dist(self):
        bigsize = BIGSETSIZE
        smallsize = SMALLSETSIZE
        small = IISet(xrange(0, bigsize, bigsize/smallsize))
        large = IITreeSet(xrange(bigsize))
        print '\nSmall set even distribution + large treeset'
        self.timing(small, large)

        small = IISet(xrange(0, bigsize, bigsize/smallsize))
        large = IISet(xrange(bigsize))
        print '\nSmall set even distribution + large set'
        self.timing(small, large)

        small = set(xrange(0, bigsize, bigsize/smallsize))
        large = set(xrange(bigsize))
        self.pytiming(small, large)

    def DONTtest_large(self):
        bigsize = BIGSETSIZE
        small = IITreeSet(xrange(bigsize))
        large = IITreeSet(xrange(bigsize))
        print '\nLarge sets'
        self.timing(small, large)

        small = set(xrange(bigsize))
        large = set(xrange(bigsize))
        self.pytiming(small, large)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestIntersection))
    return suite

from time import time
import unittest

from BTrees.IIBTree import intersection, _old_intersection
from BTrees.IIBTree import IISet, IITreeSet, IIBTree

DATASETSIZE = 1000000

class TestIntersection(unittest.TestCase):

    def pytiming(self, small, large):
        py = 0.0
        for i in xrange(10):
            start = time()
            res = small.intersection(large)
            py+=(time()-start)

        print 'Py x10: %.6f' % (py)

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
        size = DATASETSIZE
        small = IISet(xrange(10))
        large = IITreeSet(xrange(size))
        print '\nSmall set low values + large set'
        self.timing(small, large)

        small = set(xrange(10))
        large = set(xrange(size))
        self.pytiming(small, large)

    def test_heavy_end(self):
        size = DATASETSIZE
        small = IISet(xrange(size-10,size))
        large = IITreeSet(xrange(size))
        print '\nSmall set high values + large set'
        self.timing(small, large)

        small = set(xrange(size-10,size))
        large = set(xrange(size))
        self.pytiming(small, large)

    def test_even_dist(self):
        size = DATASETSIZE
        small = IISet(xrange(0, size, size/10))
        large = IITreeSet(xrange(size))
        print '\nSmall set even distribution + large set'
        self.timing(small, large)

        small = set(xrange(0, size, size/10))
        large = set(xrange(size))
        self.pytiming(small, large)

    def test_large(self):
        size = DATASETSIZE
        small = IITreeSet(xrange(size))
        large = IITreeSet(xrange(size))
        print '\nLarge sets'
        self.timing(small, large)

        small = set(xrange(size))
        large = set(xrange(size))
        self.pytiming(small, large)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestIntersection))
    return suite

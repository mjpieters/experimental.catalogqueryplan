from time import time
import unittest

from experimental.catalogqueryplan import setpatches
setpatches.apply(no_coptimizations=True)
from BTrees.IIBTree import intersection as intersection2
from BTrees.IIBTree import difference as difference2

setpatches.unapply()

from BTrees.IIBTree import intersection
from BTrees.IIBTree import difference

from BTrees.IIBTree import IISet, IITreeSet, IIBTree

try:
    from experimental.catalogqueryplan.difference import ciidifference
    from experimental.catalogqueryplan.intersection import ciiintersection
except ImportError:
    ciidifference = None
    ciiintersection = None

SMALLSETSIZE = 30
BIGSETSIZE = 1000000
LOOP = 100

class TestIntersection(unittest.TestCase):

    level = 2

    def pytiming(self, small, large):
        py = 0.0
        loop = LOOP
        for i in xrange(loop):
            start = time()
            res = small.intersection(large)
            py+=(time()-start)

        print '\nPy x%s:  %.6f' % (loop, py)

    def timing(self, small, large):
        new = 0.0
        old = 0.0
        new2 = 0.0
        c = 0.0
        loop = LOOP
        for i in xrange(loop):

            start = time()
            res = intersection2(small, large)
            new+=(time()-start)

            start = time()
            res = intersection(small, large)
            old+=(time()-start)

            if ciiintersection is not None:
                start = time()
                res = ciiintersection(small, large)
                c+=(time()-start)

        print 'Old x%s: %.6f' % (loop, old)
        print 'New x%s: %.6f' % (loop, new)
        if ciiintersection is not None:
            print 'Cyt x%s: %.6f' % (loop, c)

    def test_None(self):
        bigsize = BIGSETSIZE
        large = IITreeSet(xrange(bigsize))
        print '\nIntersection large, None'
        self.timing(large, None)
        print '\nIntersection None, large'
        self.timing(None, large)

    def test_empty(self):
        bigsize = BIGSETSIZE
        smallsize = 0
        small = IISet(xrange(smallsize))
        large = IITreeSet(xrange(bigsize))

        print '\nIntersection empty set + large treeset'
        self.timing(small, large)

        small = IITreeSet(xrange(smallsize))
        large = IISet(xrange(bigsize))
        print '\nIntersection empty tree set + large set'
        self.timing(small, large)

    def test_heavy_start(self):
        bigsize = BIGSETSIZE
        smallsize = SMALLSETSIZE

        small = IISet(xrange(smallsize))
        large = IITreeSet(xrange(smallsize))
        print '\nIntersection small set low values + small treeset'
        self.timing(small, large)

        small = IISet(xrange(smallsize))
        large = IITreeSet(xrange(bigsize))
        print '\nIntersection small set low values + large treeset'
        self.timing(small, large)

        small = IISet(xrange(smallsize))
        large = IISet(xrange(bigsize))
        print '\nIntersection small set low values + large set'
        self.timing(small, large)

        small = set(xrange(smallsize))
        large = set(xrange(bigsize))
        self.pytiming(small, large)

    def test_heavy_end(self):
        bigsize = BIGSETSIZE
        smallsize = SMALLSETSIZE

        small = IISet(xrange(bigsize-smallsize,bigsize))
        large = IITreeSet(xrange(smallsize))
        print '\nIntersection small set high values + small treeset'
        self.timing(small, large)

        small = IISet(xrange(bigsize-smallsize,bigsize))
        large = IITreeSet(xrange(bigsize))
        print '\nIntersection small set high values + large treeset'
        self.timing(small, large)

        small = IISet(xrange(bigsize-smallsize,bigsize))
        large = IISet(xrange(bigsize))
        print '\nIntersection small set high values + large set'
        self.timing(small, large)

        small = set(xrange(bigsize-smallsize,bigsize))
        large = set(xrange(bigsize))
        self.pytiming(small, large)

    def test_even_dist(self):
        bigsize = BIGSETSIZE
        smallsize = SMALLSETSIZE

        small = IISet(xrange(0, bigsize, bigsize/smallsize))
        large = IITreeSet(xrange(smallsize))
        print '\nIntersection small set even distribution + small treeset'
        self.timing(small, large)

        small = IISet(xrange(0, bigsize, bigsize/smallsize))
        large = IITreeSet(xrange(bigsize))
        print '\nIntersection small set even distribution + large treeset'
        self.timing(small, large)

        small = IISet(xrange(0, bigsize, bigsize/smallsize))
        large = IISet(xrange(bigsize))
        print '\nIntersection small set even distribution + large set'
        self.timing(small, large)

        small = set(xrange(0, bigsize, bigsize/smallsize))
        large = set(xrange(bigsize))
        self.pytiming(small, large)

    def test_small(self):
        bigsize = BIGSETSIZE
        smallsize = SMALLSETSIZE
        small = IITreeSet(xrange(smallsize))
        large = IITreeSet(xrange(smallsize))
        print '\nIntersection small tree sets'
        self.timing(small, large)

        small = IISet(xrange(smallsize))
        large = IISet(xrange(smallsize))
        print '\nIntersection small sets'
        self.timing(small, large)

        small = set(xrange(bigsize))
        large = set(xrange(bigsize))
        self.pytiming(small, large)

    def test_large(self):
        bigsize = BIGSETSIZE
        small = IITreeSet(xrange(bigsize))
        large = IITreeSet(xrange(bigsize))
        print '\nIntersection Large tree sets'
        self.timing(small, large)

        small = IISet(xrange(bigsize))
        large = IISet(xrange(bigsize))
        print '\nIntersection Large sets'
        self.timing(small, large)

        small = set(xrange(bigsize))
        large = set(xrange(bigsize))
        self.pytiming(small, large)


class TestDifference(unittest.TestCase):

    level = 2

    def pytiming(self, small, large):
        py = 0.0
        loop = LOOP
        for i in xrange(10):
            start = time()
            res = small.difference(large)
            py+=(time()-start)

        print '\nPy x%s:  %.6f' % (loop, py)

    def timing(self, small, large):
        new = 0.0
        old = 0.0
        c = 0.0
        loop = LOOP
        for i in xrange(10):
            start = time()
            res = difference(small, large)
            old+=(time()-start)

            start = time()
            res = difference2(small, large)
            new+=(time()-start)

            if ciidifference is not None:
                start = time()
                res = ciidifference(small, large)
                c+=(time()-start)

        print 'Old x%s: %.6f' % (loop, old)
        print 'New x%s: %.6f' % (loop, new)
        if ciidifference is not None:
            print 'Cyt x%s: %.6f' % (loop, c)

    def test_heavy_start(self):
        bigsize = BIGSETSIZE
        smallsize = SMALLSETSIZE
        small = IISet(xrange(smallsize))
        large = IITreeSet(xrange(bigsize))
        print '\nDifference Small set low values + large treeset'
        self.timing(small, large)

        small = IISet(xrange(smallsize))
        large = IISet(xrange(bigsize))
        print '\nDifference Small set low values + large set'
        self.timing(small, large)

        small = set(xrange(smallsize))
        large = set(xrange(bigsize))
        self.pytiming(small, large)

    def test_heavy_end(self):
        bigsize = BIGSETSIZE
        smallsize = SMALLSETSIZE
        small = IISet(xrange(bigsize-smallsize,bigsize))
        large = IITreeSet(xrange(bigsize))
        print '\nDifference Small set high values + large treeset'
        self.timing(small, large)

        small = IISet(xrange(bigsize-smallsize,bigsize))
        large = IISet(xrange(bigsize))
        print '\nDifference Small set high values + large set'
        self.timing(small, large)

        small = set(xrange(bigsize-smallsize,bigsize))
        large = set(xrange(bigsize))
        self.pytiming(small, large)

    def test_even_dist(self):
        bigsize = BIGSETSIZE
        smallsize = SMALLSETSIZE
        small = IISet(xrange(0, bigsize, bigsize/smallsize))
        large = IITreeSet(xrange(bigsize))
        print '\nDifference Small set even distribution + large treeset'
        self.timing(small, large)

        small = IISet(xrange(0, bigsize, bigsize/smallsize))
        large = IISet(xrange(bigsize))
        print '\nDifference Small set even distribution + large set'
        self.timing(small, large)

        small = set(xrange(0, bigsize, bigsize/smallsize))
        large = set(xrange(bigsize))
        self.pytiming(small, large)

    def test_large(self):
        bigsize = BIGSETSIZE
        small = IITreeSet(xrange(bigsize))
        large = IITreeSet(xrange(bigsize))
        print '\nDifference Large sets'
        self.timing(small, large)

        small = set(xrange(bigsize))
        large = set(xrange(bigsize))
        self.pytiming(small, large)

    def test_lookup(self):
        bigsize = 1000000
        smallsize = 1000
        large = IISet(xrange(bigsize))
        small = IISet(xrange(0, bigsize, bigsize/smallsize))

        start = time()
        for i in small:
            a = large[i]
        print "\ngetitem distributed %.6f" % (time()-start)

        start = time()
        for i in small:
            a = large[bigsize-1]
        print "getitem end %.6f" % (time()-start)

        start = time()
        for i in small:
            a = large[0]
        print "getitem start %.6f" % (time()-start)

        start = time()
        for i in small:
            a = large.has_key(i)
        print "\nhas_key distributed %.6f" % (time()-start)

        start = time()
        for i in small:
            a = large.has_key(bigsize-1)
        print "has_key end %.6f" % (time()-start)

        start = time()
        for i in small:
            a = large.has_key(0)
        print "has_key start %.6f" % (time()-start)


    def test_findlargesmallset(self):
        # Test different approaches to finding the large and small set
        bigsize = 10
        smallsize = 2
        o1 = IISet(xrange(bigsize))
        l1 = len(o1)
        o2 = IISet(xrange(0, bigsize, bigsize/smallsize))
        l2 = len(o2)

        # 3 approaches: if/else, sorted and max/min
        def alternative1():
            if l1 < l2:
                ls = l1
                small = o1
                lb = l2
                big = o2
            else:
                ls = l2
                small = o2
                lb = l1
                big = o1
            return (ls, small), (lb, big)

        def alternative2():
            return sorted(((l2,o2), (l1,o1)))

        def alternative3():
            small = min((l2,o2),(l1,o1))
            big = max((l2,o2),(l1,o1))
            return small,big

        self.failUnlessEqual(list(alternative1()), list(alternative2()))
        self.failUnlessEqual(list(alternative1()), list(alternative3()))

        start = time()
        for i in xrange(1000):
            alternative1()
        print '\nif/else took %.6f' % (time()-start)

        start = time()
        for i in xrange(1000):
            alternative2()
        print 'sorted took  %.6f' % (time()-start)

        start = time()
        for i in xrange(1000):
            alternative3()
        print 'minmax took  %.6f' % (time()-start)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestIntersection))
    suite.addTest(makeSuite(TestDifference))
    return suite

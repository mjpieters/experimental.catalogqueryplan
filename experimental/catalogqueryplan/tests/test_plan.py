import unittest

from experimental.catalogqueryplan import setpatches
setpatches.apply()

from BTrees.IIBTree import intersection as iiintersection
from BTrees.IIBTree import weightedIntersection as iiweightedIntersection
from BTrees.IIBTree import difference as iidifference
from BTrees.IIBTree import IISet, IITreeSet, IIBTree, IIBucket

from BTrees.IOBTree import intersection as iointersection
from BTrees.IOBTree import difference as iodifference
from BTrees.IOBTree import IOSet, IOTreeSet, IOBTree, IOBucket

from BTrees.OIBTree import intersection as oiintersection
from BTrees.OIBTree import weightedIntersection as oiweightedIntersection
from BTrees.OIBTree import difference as oidifference
from BTrees.OIBTree import OISet, OITreeSet, OIBTree, OIBucket

from BTrees.OOBTree import intersection as oointersection
from BTrees.OOBTree import difference as oodifference
from BTrees.OOBTree import OOSet, OOTreeSet, OOBTree, OOBucket

from BTrees.tests import testSetOps

from Products.PluginIndexes.FieldIndex.tests import testFieldIndex
class TestFieldIndex(testFieldIndex.FieldIndexTests):
    pass

from Products.PluginIndexes.KeywordIndex.tests import testKeywordIndex
class TestKeywordIndex(testKeywordIndex.TestKeywordIndex):
    pass

from Products.PluginIndexes.DateIndex.tests import test_DateIndex
class TestDateIndex(test_DateIndex.DI_Tests):
    pass

from Products.ExtendedPathIndex.tests import testExtendedPathIndex
class TestExtendedPathIndex(testExtendedPathIndex.TestExtendedPathIndex):
    pass


class SetResult(testSetOps.SetResult):
    def testNone(self):
        for op in self.union, self.intersection, self.difference:
            C = op(None, None)
            self.assert_(C is None)

        for op in self.union, self.intersection, self.difference:
            for A in self.As:
                C = op(A, None)
                self.assert_(C is A)

                C = op(None, A)
                if op == self.difference:
                    self.assert_(C is None)
                else:
                    self.assert_(C is A)

class TestPureII(SetResult):
    from BTrees.IIBTree import union
    def intersection(self, o1, o2):
        return iiintersection(o1, o2)
    def difference(self, o1, o2):
        return iidifference(o1, o2)
    builders = IISet, IITreeSet, testSetOps.makeBuilder(IIBTree), testSetOps.makeBuilder(IIBucket)

class TestPureIO(SetResult):
    from BTrees.IOBTree import union
    def intersection(self, o1, o2):
        return iointersection(o1, o2)
    def difference(self, o1, o2):
        return iodifference(o1, o2)
    builders = IOSet, IOTreeSet, testSetOps.makeBuilder(IOBTree), testSetOps.makeBuilder(IOBucket)

class TestPureOO(SetResult):
    from BTrees.OOBTree import union
    def intersection(self, o1, o2):
        return oointersection(o1, o2)
    def difference(self, o1, o2):
        return oodifference(o1, o2)
    builders = OOSet, OOTreeSet, testSetOps.makeBuilder(OOBTree), testSetOps.makeBuilder(OOBucket)

class TestPureOI(SetResult):
    from BTrees.OIBTree import union
    def intersection(self, o1, o2):
        return oiintersection(o1, o2)
    def difference(self, o1, o2):
        return oidifference(o1, o2)
    builders = OISet, OITreeSet, testSetOps.makeBuilder(OIBTree), testSetOps.makeBuilder(OIBucket)


class TestWeightedII(testSetOps.Weighted):
    def intersection(self, o1, o2):
        return iiintersection(o1, o2)
    def weightedIntersection(self, o1, o2, w1=1, w2=1):
        return iiweightedIntersection(o1, o2, w1, w2)
    from BTrees.IIBTree import weightedUnion, union
    from BTrees.IIBTree import IIBucket as mkbucket
    builders = IIBucket, IIBTree, testSetOps.itemsToSet(IISet), testSetOps.itemsToSet(IITreeSet)


class TestWeightedOI(testSetOps.Weighted):
    def intersection(self, o1, o2):
        return oiintersection(o1, o2)
    def weightedIntersection(self, o1, o2, w1=1, w2=1):
        return oiweightedIntersection(o1, o2, w1, w2)
    from BTrees.OIBTree import weightedUnion, union
    from BTrees.OIBTree import union
    from BTrees.OIBTree import OIBucket as mkbucket
    builders = OIBucket, OIBTree, testSetOps.itemsToSet(OISet), testSetOps.itemsToSet(OITreeSet)


class TestPriorityMap(unittest.TestCase):

    test_map = { 'foo': ['bar'] }

    def testDefaultPriorityMap(self):
        from experimental.catalogqueryplan import catalog
        self.assertEqual(catalog.DEFAULT_PRIORITYMAP, None)

    def testLoadPriorityMap(self):
        from experimental.catalogqueryplan.utils import loadPriorityMap
        from os import environ
        environ['CATALOGQUERYPLAN'] = __name__ + '.TestPriorityMap.test_map'
        self.assertEqual(loadPriorityMap(), dict(foo=['bar']))

    def testLoadBadPriorityMap(self):
        from experimental.catalogqueryplan.utils import loadPriorityMap
        from os import environ
        environ['CATALOGQUERYPLAN'] = 'foo.bar'
        self.assertEqual(loadPriorityMap(), None)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestFieldIndex))
    suite.addTest(makeSuite(TestKeywordIndex))
    suite.addTest(makeSuite(TestDateIndex))
    suite.addTest(makeSuite(TestExtendedPathIndex))
    suite.addTest(makeSuite(TestPureII))
    suite.addTest(makeSuite(TestPureIO))
    suite.addTest(makeSuite(TestPureOO))
    suite.addTest(makeSuite(TestPureOI))
    suite.addTest(makeSuite(TestWeightedII))
    suite.addTest(makeSuite(TestWeightedOI))
    suite.addTest(makeSuite(TestPriorityMap))
    return suite

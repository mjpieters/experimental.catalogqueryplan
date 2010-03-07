from logging import getLogger
from threading import currentThread
from time import time

from BTrees.IIBTree import intersection, weightedIntersection, IIBucket, IIBTree
from Products.ZCatalog.Lazy import LazyMap, LazyCat

from experimental.catalogqueryplan.config import LOG_SLOW_QUERIES
from experimental.catalogqueryplan.config import LONG_QUERY_TIME
from experimental.catalogqueryplan.utils import loadPriorityMap

logger = getLogger('catalogqueryplan')

MAX_DISTINCT_VALUES = 20

ADVANCEDTYPES = []
VALUETYPES = []

DEFAULT_PRIORITYMAP = loadPriorityMap()

class RequestCache(dict):
    def __str__(self):
        return "<RequestCache %s items>" % len(self)

def determine_value_indexes(catalog):
    # This function determines all indexes whose values should be respected
    # in the prioritymap key. A index type needs to be registered in the
    # VALUETYPES module global and the number of unique values needs to be
    # lower than the MAX_DISTINCT_VALUES watermark.
    valueindexes = []
    for name, index in catalog.indexes.items():
        if type(index) in VALUETYPES:
            if len(index) < MAX_DISTINCT_VALUES:
                # Checking for len of an index should be fast. It's a stored
                # BTrees.Length value and requires no calculation.
                valueindexes.append(name)
    return frozenset(valueindexes)


def search(self, request, sort_index=None, reverse=0, limit=None, merge=1):
    advancedtypes = tuple(ADVANCEDTYPES)
    rs = None # resultset

    # Note that if the indexes find query arguments, but the end result
    # is an empty sequence, we do nothing

    prioritymap = getattr(self, '_v_prioritymap', None)
    if prioritymap is None:
        identifier = '/'.join(self.getPhysicalPath())
        if DEFAULT_PRIORITYMAP is not None:
            default = DEFAULT_PRIORITYMAP.get(identifier, None)
            logger.info('initializing priority map for %r from default (thread %s)',
                identifier, currentThread().getName())
            if default is not None:
                prioritymap = self._v_prioritymap = default.copy()
            else:
                prioritymap = self._v_prioritymap = {}
            valueidentifier = identifier + ':valueindexes'
            valuedefault = DEFAULT_PRIORITYMAP.get(valueidentifier, None)
            if valuedefault is not None:
                self._v_valueindexes = valuedefault.copy()
        else:
            logger.info('initializing empty priority map for %r (thread %s)',
                identifier, currentThread().getName())
            prioritymap = self._v_prioritymap = {}

    valueindexes = getattr(self, '_v_valueindexes', None)
    if valueindexes is None:
        valueindexes = self._v_valueindexes = determine_value_indexes(self)

    existing_indexes = self.indexes.keys()

    # What follows is a bit of a mess, but the ZCatalog API supports passing
    # in query restrictions in almost arbitary ways
    if isinstance(request, dict):
        keydict = request.copy()
    else:
        keydict = {}
        keydict.update(request.keywords)
        real_req = request.request
        if isinstance(real_req, dict):
            keydict.update(real_req)
        known_keys = keydict.keys()
        # The request has too many places where an index restriction might be
        # specified. Putting all of request.form, request.other, ... into the
        # key isn't what we want either, so we iterate over all known indexes
        # instead and see if they are in the request.
        for iid in existing_indexes:
            if iid in known_keys:
                continue
            value = real_req.get(iid)
            if value:
                keydict[iid] = value

    key = keys = keydict.keys()
    values = [name for name in keys if name in valueindexes]
    if values:
        # If we have indexes whose values should be considered, we first
        # preserve all normal indexes and then add the keys whose values
        # matter including their value into the key
        key = [name for name in keys if name not in values]
        for name in values:
            # We need to make sure the key is immutable, repr() is an easy way
            # to do this without imposing restrictions on the types of values
            key.append((name, repr(keydict.get(name, ''))))

    key = tuple(sorted(key))
    indexes = prioritymap.get(key, [])
    start = time()
    index_times = {}

    if not indexes:
        pri = []
        for i in existing_indexes:
            if i not in keys:
                # Do not ask indexes to restrict the result, which aren't part
                # of the query
                continue
            index = self.getIndex(i)
            _apply_index = getattr(index, "_apply_index", None)
            if _apply_index is None:
                continue
            r = _apply_index(request)

            result_len = 0
            if r is not None:
                r, u = r
                result_len = len(r)
                w, rs = weightedIntersection(rs, r)
            pri.append((isinstance(index, advancedtypes), result_len, i))

        pri.sort()
        prioritymap[key] = [p[-1] for p in pri]

    else:
        for i in indexes:
            index = self.getIndex(i)
            _apply_index = getattr(index, "_apply_index", None)
            if _apply_index is None:
                continue
            index_times[i] = time()
            if isinstance(index, advancedtypes):
                r = _apply_index(request, res=rs)
            else:
                r = _apply_index(request)
            index_times[i] = time() - index_times[i]

            if r is not None:
                # Short circuit if empty result
                r, u = r
                if not r:
                    return LazyCat([])
                if rs is None:
                    rs = r
                # Because weightedIntersection isn't optimized we only use it if necessary
                elif isinstance(rs, (IIBucket, IIBTree)) or isinstance(r, (IIBucket, IIBTree)):
                    _i = '%s_weightedIntersection'%i
                    index_times[_i] = time()
                    w, rs = weightedIntersection(rs, r)
                    index_times[_i] = time() - index_times[_i]
                else:
                    _i = '%s_intersection'%i
                    index_times[_i] = time()
                    rs = intersection(rs, r)
                    index_times[_i] = time() - index_times[_i]
    duration =  time() - start
    if LOG_SLOW_QUERIES and duration >= LONG_QUERY_TIME:
        detailed_times = []
        for i, t in index_times.items():
            detailed_times.append("%s : %3.2fms" % (i, t*1000))
        info = 'query: %3.2fms, priority: %s, key: %s' % (duration*1000, indexes, key)
        if detailed_times:
            info += ', detailed: %s' % (', '.join(detailed_times))
        logger.info(info)

    if rs is None:
        # None of the indexes found anything to do with the request
        # We take this to mean that the query was empty (an empty filter)
        # and so we return everything in the catalog
        if sort_index is None:
            return LazyMap(self.instantiate, self.data.items(), len(self))
        else:
            return self.sortResults(
                self.data, sort_index, reverse,  limit, merge)
    elif rs:
        # We got some results from the indexes.
        # Sort and convert to sequences.
        # XXX: The check for 'values' is really stupid since we call
        # items() and *not* values()
        if sort_index is None and hasattr(rs, 'values'):
            # having a 'values' means we have a data structure with
            # scores.  Build a new result set, sort it by score, reverse
            # it, compute the normalized score, and Lazify it.

            if not merge:
                # Don't bother to sort here, return a list of
                # three tuples to be passed later to mergeResults
                # note that data_record_normalized_score_ cannot be
                # calculated and will always be 1 in this case
                getitem = self.__getitem__
                return [(score, (1, score, rid), getitem)
                        for rid, score in rs.items()]

            rs = rs.byValue(0) # sort it by score
            max = float(rs[0][0])

            # Here we define our getter function inline so that
            # we can conveniently store the max value as a default arg
            # and make the normalized score computation lazy
            def getScoredResult(item, max=max, self=self):
                """
                Returns instances of self._v_brains, or whatever is passed
                into self.useBrains.
                """
                score, key = item
                r=self._v_result_class(self.data[key])\
                      .__of__(self.aq_parent)
                r.data_record_id_ = key
                r.data_record_score_ = score
                r.data_record_normalized_score_ = int(100. * score / max)
                return r

            return LazyMap(getScoredResult, rs, len(rs))

        elif sort_index is None and not hasattr(rs, 'values'):
            # no scores
            if hasattr(rs, 'keys'):
                rs = rs.keys()
            return LazyMap(self.__getitem__, rs, len(rs))
        else:
            # sort.  If there are scores, then this block is not
            # reached, therefore 'sort-on' does not happen in the
            # context of a text index query.  This should probably
            # sort by relevance first, then the 'sort-on' attribute.
            return self.sortResults(rs, sort_index, reverse, limit, merge)
    else:
        # Empty result set
        return LazyCat([])


def patch_catalog():
    from Products.ZCatalog.Catalog import Catalog
    Catalog.search = search
    logger.debug('Patched Catalog.search')

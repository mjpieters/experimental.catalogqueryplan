from BTrees.IIBTree import weightedIntersection

from Products.ZCatalog.Lazy import LazyMap, LazyCat

from logging import getLogger

logger = getLogger('experimental.catalogqueryplan')

ADVANCEDTYPES = []

def search(self, request, sort_index=None, reverse=0, limit=None, merge=1):
    advancedtypes = tuple(ADVANCEDTYPES)
    rs = None # resultset

    # Note that if the indexes find query arguments, but the end result
    # is an empty sequence, we do nothing
    
    prioritymap = getattr(self, '_v_prioritymap', None)
    if prioritymap is None:
        prioritymap = self._v_prioritymap = {}
    
    if isinstance(request, dict):
        keydict = request.copy()
    else:
        keydict = {}
        keydict.update(request.keywords)
        if isinstance(request.request, dict):
            keydict.update(request.request)
    key = tuple(sorted(keydict.keys()))
    indexes = prioritymap.get(key, [])
    if not indexes:
        pri = []
        for i in self.indexes.keys():
            index = self.getIndex(i)
            _apply_index = getattr(index, "_apply_index", None)
            if _apply_index is None:
                continue
            r = _apply_index(request)

            if r is not None:
                r, u = r
                pri.append((isinstance(index, advancedtypes), len(r), i))
                w, rs = weightedIntersection(rs, r)
        pri.sort()
        prioritymap[key] = [p[-1] for p in pri]

    else:
        for i in indexes:
            index = self.getIndex(i)
            _apply_index = getattr(index, "_apply_index", None)
            if _apply_index is None:
                continue
            if isinstance(index, advancedtypes):
                r = _apply_index(request, res=rs)
            else:
                r = _apply_index(request)

            if r is not None:
                # Short circuit if empty result
                r, u = r
                if not r:
                    return LazyCat([])
                w, rs = weightedIntersection(rs, r)

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

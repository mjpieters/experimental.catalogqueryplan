from Acquisition import aq_inner, aq_parent
from BTrees.IIBTree import multiunion
from BTrees.IIBTree import intersection
from BTrees.IIBTree import difference
from Products.PluginIndexes.common.util import parseIndexRequest
from experimental.catalogqueryplan.catalog import RequestCache

from logging import getLogger

logger = getLogger('experimental.catalogqueryplan')

def daterangeindex_apply_index(self, request, cid='', res=None):
    record = parseIndexRequest(request, self.getId())
    if record.keys is None:
        return None

    term = self._convertDateTime(record.keys[0])

    REQUEST = getattr(self, 'REQUEST', None)
    if REQUEST is not None:
        catalog = aq_parent(aq_parent(aq_inner(self)))
        if catalog is not None:
            key = '%s_%s'%(catalog.getId(), catalog.getCounter())
            cache = REQUEST.get(key, None)
            if res is None:
                cachekey = '_daterangeindex_%s_%s' % (self.getId(), term/10)
            else:
                cachekey = '_daterangeindex_inverse_%s_%s' % (self.getId(), term/10)
            if cache is None:
                cache = REQUEST[key] = RequestCache()
            else:
                cached = cache.get(cachekey, None)
                if cached is not None:
                    if res is None:
                        return cached, (self._since_field, self._until_field)
                    else:
                        return difference(res, cached), (self._since_field, self._until_field)

    if res is None:
        #
        #   Aggregate sets for each bucket separately, to avoid
        #   large-small union penalties.
        #   XXX Does this apply for multiunion?
        #
        until_only = multiunion(self._until_only.values(term))

        since_only = multiunion(self._since_only.values(None, term))

        until = multiunion(self._until.values(term))

        # Total result is bound by res
        if REQUEST is None:
            until = intersection(res, until)

        since = multiunion(self._since.values(None, term))

        bounded = intersection(until, since)

        result = multiunion([bounded, until_only, since_only, self._always])
        if REQUEST is not None and catalog is not None:
            cache[cachekey] = result

        return result, (self._since_field, self._until_field)
    else:
        # Compute the inverse and subtract from res
        until_only = multiunion(self._until_only.values(None,term))
        since_only = multiunion(self._since_only.values(term))
        until = multiunion(self._until.values(None,term))
        since = multiunion(self._since.values(term))
        result = multiunion([until_only,since_only,until,since])
        if REQUEST is not None and catalog is not None:
            cache[cachekey] = result
        return difference(res, result), (self._since_field, self._until_field)

def patch_daterangeindex():
    from Products.PluginIndexes.DateRangeIndex.DateRangeIndex import DateRangeIndex
    DateRangeIndex._apply_index = daterangeindex_apply_index

    from catalog import ADVANCEDTYPES
    ADVANCEDTYPES.append(DateRangeIndex)
    logger.debug('Patched DateRangeIndex._apply_index')

from BTrees.IIBTree import multiunion
from BTrees.IIBTree import intersection
from Products.PluginIndexes.common.util import parseIndexRequest

from logging import getLogger

logger = getLogger('experimental.catalogqueryplan')

def daterangeindex_apply_index( self, request, cid='', res=None):
    record = parseIndexRequest( request, self.getId() )
    if record.keys is None:
        return None

    REQUEST = getattr(self, 'REQUEST', None)
    if REQUEST is not None:
        requestkey = '_daterangeindex_%s' % self.getId()
        cached = REQUEST.get(requestkey, None)
        if cached is not None:
            return cached, ( self._since_field, self._until_field )

    term        = self._convertDateTime( record.keys[0] )

    #
    #   Aggregate sets for each bucket separately, to avoid
    #   large-small union penalties.
    #   XXX Does this apply for multiunion?
    #
    until_only = multiunion( self._until_only.values( term ) )

    since_only = multiunion( self._since_only.values( None, term ) )

    until = multiunion( self._until.values( term ) )

    # Total result is bound by res
    if REQUEST is None:
        until = intersection(res, until)

    since = multiunion( self._since.values( None, term ) )

    bounded     = intersection( until, since )

    result = multiunion([bounded, until_only, since_only, self._always])

    if REQUEST is not None:
        REQUEST.set(requestkey, result)

    return result, ( self._since_field, self._until_field )

def patch_daterangeindex():
    from Products.PluginIndexes.DateRangeIndex.DateRangeIndex import DateRangeIndex
    DateRangeIndex._apply_index = daterangeindex_apply_index

    from catalog import ADVANCEDTYPES
    ADVANCEDTYPES.append(DateRangeIndex)
    logger.info('Patched DateRangeIndex._apply_index')

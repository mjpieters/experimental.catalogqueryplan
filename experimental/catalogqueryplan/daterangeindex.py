from BTrees.IIBTree import multiunion, intersection
from Products.PluginIndexes.common.util import parseIndexRequest


def daterangeindex_apply_index( self, request, cid='', res=None):
    record = parseIndexRequest( request, self.getId() )
    if record.keys is None:
        return None

    REQUEST = getattr(self, 'REQUEST', None)
    if REQUEST is not None:
        requestkey = '_daterangeindex_%s' % self.getId()
        cached = REQUEST.get(requestkey, None)
        if cached is not None:
            return intersection(res, cached), ( self._since_field, self._until_field )

    term        = self._convertDateTime( record.keys[0] )

    #
    #   Aggregate sets for each bucket separately, to avoid
    #   large-small union penalties.
    #
    #until_only  = IISet()
    #map( until_only.update, self._until_only.values( term ) )
    # XXX use multi-union
    until_only = multiunion( self._until_only.values( term ) )

    #since_only  = IISet()
    #map( since_only.update, self._since_only.values( None, term ) )
    # XXX use multi-union
    since_only = multiunion( self._since_only.values( None, term ) )

    #until       = IISet()
    #map( until.update, self._until.values( term ) )
    # XXX use multi-union
    until = multiunion( self._until.values( term ) )

    # Total result is bound by res
    if REQUEST is None:
        until = intersection(res, until)

    #since       = IISet()
    #map( since.update, self._since.values( None, term ) )
    # XXX use multi-union
    since = multiunion( self._since.values( None, term ) )

    bounded     = intersection( until, since )

    #   Merge from smallest to largest.
    #result      = union( bounded, until_only )
    #result      = union( result, since_only )
    #result      = union( result, self._always )
    result = multiunion([bounded, until_only, since_only, self._always])

    if REQUEST is not None:
        REQUEST.set(requestkey, result)
        result = intersection(res, result)

    return result, ( self._since_field, self._until_field )

def patch_daterangeindex():
    from Products.PluginIndexes.DateRangeIndex.DateRangeIndex import DateRangeIndex
    DateRangeIndex._apply_index = daterangeindex_apply_index

    from catalog import ADVANCEDTYPES
    ADVANCEDTYPES.append(DateRangeIndex)

from BTrees.IIBTree import union, multiunion
from BTrees.IIBTree import intersection
from Products.PluginIndexes.common.util import parseIndexRequest
from BTrees.IIBTree import IISet

from logging import getLogger

logger = getLogger('experimental.catalogqueryplan')

def dateindex_apply_index( self, request, cid='', type=type, res=None):
    record = parseIndexRequest( request, self.id, self.query_options )
    if record.keys == None:
        return None

    keys = map( self._convert, record.keys )

    index = self._index
    r = None
    opr = None

    #experimental code for specifing the operator
    operator = record.get( 'operator', self.useOperator )
    if not operator in self.operators :
        raise RuntimeError, "operator not valid: %s" % operator

    # depending on the operator we use intersection or union
    if operator=="or":
        set_func = union
    else:
        set_func = intersection

    # range parameter
    range_arg = record.get('range',None)
    if range_arg:
        opr = "range"
        opr_args = []
        if range_arg.find("min") > -1:
            opr_args.append("min")
        if range_arg.find("max") > -1:
            opr_args.append("max")

    if record.get('usage',None):
        # see if any usage params are sent to field
        opr = record.usage.lower().split(':')
        opr, opr_args = opr[0], opr[1:]

    if opr=="range":   # range search
        if 'min' in opr_args:
            lo = min(keys)
        else:
            lo = None

        if 'max' in opr_args:
            hi = max(keys)
        else:
            hi = None

        if hi:
            setlist = index.values(lo,hi)
        else:
            setlist = index.values(lo)

        #for k, set in setlist:
            #if type(set) is IntType:
                #set = IISet((set,))
            #r = set_func(r, set)
        # XXX: Use multiunion!
        r = multiunion(setlist)

    else: # not a range search
        for key in keys:
            set = index.get(key, None)
            if set is not None:
                if isinstance(set, int):
                    set = IISet((set,))
                else:
                    # set can't be bigger than res
                    set = intersection(set, res)
                r = set_func(r, set)

    if isinstance(r, int):
        r = IISet((r,))

    if r is None:
        return IISet(), (self.id,)
    else:
        return r, (self.id,)

def patch_dateindex():
    from Products.PluginIndexes.DateIndex.DateIndex import DateIndex
    DateIndex._apply_index = dateindex_apply_index

    from catalog import ADVANCEDTYPES
    ADVANCEDTYPES.append(DateIndex)
    logger.debug('Patched DateIndex._apply_index')

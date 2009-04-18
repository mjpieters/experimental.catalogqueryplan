from cgi import escape
from BTrees.IIBTree import union, multiunion
from BTrees.IIBTree import intersection
from Products.PluginIndexes.common.util import parseIndexRequest
from BTrees.IIBTree import IISet

from logging import getLogger

logger = getLogger('experimental.catalogqueryplan')

def unindex_apply_index(self, request, cid='', type=type, res=None):
    record = parseIndexRequest(request, self.id, self.query_options)
    if record.keys==None: return None

    index = self._index
    r     = None
    opr   = None

    # experimental code for specifing the operator
    operator = record.get('operator',self.useOperator)
    if not operator in self.operators :
        raise RuntimeError,"operator not valid: %s" % escape(operator)

    # depending on the operator we use intersection or union
    if operator=="or":  set_func = union
    else:               set_func = intersection

    # Range parameter
    range_parm = record.get('range',None)
    if range_parm:
        opr = "range"
        opr_args = []
        if range_parm.find("min")>-1:
            opr_args.append("min")
        if range_parm.find("max")>-1:
            opr_args.append("max")

    if record.get('usage',None):
        # see if any usage params are sent to field
        opr = record.usage.lower().split(':')
        opr, opr_args=opr[0], opr[1:]

    if opr=="range":   # range search
        if 'min' in opr_args: lo = min(record.keys)
        else: lo = None
        if 'max' in opr_args: hi = max(record.keys)
        else: hi = None
        if hi:
            setlist = index.values(lo,hi)
        else:
            setlist = index.values(lo)


        # If we only use 1 key (default setting), intersect and return immediately
        if len(setlist) == 1:
            result = setlist[0]
            if isinstance(result, int):
                result = IISet((result,))
            return result, (self.id,)

        if operator == 'or':
            r = multiunion(setlist)
        else:
            # For intersection, sort with smallest data set first
            tmp = []
            for s in setlist:
                if isinstance(s, int):
                    s = IISet((s,))
                tmp.append(s)
            if len(tmp) > 2:
                setlist = sorted(tmp, key=len)
            else:
                setlist = tmp
            r = res
            for s in setlist:
                r = intersection(r, s)

    else: # not a range search
        # Filter duplicates, and sort by length
        keys = set(record.keys)
        setlist = []
        for k in keys:
            s = index.get(k, None)
            # If None, try to bail early
            if s is None:
                if operator == 'or':
                    # If union, we can't possibly get a bigger result
                    continue
                # If intersection, we can't possibly get a smaller result
                return IISet(), (self.id,)
            elif isinstance(s, int):
                s = IISet((s,))
            setlist.append(s)

        # If we only use 1 key (default setting), intersect and return immediately
        if len(setlist) == 1:
            result = setlist[0]
            if isinstance(result, int):
                result = IISet((result,))
            return result, (self.id,)

        if operator == 'or':
            # If we already get a small result set passed in, intersecting
            # the various indexes with it and doing the union later is faster
            # than creating a multiunion first.
            if res is not None and len(res) < 200:
                smalllist = []
                for s in setlist:
                    smalllist.append(intersection(res, s))
                r = multiunion(smalllist)
            else:
                r = multiunion(setlist)
        else:
            # For intersection, sort with smallest data set first
            if len(setlist) > 2:
                setlist = sorted(setlist, key=len)
            r = res
            for s in setlist:
                r = intersection(r, s)

    if isinstance(r, int):  r=IISet((r,))
    if r is None:
        return IISet(), (self.id,)
    else:
        return r, (self.id,)

def patch_unindex():
    from Products.PluginIndexes.common.UnIndex import UnIndex
    UnIndex._apply_index = unindex_apply_index
    logger.debug('Patched UnIndex._apply_index')

    from catalog import ADVANCEDTYPES, VALUETYPES
    from Products.PluginIndexes.FieldIndex.FieldIndex import FieldIndex
    ADVANCEDTYPES.append(FieldIndex)
    VALUETYPES.append(FieldIndex)
    from Products.PluginIndexes.KeywordIndex.KeywordIndex import KeywordIndex
    ADVANCEDTYPES.append(KeywordIndex)
    VALUETYPES.append(KeywordIndex)

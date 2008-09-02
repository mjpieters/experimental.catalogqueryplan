from cgi import escape
from BTrees.IIBTree import union, intersection
from Products.PluginIndexes.common.util import parseIndexRequest
from BTrees.IIBTree import IISet


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
            setlist = index.items(lo,hi)
        else:
            setlist = index.items(lo)

        for k, set in setlist:
            if isinstance(set, int):
                set = IISet((set,))
            # set can't be bigger than res
            set = intersection(set, res)
            r = set_func(r, set)
    else: # not a range search
        for key in record.keys:
            set=index.get(key, None)
            if set is None:
                set = IISet(())
            elif isinstance(set, int):
                set = IISet((set,))
            # set can't be bigger than res
            set = intersection(set, res)
            r = set_func(r, set)

    if isinstance(r, int):  r=IISet((r,))
    if r is None:
        return IISet(), (self.id,)
    else:
        return r, (self.id,)

def patch_unindex():
    from Products.PluginIndexes.common.UnIndex import UnIndex
    UnIndex._apply_index = unindex_apply_index

    from catalog import ADVANCEDTYPES
    from Products.PluginIndexes.FieldIndex.FieldIndex import FieldIndex
    ADVANCEDTYPES.append(FieldIndex)
    from Products.PluginIndexes.KeywordIndex.KeywordIndex import KeywordIndex
    ADVANCEDTYPES.append(KeywordIndex)

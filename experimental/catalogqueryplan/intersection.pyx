DEF SMALLSETSIZE = 1000
DEF BIGSMALLRATIO = 20

from cpython cimport bool
from BTrees._IIBTree import intersection as iiintersection
from BTrees._IIBTree import IISet

cpdef object ciiintersection(object o1, object o2):
    if o1 is None:
        return o2
    if o2 is None:
        return o1

    if not o2 or not o1:
        return iiintersection(o1, o2)

    cdef bool s1, s2
    cdef object small, big, new, ins, has

    s1 = type(o1) is IISet
    s2 = type(o2) is IISet

    if s1 and s2:
        return iiintersection(o1, o2)
    elif s1 or s2:
        # Only do this if one of them is a set, we are slower at treesets.
        # We don't check the size of the treeset, so we sometimes loop over
        # a very small one, but there's no way to tell, without loading it.

        if s1 and len(o1) < SMALLSETSIZE:
            small = o1
            big = o2
        elif s2 and len(o2) < SMALLSETSIZE:
            small = o2
            big = o1
        else:
            return iiintersection(o1, o2)

        new = IISet()
        ins = new.insert
        has = big.has_key
        for i in small:
            if has(i):
                ins(i)
        return new
    return iiintersection(o1, o2)

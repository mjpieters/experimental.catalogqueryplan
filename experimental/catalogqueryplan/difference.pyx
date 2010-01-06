DEF SMALLSETSIZE = 1000
DEF BIGSMALLRATIO = 20

from BTrees._IIBTree import difference as iidifference
from BTrees._IIBTree import IISet

cpdef object ciidifference(object o1, object o2):
    # Bail out as soon as possible if one or both are None
    if not o1 or not o2:
        return iidifference(o1, o2)

    cdef int l1, l2, i
    cdef object new, ins, has

    # Both are real sets, of unknown size
    l1 = len(o1)

    # Difference returns bucket if o1 is btree
    if l1 < SMALLSETSIZE and isinstance(o1, IISet):
        l2 = len(o2)
        if l2/l1 > BIGSMALLRATIO:
            new = IISet()
            ins = new.insert
            has = o2.has_key
            for i in o1:
                if not has(i):
                    ins(i)
            return new

    return iidifference(o1, o2)

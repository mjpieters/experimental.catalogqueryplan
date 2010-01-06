DEF SMALLSETSIZE = 1000
DEF BIGSMALLRATIO = 20


cdef object cdifference(object o1, object o2, settype, setdifference):
    # Bail out as soon as possible if one or both are None
    if not o1 or not o2:
        return setdifference(o1, o2)

    cdef int l1, l2
    cdef object i, new, ins, has

    # Both are real sets, of unknown size
    l1 = len(o1)

    # Difference returns bucket if o1 is btree
    if l1 < SMALLSETSIZE and isinstance(o1, settype):
        l2 = len(o2)
        if l2/l1 > BIGSMALLRATIO:
            new = settype()
            ins = new.insert
            has = o2.has_key
            for i in o1:
                if not has(i):
                    ins(i)
            return new

    return setdifference(o1, o2)

from BTrees._IIBTree import difference as iidifference
from BTrees._IIBTree import IISet

cpdef object ciidifference(object o1, object o2):
    return cdifference(o1, o2, IISet, iidifference)

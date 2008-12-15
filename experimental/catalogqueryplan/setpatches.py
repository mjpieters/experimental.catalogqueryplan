SMALLSETSIZE = 200
BIGSMALLRATIO = 20
def patch_intersection(treetype, settype):

    setintersection = treetype.intersection

    def intersection(o1, o2):
        # Bail out as soon as possible if one or both are None
        if o1 is None:
            if o2 is None:
                return None
            return o2
        if o2 is None:
            return o1

        # Both are real sets, of unknown size
        l1 = len(o1)
        # If empty set, return
        if l1 == 0:
            return o1

        l2 = len(o2)
        if l2 == 0:
            return o2
        elif l1 == l2:
            return setintersection(o1, o2)

        if l1 < l2:
            ls = l1
            small = o1
            lb = l2
            big = o2
        else:
            ls = l2
            small = o2
            lb = l1
            big = o1

        if ls < SMALLSETSIZE and lb/ls > BIGSMALLRATIO:
            new = settype()
            for i in small:
                if big.has_key(i):
                    new.insert(i)
            #print '% 10d  % 10d %s' % (ls, lb, new)
            return new

        return setintersection(o1, o2)

    treetype._old_intersection = treetype.intersection
    treetype.intersection = intersection


def patch_difference(treetype, settype):

    setdifference = treetype.difference

    def difference(o1, o2):
        # Bail out as soon as possible if one or both are None
        if not o1:
            return o1
        if not o2:
            return o1
        # Both are real sets, of unknown size
        l1 = len(o1)
        if l1 < SMALLSETSIZE:
            l2 = len(o2)
            if l2/l1 > BIGSMALLRATIO:
                new = settype()
                for i in o1:
                    if not o2.has_key(i):
                        new.insert(i)
                #print '% 10d  % 10d %s' % (ls, lb, new)
                return new

        return setdifference(o1, o2)

    treetype._old_difference = treetype.difference
    treetype.difference = difference


def apply():
    from BTrees.IIBTree  import IISet
    from BTrees import IIBTree
    patch_intersection(IIBTree, IISet)
    patch_difference(IIBTree, IISet)

    from BTrees.IOBTree  import IOSet
    from BTrees import IOBTree
    patch_intersection(IOBTree, IOSet)
    patch_difference(IOBTree, IOSet)

    from BTrees.OIBTree  import OISet
    from BTrees import OIBTree
    patch_intersection(OIBTree, OISet)
    patch_difference(OIBTree, OISet)

    from BTrees.OOBTree  import OOSet
    from BTrees import OOBTree
    patch_intersection(OOBTree, OOSet)
    patch_difference(OOBTree, OOSet)

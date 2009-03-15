from BTrees.IIBTree import union, multiunion
from BTrees.IIBTree import intersection
from Products.PluginIndexes.common.util import parseIndexRequest
from BTrees.IIBTree import IISet

from logging import getLogger

logger = getLogger('experimental.catalogqueryplan')

def extendedpathindex_apply_index(self, request, res=None):
    """ hook for (Z)Catalog
        'request' --  mapping type (usually {"path": "..." }
         additionaly a parameter "path_level" might be passed
         to specify the level (see search())
    """

    record = parseIndexRequest(request,self.id,self.query_options)
    if record.keys==None: return None

    level    = record.get("level", 0)
    operator = record.get('operator', self.useOperator).lower()
    depth    = getattr(record, 'depth', -1) # use getattr to get 0 value
    navtree  = record.get('navtree', 0)
    navtree_start  = record.get('navtree_start', 0)

    # depending on the operator we use intersection of union
    if operator == "or":  set_func = union
    else: set_func = intersection

    result = None
    for k in record.keys:
        rows = self.search(k,level, depth, navtree, navtree_start, tmpres=res)
        result = set_func(result,rows)

    if result:
        return result, (self.id,)
    else:
        return IISet(), (self.id,)


def extendedpathindex_search(self, path, default_level=0, depth=-1, navtree=0,
           navtree_start=0, tmpres=None):
    """
    path is either a string representing a
    relative URL or a part of a relative URL or
    a tuple (path,level).
    
    default_level specifies the level to use when no more specific
    level has been passed in with the path.

    level >= 0  starts searching at the given level
    level <  0  finds matches at *any* level
    
    depth let's you limit the results to items at most depth levels deeper
    than the matched path. depth == 0 means no subitems are included at all,
    with depth == 1 only direct children are included, etc. depth == -1, the
    default, returns all children at any depth.
    
    navtree is treated as a boolean; if it evaluates to True, not only the
    query match is returned, but also each container in the path. If depth
    is greater than 0, also all siblings of those containers, as well as the
    siblings of the match are included as well, plus *all* documents at the
    starting level.
    
    navtree_start limits what containers are included in a navtree search.
    If greater than 0, only containers (and possibly their siblings) at that
    level and up will be included in the resultset.

    """
    if isinstance(path, basestring):
        level = default_level
    else:
        level = int(path[1])
        path = path[0]

    if level < 0:
        # Search at every level, return the union of all results
        return multiunion(
            [self.search(path, level, depth, navtree, navtree_start)
             for level in xrange(self._depth + 1)])

    comps = filter(None, path.split('/'))

    if navtree and depth == -1: # Navtrees don't do recursive
        depth = 1

    #
    # Optimisations
    #
    
    pathlength = level + len(comps) - 1
    if navtree and navtree_start > min(pathlength + depth, self._depth):
        # This navtree_start excludes all items that match the depth
        return IISet()
    if pathlength > self._depth:
        # Our search is for a path longer than anything in the index
        return IISet()

    if level == 0 and depth in (0, 1):
        # We have easy indexes for absolute paths where
        # we are looking for depth 0 or 1 result sets
        if navtree:
            # Optimized absolute path navtree and breadcrumbs cases
            result = []
            add = lambda x: x is not None and result.append(x)
            if depth == 1:
                # Navtree case, all sibling elements along the path
                convert = multiunion
                index = self._index_parents
            else:
                # Breadcrumbs case, all direct elements along the path
                convert = IISet
                index = self._index_items
            # Collect all results along the path
            for i in range(len(comps), navtree_start - 1, -1):
                parent_path = '/' + '/'.join(comps[:i])
                add(index.get(parent_path))
            return convert(result)
        
        if not path.startswith('/'):
            path = '/' + path
        if depth == 0:
            # Specific object search
            res = self._index_items.get(path)
            return res and IISet([res]) or IISet()
        else:
            # Single depth search
            return self._index_parents.get(path, IISet())
    
    # Avoid using the root set
    # as it is common for all objects anyway and add overhead
    # There is an assumption about all indexed values having the
    # same common base path
    if level == 0:
        indexpath = list(filter(None, self.getPhysicalPath()))
        minlength = min(len(indexpath), len(comps))
        # Truncate path to first different element
        for i in xrange(minlength):
            if indexpath[i] != comps[i]:
                break
            level += 1
        comps = comps[level:]

    if not comps and depth == -1:
        # Recursive search for everything
        return IISet(self._unindex)
    
    #
    # Core application of the indexes
    #

    pathset  = tmpres # Same as pathindex
    depthset = None # For limiting depth

    if navtree and depth > 0:
        # Include the elements up to the matching path
        depthset = multiunion([
            self._index.get(None, {}).get(i, IISet())
            for i in range(min(navtree_start, level), 
                           max(navtree_start, level) + 1)])
    
    indexedcomps = enumerate(comps)
    if not navtree:
        # Optimize relative-path searches by starting with the
        # presumed smaller sets at the end of the path first
        # We can't do this for the navtree case because it needs
        # the bigger rootset to include siblings along the way.
        indexedcomps = list(indexedcomps)
        indexedcomps.reverse()
    
    for i, comp in indexedcomps:
        # Find all paths that have comp at the given level
        res = self._index.get(comp, {}).get(i + level)
        if res is None: # Non-existing path; navtree is inverse, keep going
            pathset = IISet()
            if not navtree: return pathset
        pathset = intersection(pathset, res)
        
        if navtree and i + level >= navtree_start:
            depthset = union(depthset, intersection(pathset,
                self._index.get(None, {}).get(i + level)))
    
    if depth >= 0:
        # Limit results to those that terminate within depth levels
        start = len(comps) - 1
        if navtree: start = max(start, (navtree_start - level))
        depthset = multiunion(filter(None, [depthset] + [
            intersection(pathset, self._index.get(None, {}).get(i + level))
            for i in xrange(start, start + depth + 1)]))

    if navtree or depth >= 0: return depthset
    return pathset


def patch_extendedpathindex():
    pass
    try:
        from Products.ExtendedPathIndex.ExtendedPathIndex import ExtendedPathIndex
        ExtendedPathIndex._apply_index = extendedpathindex_apply_index
        logger.debug('Patched ExtendedPathIndex._apply_index')
        ExtendedPathIndex.search = extendedpathindex_search
        logger.debug('Patched ExtendedPathIndex.search')

        from catalog import ADVANCEDTYPES
        ADVANCEDTYPES.append(ExtendedPathIndex)
    except ImportError:
        pass

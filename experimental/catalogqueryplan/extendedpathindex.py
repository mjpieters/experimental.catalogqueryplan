from BTrees.IIBTree import union, multiunion, intersection
from Products.PluginIndexes.common.util import parseIndexRequest
from BTrees.IIBTree import IISet

def extendedpathindex_apply_index(self, request, cid='', res=None):
    """ hook for (Z)Catalog
        'request' --  mapping type (usually {"path": "..." }
         additionaly a parameter "path_level" might be passed
         to specify the level (see search())

        'cid' -- ???
    """

    record = parseIndexRequest(request,self.id,self.query_options)
    if record.keys==None: return None

    level    = record.get("level", 0)
    operator = record.get('operator', self.useOperator).lower()
    depth    = getattr(record, 'depth', -1) # Set to 0 or navtree later
                                            # use getattr to get 0 value
    navtree  = record.get('navtree', 0)
    navtree_start  = record.get('navtree_start', 0)

    # depending on the operator we use intersection of union
    if operator == "or":  set_func = union
    else: set_func = intersection

    result = None
    for k in record.keys:
        rows = self.search(k,level, depth, navtree, navtree_start, res=res)
        result = set_func(result,rows)

    if result:
        return result, (self.id,)
    else:
        return IISet(), (self.id,)


def extendedpathindex_search(self, path, default_level=0, depth=-1, navtree=0,
                                                         navtree_start=0, res=None):
    """
    path is either a string representing a
    relative URL or a part of a relative URL or
    a tuple (path,level).

    level >= 0  starts searching at the given level
    level <  0  not implemented yet
    """

    if isinstance(path, basestring):
        startlevel = default_level
    else:
        startlevel = int(path[1])
        path = path[0]

    absolute_path = isinstance(path, basestring) and path.startswith('/')

    comps = filter(None, path.split('/'))

    orig_comps = [''] + comps[:]
    # Optimization - avoid using the root set
    # as it is common for all objects anyway and add overhead
    # There is an assumption about catalog/index having
    # the same container as content
    if default_level == 0:
        indexpath = list(filter(None, self.getPhysicalPath()))
        while min(len(indexpath), len(comps)):
            if indexpath[0] == comps[0]:
                del indexpath[0]
                del comps[0]
                startlevel += 1
            else:
                break

    if len(comps) == 0:
        if depth == -1 and not navtree:
            return IISet(self._unindex.keys())

    # Make sure that we get depth = 1 if in navtree mode
    # unless specified otherwise

    orig_depth = depth
    if depth == -1:
        depth = 0 or navtree

    # Optimized navtree starting with absolute path
    if absolute_path and navtree and depth == 1 and default_level==0:
        set_list = []
        # Insert root element
        if navtree_start >= len(orig_comps):
            navtree_start = 0
        # create a set of parent paths to search
        for i in range(len(orig_comps), navtree_start, -1):
            parent_path = '/'.join(orig_comps[:i])
            parent_path = parent_path and parent_path or '/'
            try:
                set_list.append(self._index_parents[parent_path])
            except KeyError:
                pass
        return multiunion(set_list)
    # Optimized breadcrumbs
    elif absolute_path and navtree and depth == 0 and default_level==0:
        item_list = IISet()
        # Insert root element
        if navtree_start >= len(orig_comps):
            navtree_start = 0
        # create a set of parent paths to search
        for i in range(len(orig_comps), navtree_start, -1):
            parent_path = '/'.join(orig_comps[:i])
            parent_path = parent_path and parent_path or '/'
            try:
                item_list.insert(self._index_items[parent_path])
            except KeyError:
                pass
        return item_list
    # Specific object search
    elif absolute_path and orig_depth == 0 and default_level == 0:
        try:
            return IISet([self._index_items[path]])
        except KeyError:
            return IISet()
    # Single depth search
    elif absolute_path and orig_depth == 1 and default_level == 0:
        # only get objects contained in requested folder
        try:
            return self._index_parents[path]
        except KeyError:
            return IISet()
    # Sitemaps, relative paths, and depth queries
    elif startlevel >= 0:

        pathset = res # Same as pathindex, None or bound by existing result
        navset  = None # For collecting siblings along the way
        depthset = None # For limiting depth

        if navtree and depth and \
               self._index.has_key(None) and \
               self._index[None].has_key(startlevel):
            navset = self._index[None][startlevel]

        for level in range(startlevel, startlevel+len(comps) + depth):
            if level-startlevel < len(comps):
                comp = comps[level-startlevel]
                if not self._index.has_key(comp) or not self._index[comp].has_key(level): 
                    # Navtree is inverse, keep going even for
                    # nonexisting paths
                    if navtree:
                        pathset = IISet()
                    else:
                        return IISet()
                else:
                    pathset = intersection(pathset,
                                                 self._index[comp][level])
                if navtree and depth and \
                       self._index.has_key(None) and \
                       self._index[None].has_key(level+depth):
                    navset  = union(navset, intersection(pathset,
                                          self._index[None][level+depth]))
            if level-startlevel >= len(comps) or navtree:
                if self._index.has_key(None) and self._index[None].has_key(level):
                    depthset = union(depthset, intersection(pathset,
                                                self._index[None][level]))

        if navtree:
            return union(depthset, navset) or IISet()
        elif depth:
            return depthset or IISet()
        else:
            return pathset or IISet()

    else:
        results = IISet()
        for level in range(0,self._depth + 1):
            ids = None
            error = 0
            for cn in range(0,len(comps)):
                comp = comps[cn]
                try:
                    ids = intersection(ids,self._index[comp][level+cn])
                except KeyError:
                    error = 1
            if error==0:
                results = union(results,ids)
        return results


def patch_extendedpathindex():
    try:
        from Products.ExtendedPathIndex.ExtendedPathIndex import ExtendedPathIndex
        ExtendedPathIndex._apply_index = extendedpathindex_apply_index
        ExtendedPathIndex.search = extendedpathindex_search

        from catalog import ADVANCEDTYPES
        ADVANCEDTYPES.append(ExtendedPathIndex)
    except ImportError:
        pass

from BTrees.IIBTree import IISet
from BTrees.IIBTree import union as ii_union
from BTrees.OOBTree import OOSet
from BTrees.OOBTree import union as oo_union
from Products.PluginIndexes.common.util import parseIndexRequest

# Conditional import to avoid hard dependency
try:
    from Products.LinguaPlone.utils import splitLanguage
except ImportError:
    pass

from logging import getLogger

logger = getLogger('experimental.catalogqueryplan')


def lang_tag(main, sub):
    return '-'.join(filter(None, (main, sub)))


def languageindex_apply_index(self, request, cid='', res=None):
    """Apply the index to the search parameters given in request"""

    record = parseIndexRequest(request, self.id, self.query_options)
    if record.keys is None:
        return None

    result = None
    fallback = self.fallback
    if hasattr(record, 'fallback'):
        fallback = bool(record.fallback)

    # TODO: This could be optimized to avoid a loop per language
    # As we most often get a language code and '' for language neutral this
    # could be beneficial. If the site has no language neutral content, the
    # first check "main not in self._index" will return None. The union of
    # None with the resultset is a cheap call, so we don't care right now.
    for language in record.keys:
        rows = self._search(language, fallback, res=res)
        result = ii_union(result, rows)

    return (result or IISet()), ('Language',)


def languageindex_search(self, language, fallback=True, res=None):
    main, sub = splitLanguage(language)

    if main not in self._index:
        return None

    if fallback:
        # Search in sorted order, specific sub tag first, None second
        subs = list(self._index[main].keys())
        subs.sort()
        if sub in subs:
            subs.remove(sub)
            subs.insert(0, sub)
    else:
        subs = [sub]

    if not fallback and res is not None:
        # We do not support any optimization when fallback is enabled.
        #
        # TODO: The core loop is not in C here. Casual benchmarks suggest this
        # is still more effecient than trying to move it to C. The problem is
        # that we only have an IISet of docids as an input. We need to filter
        # this per language. The available index structures we have are:
        #
        # IndexEntry objects used as entries. Complex objects storing docid,
        # main and sub languages and UID of the canonical. Their hash and
        # compare function uses the canonical UID.
        #
        # self._index
        # An OOBTreeSet structure per language. In the outermost nodes we have
        # OOBTree's per language. Useful to get all items in a language.
        # Otherwise useless, as we would have to compare the docid attribute
        # of the object in the tree against our wanted set, requiring a full
        # loop over all items.
        #
        # self._unindex
        # An IOBTree of docid to entry. Better to match our docid wanted set,
        # but we would still have to compare the language code to the entry
        # object itself.
        #
        # self._sortindex
        # An IOBTree of docid to language tag. Looks like the best candidate
        # for us, as we can compare the language directly as a simple string
        # comparision.
        #
        # One thing to keep in mind, is that once we get a wanted set, this
        # will usually have gone through a path query already. This means
        # we will almost always already have matching set and won't filter
        # out any item at all. So the edge-case of a 100% match is actually
        # the most common one for us.
        #
        # Casual benchmarks show that trying to construct an IOBTree from the
        # wanted set and intersecting it with the sortindex is still slower
        # than having the core loop in Python code.
        tag = lang_tag(main, sub)

        result = IISet()
        for r in res:
            lang = self._sortindex.get(r)
            if lang == tag:
                result.insert(r)
        return result

    result = OOSet()
    for sublanguage in subs:
        result = oo_union(result, self._index[main][sublanguage])

    return IISet(entry.docid for entry in result)


def patch_languageindex():
    try:
        from Products.LinguaPlone.LanguageIndex import LanguageIndex
        LanguageIndex._apply_index = languageindex_apply_index
        logger.debug('Patched LanguageIndex._apply_index')
        LanguageIndex._search = languageindex_search
        logger.debug('Patched LanguageIndex.search')

        from catalog import ADVANCEDTYPES
        ADVANCEDTYPES.append(LanguageIndex)
    except ImportError:
        pass

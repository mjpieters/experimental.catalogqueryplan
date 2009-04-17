Introduction
============

While the catalog tool in Zope is immensely useful, we have seen some slowdowns
in large Plone sites with a combination of additional indexes and lots of
content.

The catalog implementation is using BTree set operations like union, multiunion
and intersection. Those operations are fairly fast, especially when everything
is in memory. However, the catalog implementation is rather naive which leads
to lots of set operations on rather big sets.

Query plan
==========

Search engines and databases uses query optimizers to select query plans that
will minimize the result set as early as possible, because working with large
amounts of data is time consuming.

What we want to do is to search against the indexes giving the smallest result
set first. However, for that to be useful, we need to pass that result along
into the indexes to allow the indexes to limit the result set as soon as
possible internally. When calculating a path search, there is no need to look
in all 150000 results if the portal type index has already limited the possible
result to 10000. If we have already limited the result to 10000 results, all
set operations are going to be significantly faster.

We identify different searches by the list of indexes that are searched. If
there are no query plans for a set of indexes, the query is run like normal
while storing the number of results for each index. When all indexes have been
checked, the list is sorted on number of results and stored as a query
plan. Next time a search on the same indexes comes in, the query plan is
looked up.

To get different query plans for similar queries, you can provide additional
bogus index names. They will be ignored by the catalog, but will become part of
the key. For indexes that have only a small number of distinct values the
query value will become part of the key as well. These type of indexes often
have an uneven distribution of indexed keys to values. For example there might
be very few `pending` documents in a site, but many `published` ones.


Testing
=======

To test, import the monkey patch in other tests, like CMFPlone::

 import experimental.catalogqueryplan

and run the test.

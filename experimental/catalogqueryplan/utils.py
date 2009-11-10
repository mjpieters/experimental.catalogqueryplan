from zope.dottedname.resolve import resolve
from logging import getLogger
from os import environ


logger = getLogger('catalogqueryplan')


def loadPriorityMap():
    location = environ.get('CATALOGQUERYPLAN')
    if location:
        try:
            pmap = resolve(location)
            logger.info('loaded priority %d map(s) from %s',
                len(pmap), location)
            return pmap
        except ImportError:
            logger.warning('could not load priority map from %s', location)

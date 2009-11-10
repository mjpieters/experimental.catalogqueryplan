from zope.dottedname.resolve import resolve
from logging import getLogger
from os import environ


def loadPriorityMap():
    location = environ.get('CATALOGQUERYPLAN')
    if location:
        try:
            return resolve(location)
        except ImportError:
            log = getLogger('catalogqueryplan').warning
            log('could not load priority map from %s', location)

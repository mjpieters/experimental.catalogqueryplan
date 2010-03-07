from Products.Five.browser import BrowserView
from Products.ZCatalog.interfaces import IZCatalog
from StringIO import StringIO
from time import asctime


class Views(BrowserView):
    """ helper view for dumping the priority map as a python dict """

    def prioritymap(self):
        output = StringIO()
        print >> output, '# query plan dumped at %r\n' % asctime()
        print >> output, 'queryplan = {'
        for obj in self.context.objectValues():
            if IZCatalog.providedBy(obj):
                identifier = '/'.join(obj.getPhysicalPath())
                data = getattr(obj._catalog, '_v_prioritymap', None)
                if data:
                    print >> output, '  %r: {' % identifier
                    for item in sorted(data.items()):
                        print >> output, '    %s:\n      %r,' % item
                    print >> output, '  },'
                data = getattr(obj._catalog, '_v_valueindexes', None)
                # TODO: Instead of trusting the simple algorithm, we could do
                # some more expensive calculation here and actually check if
                # the proposed indexes have an uneven value distribution
                if data:
                    print >> output, "  '%s:valueindexes': frozenset([" % identifier
                    for item in sorted(data):
                        print >> output, '    %r,' % item
                    print >> output, '  ]),'
        print >> output, '}\n'
        return output.getvalue()

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
                data = getattr(obj._catalog, '_v_prioritymap', None)
                if data:
                    identifier = '/'.join(obj.getPhysicalPath())
                    print >> output, '  %r: {' % identifier
                    for item in sorted(data.items()):
                        print >> output, '    %s:\n      %r,' % item
                    print >> output, '  },'
        print >> output, '}\n'
        return output.getvalue()

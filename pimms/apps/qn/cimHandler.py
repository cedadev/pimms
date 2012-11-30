from lxml import etree as ET

from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.core.urlresolvers import reverse

from pimms.apps.qn.webui.cimHandling import viewer
from pimms.apps.qn.webui.models import Simulation
from pimms.apps.qn.webui.models import Component
from pimms.apps.qn.vocabs import model_list


def commonURLs(obj, dictionary):
    '''
    Add urls for the common methods to a dictionary for use in a template
    '''
    for key in ['validate', 'xml', 'cimView']:
        dictionary[key] = reverse('pimms.apps.qn.views.genericDoc',
                                  args=(obj.centre.id,
                                        obj._meta.module_name,
                                        obj.id,
                                        key))

    if str(obj.centre) not in ['1. Example', '2. Test Centre', ]:
        dictionary['export'] = reverse('pimms.apps.qn.views.genericDoc',
                                       args=(obj.centre.id,
                                             obj._meta.module_name,
                                             obj.id,
                                             'export'))
    return dictionary


class cimHandler(object):
    '''
    This handles common operations to produce views etc on CIM document objects
    '''

    def __init__(self, obj):
        ''' Instantiate the object '''
        self.obj = obj

    def _XMLO(self):
        ''' XML view of self as an lxml element tree instance '''
        return self.obj.xmlobject()

    def _versions(self):
        ''' Provide a list of versions of this CIM document '''
        return HttpResponse('not implemented')

    def validate(self):
        ''' Is this object complete? '''
        urls = commonURLs(self.obj, {})
        del urls['validate']  # done as part of this method
        # first check that the model name is valid for cmip5 (in the event of
        # validating a model or simulation)
        if isinstance(self.obj, Simulation):
            mymodelname = str(self.obj.numericalModel)
        elif isinstance(self.obj, Component):
            mymodelname = str(self.obj)

        if mymodelname not in model_list.modelnames:
            html = ''' The model name used is not valid for CMIP5. Return to
                       the top level model page to correct this. '''
            return render_to_response('cimpage.html', {'source': 'Validation',
                                                       'obj': self.obj,
                                                       'html': html,
                                                       'urls': urls})
        valid, html = self.obj.validate()
        return render_to_response('cimpage.html', {'source': 'Validation',
                                                   'obj': self.obj,
                                                   'html': html,
                                                   'urls': urls})

    def html(self):
        ''' Return a "pretty" version of self '''
        html = viewer(self._XMLO())
        urls = commonURLs(self.obj, {})
        del urls['html']
        return render_to_response('cimpage.html',
                                  {'source': 'View',
                                   'obj': self.obj,
                                   'html': html,
                                   'urls': urls})

    def xml(self):
        mimetype = 'application/xml'
        docStr = ET.tostring(self._XMLO(), pretty_print=True)
        return HttpResponse(docStr, mimetype)

    def export(self):
        ''' Mark as complete and export to an atom feed '''
        ok, msg, url = self.obj.export()
        html = '<p>%s</p>' % msg
        urls = commonURLs(self.obj, {'persisted': url})
        del urls['export']
        return render_to_response('cimpage.html', {'source': 'Export to CMIP5',
                                                   'obj': self.obj,
                                                   'html': html,
                                                   'urls': urls})

    def cimView(self):
        ''' View this in the CIMView interface '''
        html = self.obj.cimView()
        urls = commonURLs(self.obj, {})
        del urls['cimView']  # we've just done it
        return render_to_response('viewer/cimview.html',
                                  {'source': 'cimView',
                                   'obj': self.obj,
                                   'viewhtml': html,
                                   'urls': urls})

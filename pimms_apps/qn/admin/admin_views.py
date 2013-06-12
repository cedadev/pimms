'''
Created on 5 Sep 2011

@author: gerarddevine
'''

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse

from pimms_apps.qn.admin.admin_forms import CompCopyForm
from pimms_apps.qn.admin.admin_scripts import copyCompToNewCen

from pimms_apps.qn.models import Component, Centre


def modelcopy(request):
    '''
    controller for cross-centre model copying in admin 
    '''
        
    # Deal with response 
    if request.method == 'POST':
        sourcemodel=Component.objects.get(id=request.POST['sourcemodel'])
        targetcentre=Centre.objects.get(id=request.POST['targetcentre'])
        
        copyCompToNewCen(sourcemodel, targetcentre)        
        return HttpResponse("Successfully Copied") # Redirect to success page
    else:
        form = CompCopyForm() # An unbound form
    
    return render_to_response("admin/qn/Component/compcopy.html",
                              {'form' : form},
    )
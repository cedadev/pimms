from django.shortcuts import render_to_response
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.template.context import RequestContext

from pimms.apps.qnsetup.forms import qnSetupForm
from pimms.apps.qnsetup.helpers import getqnsetupurls
from pimms.apps.helpers import getsiteurls


def qnsetuphome(request):
    '''Controller for qnsetup app home page
    
    '''
  
    try:
        # get my urls
        urls = {}
        urls = getsiteurls(urls)
        urls = getqnsetupurls(urls) 
    except:
        raise Http404
      
    if request.method == 'POST':
        qnsetupform = qnSetupForm(request.POST, request.FILES)
        if qnsetupform.is_valid():
            # Kick off the qn setup scripts
            pass
        else:
            return HttpResponseRedirect(urls['qnsetuphome'])
    else:
        qnsetupform = qnSetupForm()      
    
    return render_to_response('qnsetup/qnsetuphome.html', {'urls': urls, 'qnsetupform': qnsetupform},
                              context_instance=RequestContext(request))


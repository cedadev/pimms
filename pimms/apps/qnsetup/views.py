from django.shortcuts import render_to_response
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.template.context import RequestContext

from pimms.apps.qnsetup.forms import qnSetupForm
from pimms.apps.qnsetup.helpers import getqnsetupurls
from pimms.apps.qnsetup.models import SetupFile, Questionnaire
from pimms.apps.helpers import getsiteurls

import simplejson



def qnsetuphome(request):
    '''
    controller for experiment list home page .
    '''
    try:
        # get my urls
        urls = {}
        urls = getsiteurls(urls)
        urls = getqnsetupurls(urls)        
        
        allqns = Questionnaire.objects.filter()
#        for qn in allqns:
#            qn.url = reverse('pimms.apps.exp.views.expview', args=(exp.id, ))
#            qn.cpurl = reverse('pimms.apps.exp.views.expcopy', args=(exp.id, ))
#            qn.delurl = reverse('pimms.apps.exp.views.expdelete', args=(exp.id, ))
    except:
        raise Http404
      
    return render_to_response('qnsetup/qnsetuphome.html', {'allqns': allqns,
                                               'urls': urls},
                                context_instance=RequestContext(request))
    
    
def qninputs(request):
    '''
    '''
          
    # get my urls
    urls = {}
    urls = getsiteurls(urls)
    urls = getqnsetupurls(urls)  
    
    # Deal with response 
    if request.method == 'POST':
        cancel = request.POST.get('cancel', None)
        if cancel:
            return HttpResponseRedirect(urls['qnsetuphome'])
        else:        
            qnsetupform = qnSetupForm(request.POST, prefix='qnsetup') 
            if qnsetupform.is_valid(): 
                qn = qnsetupform.save(commit=False)
                qn.creator = request.user
                qn.save()
                
                #Run QN setup script
                
                return HttpResponseRedirect(urls['qnsetupsuccess']) # Redirect to list page 
            else:
                return render_to_response('qnsetup/qninputs.html', {'qnsetupform': qnsetupform, 'urls':urls}, context_instance=RequestContext(request))
    else:
        #qnsetupform = qnSetupForm(instance=qn, prefix='qn') # An unbound form
        qnsetupform = qnSetupForm(prefix='qnsetup') # An unbound form
        

    return render_to_response('qnsetup/qninputs.html', 
                              {'qnsetupform': qnsetupform, 
                               'urls':urls},
                                context_instance=RequestContext(request))
    

def multiple_uploader(request):
    if request.method == 'POST':
        if request.FILES == None:
            raise Http404("No objects uploaded")
        f = request.FILES['file']

        a = SetupFile()
        a.setupfile.save(f.name, f)
        a.save()

        result = [{'name': f.name,
                   'size': f.size,
                 },]

        response_data = simplejson.dumps(result)
        if "application/json" in request.META['HTTP_ACCEPT_ENCODING']:
            mimetype = 'application/json'
        else:
            mimetype = 'text/plain'
        return HttpResponse(response_data, mimetype=mimetype)
    else:
        return HttpResponse('Only POST accepted')


def qnsetupsuccess(request):
    '''Controller for app home page
    '''
    try:
        # get my urls
        urls = {}
        urls = getsiteurls(urls)
        urls = getqnsetupurls(urls)
    except:
        raise Http404
    
    return render_to_response('qnsetup/qnsetupsuccess.html', {'urls': urls},
                              context_instance=RequestContext(request))
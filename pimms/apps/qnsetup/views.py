import simplejson

from django.shortcuts import render_to_response
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.template.context import RequestContext
from django.forms.formsets import formset_factory

from pimms.apps.qnsetup.forms import qnSetupForm, UploadCVForm, UploadExpForm
from pimms.apps.qnsetup.helpers import getqnsetupurls
from pimms.apps.qnsetup.models import Questionnaire
from pimms.apps.helpers import getsiteurls



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
    
    CVFileFormSet = formset_factory(UploadCVForm)
    ExpFileFormSet = formset_factory(UploadExpForm)
    
    # Deal with response 
    if request.method == 'POST':
        cancel = request.POST.get('cancel', None)
        if cancel:
            return HttpResponseRedirect(urls['qnsetuphome'])
        else:        
            qnsetupform = qnSetupForm(request.POST, prefix='qn') 
            cvformset   = CVFileFormSet(request.POST, request.FILES, prefix='cvfile')
            expformset  = ExpFileFormSet(request.POST, request.FILES, prefix='expfile')
            if qnsetupform.is_valid() and cvformset.is_valid() and expformset.is_valid():
                #make use of the cleaned data lists here to now process the files
                #cvs = cvformset.save()
                #exps = expformset.save()
                qnsetupform.save()
              
                return HttpResponseRedirect(urls['qnsetuphome']) # Redirect to list page 
            else:
                return render_to_response('qnsetup/qninputs.html', 
                                          {'qnsetupform': qnsetupform,
                                           'cvformset': cvformset, 
                                           'expformset': expformset,
                                           'urls':urls},
                                          context_instance=RequestContext(request))
    else:
        qnsetupform = qnSetupForm(prefix='qn')
        cvformset   = CVFileFormSet(prefix='cvfile')
        expformset  = ExpFileFormSet(prefix='expfile')

    return render_to_response('qnsetup/qninputs.html', 
                              {'qnsetupform': qnsetupform,
                               'cvformset': cvformset,
                               'expformset': expformset,
                               'urls':urls},
                                context_instance=RequestContext(request))
    
    
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
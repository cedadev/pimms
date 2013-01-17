import simplejson

from django.shortcuts import render_to_response
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.template.context import RequestContext
from django.forms.formsets import formset_factory

from pimms.apps.qnsetup.forms import qnSetupForm, UploadCVForm, UploadExpForm
from pimms.apps.qnsetup.helpers import getqnsetupurls
from pimms.apps.qn.models import Questionnaire, CVFile, ExpFile
from pimms.apps.helpers import getsiteurls
from pimms.apps.qnsetup.generateQn import generate_qn


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
    
    CVFileFormSet = formset_factory(UploadCVForm, extra=2)
    ExpFileFormSet = formset_factory(UploadExpForm, extra =2)
    
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
                # deal with saving qn details
                qn = qnsetupform.save()
                # deal with saving cv file details
                cvlist = []
                for entry in cvformset.cleaned_data:
                    if len(entry):
                        cvfile = CVFile(abbrev=entry['abbrev'], filename=entry['cvfile'].name)
                        cvfile.save()
                        # add to qn instance
                        qn.cvs.add(cvfile)
                        #add the files to a list to pass to the qn generator
                        cvlist.append(entry['cvfile'])
                    
                # deal with saving exp file details
                explist = []
                for entry in expformset.cleaned_data:
                    if len(entry):
                        expfile = ExpFile(abbrev=entry['abbrev'], filename=entry['expfile'].name)
                        expfile.save()
                        # add to qn instance
                        qn.exps.add(expfile)
                        #add the files to a list to pass to the qn generator
                        explist.append(entry['expfile'])
                
                #Now run the questionnaire setup script
                generate_qn(cvlist, explist)
                
              
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
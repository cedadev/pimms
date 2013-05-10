from django.shortcuts import render_to_response
from django.http import Http404, HttpResponseRedirect
from django.template.context import RequestContext
from django.forms.formsets import formset_factory
from django.core.urlresolvers import reverse

from pimms_apps.qn.qnsetup.forms import qnSetupForm, UploadCVForm, UploadGridCVForm, UploadExpForm
from pimms_apps.qn.qnsetup.helpers import getqnsetupurls
from pimms_apps.qn.qnsetup.generateQn import generate_qn
from pimms_apps.qn.models import Questionnaire, CVFile, GridCVFile, ExpFile
from pimms_apps.helpers import getsiteurls
from pimms_apps.qn.helpers import getqnurls


def qnsetuphome(request):
    '''
    controller for experiment list home page .
    '''
    try:
        # get my urls
        urls = {}
        urls = getsiteurls(urls)
        urls = getqnsetupurls(urls)        
        
        #!FIXME: if one of the questionnairs raises an error none will be built.
        allqns = Questionnaire.objects.filter()
        for qn in allqns:
            qn.url = reverse('pimms_apps.qn.views.qnhome', args=(qn, ))
#            qn.cpurl = reverse('pimms_apps.exp.views.expcopy', args=(exp.id, ))
#            qn.delurl = reverse('pimms_apps.exp.views.expdelete', args=(exp.id, ))
    except:
        raise Http404
      
    return render_to_response('qnsetup/qnsetuphome.html', {'allqns': allqns, 'urls': urls},
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
            gridcvform   = UploadGridCVForm(request.POST, request.FILES, prefix='gridcvfile')
            expformset  = ExpFileFormSet(request.POST, request.FILES, prefix='expfile')
            if qnsetupform.is_valid() and gridcvform.is_valid() and cvformset.is_valid() and expformset.is_valid():
                # deal with saving qn details
                qn = qnsetupform.save()
                
                # deal with saving cv file details
                cvlist = []
                for entry in cvformset.cleaned_data:
                    if len(entry):
                        cvfile = CVFile(filename=entry['cvfile'].name)
                        cvfile.save()
                        # add to qn instance
                        qn.cvs.add(cvfile)
                        #add the files to a list to pass to the qn generator
                        cvlist.append(entry['cvfile'])
                
                # handle grid cvupload
                gridcvfile = GridCVFile(filename=gridcvform.cleaned_data['gridcvfile'].name)
                gridcvfile.save()
                qn.gridcv = gridcvfile
                gridupload = gridcvform.cleaned_data['gridcvfile']
                    
                # deal with saving exp file details
                explist = []
                for entry in expformset.cleaned_data:
                    if len(entry):
                        expfile = ExpFile(filename=entry['expfile'].name)
                        expfile.save()
                        # add to qn instance
                        qn.exps.add(expfile)
                        #add the files to a list to pass to the qn generator
                        explist.append(entry['expfile'])
                
                #Now run the questionnaire setup script with the uploaded files/settings and return the generated url
                generate_qn(qn, cvlist, gridupload, explist)
                
                urls['qnsetupsuccess'] = reverse('pimms_apps.qn.qnsetup.views.qnsetupsuccess', args=(qn.project, ))
                
                return HttpResponseRedirect(urls['qnsetupsuccess']) # Redirect to list page 
            else:
                return render_to_response('qnsetup/qninputs.html', 
                                          {'qnsetupform': qnsetupform,
                                           'cvformset': cvformset, 
                                           'gridcvform': gridcvform,
                                           'expformset': expformset,
                                           'urls':urls},
                                           context_instance=RequestContext(request))
    else:
        qnsetupform = qnSetupForm(prefix='qn')
        cvformset   = CVFileFormSet(prefix='cvfile')
        gridcvform   = UploadGridCVForm(prefix='gridcvfile')
        expformset  = ExpFileFormSet(prefix='expfile')

    return render_to_response('qnsetup/qninputs.html', 
                              {'qnsetupform': qnsetupform,
                               'cvformset': cvformset,
                               'gridcvform': gridcvform,
                               'expformset': expformset,
                               'urls':urls},
                                context_instance=RequestContext(request))
    
    
def qnsetupsuccess(request, qnproj):
    '''
    View controller for successful questionnaire setup
    '''
    try:
        # get my urls
        urls = {}
        urls = getsiteurls(urls)
        urls = getqnsetupurls(urls)
        # get qn specific url for success page
        urls['qnsetupsuccess'] = reverse('pimms_apps.qn.qnsetup.views.qnsetupsuccess', args=(qnproj, ))
        
        #### Now construct a url using the qnname and the home url for an actual questionnaire
        urls['qnhome'] = reverse('pimms_apps.qn.views.qnhome', args=(qnproj, ))
        
        
    except:
        raise Http404
    
    return render_to_response('qnsetup/qnsetupsuccess.html', {'urls': urls, 'qnname':qnproj},
                              context_instance=RequestContext(request))

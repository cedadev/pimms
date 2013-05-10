from django.shortcuts import render_to_response, get_object_or_404 
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required

from guardian.shortcuts import assign
from guardian.decorators import permission_required_or_403

from pimms.apps.exp.models import Experiment
from pimms.apps.exp.models import NumericalRequirement
from pimms.apps.exp.forms import ExperimentForm, RequirementForm
from pimms.apps.exp.XMLutilities import getCIMXML
from pimms.apps.exp.helpers import getexpurls
from pimms.apps.helpers import getsiteurls


@login_required
def exphome(request):
    '''
    controller for experiment list home page .
    '''
    try:
        # get my urls
        urls = {}
        urls = getsiteurls(urls)
        urls = getexpurls(urls)        
        allexps = Experiment.objects.filter(author=request.user)
        for exp in allexps:
            exp.url = reverse('pimms.apps.exp.views.expview', args=(exp.id, ))
            exp.cpurl = reverse('pimms.apps.exp.views.expcopy', args=(exp.id, ))
            exp.delurl = reverse('pimms.apps.exp.views.expdelete', args=(exp.id, ))
    except:
        raise Http404
    return render_to_response('exp/exphome.html', {'allexps': allexps,
                                               'urls': urls},
                                context_instance=RequestContext(request))


@login_required
@permission_required_or_403('exp.manage_exp', (Experiment, 'id', 'expid'))
def expview(request, expid):
    '''
    controller for individual experiment view page
    '''    
    exp = get_object_or_404(Experiment, pk=expid)
    
    # get my urls
    urls = {}
    urls = getsiteurls(urls)
    urls = getexpurls(urls)      
    urls['expedit']=reverse('pimms.apps.exp.views.expedit',args=(exp.id, ))
    urls['exppub']=reverse('pimms.apps.exp.views.exppub',args=(exp.id, ))
    
    #Get my numerical requirements
    reqs = NumericalRequirement.objects.filter(experiment=expid)
    
    for req in reqs:
        req.url = reverse('pimms.apps.exp.views.reqview', 
                              args=(req.id, ))   
    
    #Send to template
    return render_to_response('exp/expview.html', 
                              {'exp': exp, 'urls':urls, 'reqs':reqs},
                                context_instance=RequestContext(request))


@login_required
@permission_required_or_403('exp.manage_exp', (Experiment, 'id', 'expid'))
def expcopy(request, expid):
    '''
    controller for individual experiment copy page
    '''
    
    exp = get_object_or_404(Experiment, pk=expid)
    
    # get my urls
    urls = {}
    urls = getsiteurls(urls)
    urls = getexpurls(urls)  
    urls['expedit']=reverse('pimms.apps.exp.views.expedit',args=(exp.id, ))
    urls['exppub']=reverse('pimms.apps.exp.views.exppub',args=(exp.id, ))
    
    return HttpResponseRedirect(urls['exphome']) # Redirect after POST


@login_required
@permission_required_or_403('exp.manage_exp', (Experiment, 'id', 'expid'))
def expdelete(request, expid):
    '''
    controller for individual experiment delete page
    '''
    
    # get my urls
    urls = {}
    urls = getsiteurls(urls)
    urls = getexpurls(urls)  
    
    exp = get_object_or_404(Experiment, pk=expid)
    exp.delete()
    
    return HttpResponseRedirect(urls['exphome']) # Redirect after POST
  

@login_required
def expadd(request):
    '''
    controller for experiment add page
    '''
    
    exp = Experiment()
        
    # get my urls
    urls = {}
    urls = getsiteurls(urls)
    urls = getexpurls(urls)  
    
    # Deal with response 
    if request.method == 'POST':
        cancel = request.POST.get('cancel', None)
        if cancel:
            return HttpResponseRedirect(urls['exphome'])
        else:        
            if 'expform' in request.POST:
                expform = ExperimentForm(request.POST, instance=exp, prefix='exp', user=request.user) 
                if expform.is_valid(): 
                    exp = expform.save(commit=False)
                    exp.author = request.user
                    exp.save()
                    # assign permissions to access this experiment
                    assign('manage_exp', request.user, exp)
                    
                    return HttpResponseRedirect(urls['exphome']) # Redirect to list page 
                else:
                    return render_to_response('exp/expedit.html', {'expform': expform, 'urls':urls}, context_instance=RequestContext(request))
            elif 'reqform' in request.POST:
                reqform = RequirementForm(request.POST, 
                                          instance=NumericalRequirement(), 
                                          prefix='req') 
                if reqform.is_valid(): 
                    newreq = reqform.save()
                    exp.requirements.add(newreq)
            
                return HttpResponseRedirect(urls['exphome']) # Redirect to list page
    else:
        expform = ExperimentForm(instance=exp, prefix='exp', user=request.user) # An unbound form
        reqform = RequirementForm(prefix='req') # An unbound form

    return render_to_response('exp/expedit.html', 
                              {'expform': expform,               
                               'reqform': reqform, 
                               'urls':urls},
                                context_instance=RequestContext(request))



@login_required
@permission_required_or_403('exp.manage_exp', (Experiment, 'id', 'expid'))
def expedit(request, expid=None):
    '''
    controller for individual experiment edit page
    '''
    
    exp = get_object_or_404(Experiment, pk=expid)
        
    # get my urls
    urls = {}
    urls = getsiteurls(urls)
    urls = getexpurls(urls)  
    
    # Deal with response 
    if request.method == 'POST':
        cancel = request.POST.get('cancel', None)
        if cancel:
            # reroute back to view page
            urls['expview']=reverse('pimms.apps.exp.views.expview',args=(exp.id, ))
            return HttpResponseRedirect(urls['expview'])
        else:        
            if 'expform' in request.POST:
                expform = ExperimentForm(request.POST, instance=exp, prefix='exp', user=request.user) 
                if expform.is_valid():
                    exp = expform.save()
                    #add requirements
                    for newreq in expform.cleaned_data['requirements']:
                        exp.requirements.add(newreq)
                    
                    exp.author = request.user
                    exp.save()
                    # assign permissions to access this experiment
                    assign('manage_exp', request.user, exp)
                    
                    return HttpResponseRedirect(urls['exphome']) # Redirect to list page 
                else:
                    return render_to_response('exp/expedit.html', {'expform': expform, 'urls':urls}, context_instance=RequestContext(request))
            elif 'reqform' in request.POST:
                reqform = RequirementForm(request.POST, 
                                          instance=NumericalRequirement(), 
                                          prefix='req') 
                if reqform.is_valid(): 
                    newreq = reqform.save()
                    exp.requirements.add(newreq)
            
                return HttpResponseRedirect(urls['exphome']) # Redirect to list page
    else:
        expform = ExperimentForm(instance=exp, prefix='exp', user=request.user) # An unbound form
        reqform = RequirementForm(prefix='req') # An unbound form

    return render_to_response('exp/expedit.html', 
                              {'expform': expform,               
                               'reqform': reqform, 
                               'urls':urls},
                                context_instance=RequestContext(request))


@login_required
@permission_required_or_403('exp.manage_exp', (Experiment, 'id', 'expid'))
def exppub(request, expid):
    '''
    controller for individual experiment publish page
    '''
    # generate xml instance of self
    cim = getCIMXML(expid)
    
    mimetype='application/xml'
    return HttpResponse(cim, mimetype)
    

@login_required
def reqlist(request):
    '''
    controller for requirement list page
    '''
    
    try:        
        allreqs = NumericalRequirement.objects.filter(author=request.user)
        for req in allreqs:
            req.url = reverse('pimms.apps.exp.views.reqview', 
                              args=(req.id, ))
            req.delurl = reverse('pimms.apps.exp.views.reqdelete', 
                              args=(req.id, ))
        
        # get my urls
        urls = {}
        urls = getsiteurls(urls)
        urls = getexpurls(urls)  
        
    except:
        raise Http404
    
    return render_to_response('exp/reqlist.html', {'allreqs':allreqs, 'urls':urls}, 
                                       context_instance=RequestContext(request))
    


@login_required
@permission_required_or_403('exp.manage_req', (NumericalRequirement, 'id', 'reqid'))
def reqview(request, reqid):
    '''
    controller for individual requirement view page
    '''
    
    req = get_object_or_404(NumericalRequirement, pk=reqid)
    
    # get my urls
    urls = {}
    urls = getsiteurls(urls)
    urls = getexpurls(urls)  
    urls['reqedit']=reverse('pimms.apps.exp.views.reqedit',args=(req.id, ))
         
    return render_to_response('exp/reqview.html', {'req':req, 'urls':urls}, 
                                context_instance=RequestContext(request))


@login_required
def reqadd(request):
    '''
    controller for individual numerical requirement add page
    '''
    
    req = NumericalRequirement()  
    
    # get my urls
    urls = {}
    urls = getsiteurls(urls)
    urls = getexpurls(urls)    
          
    if request.method == 'POST': 
        cancel = request.POST.get('cancel', None)
        if cancel:
            return HttpResponseRedirect(urls['reqlist'])
        else:          
            reqform = RequirementForm(request.POST, instance=req)
            if reqform.is_valid():
                req = reqform.save(commit=False)
                req.author = request.user
                req.save()
                # assign permissions to access this requirement
                assign('manage_req', request.user, req)
                
                return HttpResponseRedirect(urls['reqlist']) # Redirect after POST
            else:
                return render_to_response('exp/reqedit.html', {'reqform': reqform, 'urls':urls}, context_instance=RequestContext(request))
    else:
        reqform = RequirementForm(instance=req) # An unbound form

    return render_to_response('exp/reqedit.html', {'reqform': reqform, 'urls':urls}, 
                                context_instance=RequestContext(request))


@login_required
@permission_required_or_403('exp.manage_req', (NumericalRequirement, 'id', 'reqid'))
def reqedit(request, reqid=None):
    '''
    controller for individual numerical requirement edit page
    '''
    
    req = get_object_or_404(NumericalRequirement, pk=reqid)  
    
    # get my urls
    urls = {}
    urls = getsiteurls(urls)
    urls = getexpurls(urls)    
          
    if request.method == 'POST': 
        cancel = request.POST.get('cancel', None)
        if cancel:
            urls['reqview']=reverse('pimms.apps.exp.views.reqview', args=(req.id, ))
            return HttpResponseRedirect(urls['reqview'])
        else:          
            reqform = RequirementForm(request.POST, instance=req)
            if reqform.is_valid():
                req = reqform.save(commit=False)
                req.author = request.user
                req.save()
                # assign permissions to access this requirement
                assign('manage_req', request.user, req)
                
                return HttpResponseRedirect(urls['reqlist']) # Redirect after POST
            else:
                return render_to_response('exp/reqedit.html', {'reqform': reqform, 'urls':urls}, context_instance=RequestContext(request))
    else:
        reqform = RequirementForm(instance=req) # An unbound form

    return render_to_response('exp/reqedit.html', {'reqform': reqform, 'urls':urls}, 
                                context_instance=RequestContext(request))


@login_required
@permission_required_or_403('exp.manage_req', (NumericalRequirement, 'id', 'reqid'))
def reqdelete(request, reqid=None):
    '''
    controller for deleting an individual requirement
    '''
    
    req = get_object_or_404(NumericalRequirement, pk=reqid)
    req.delete()
    
    # get my urls
    urls = {}
    urls = getsiteurls(urls)
    urls = getexpurls(urls)  

    # Redirect after POST
    return HttpResponseRedirect(urls['reqlist'])
    

# -*- coding: utf-8 -*-

import simplejson

from django.shortcuts import render_to_response
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.template.context import RequestContext
from django import forms
from django.conf import settings

from pimms_apps.qn.models import *
#from pimms_apps.qn.feeds import DocFeed
from pimms_apps.qn.forms import *
#from pimms_apps.qn.yuiTree import *
from pimms_apps.qn.BaseView import *
from pimms_apps.qn.layoutUtilities import tabs, getpubs, getsims
from pimms_apps.qn.components import componentHandler
from pimms_apps.qn.grids import gridHandler
from pimms_apps.qn.simulations import simulationHandler
from pimms_apps.qn.cimHandler import cimHandler, commonURLs
#from pimms_apps.qn.XML import *
from pimms_apps.qn.utilities import render_badrequest, gracefulNotFound, atomuri, sublist 
from pimms_apps.qn.coupling import couplingHandler
#from pimms_apps.qn.vocabs import model_list
#from pimms_apps.qn.helpers import getqnurls
#from pimms_apps.helpers import getsiteurls


logging=settings.LOG
MESSAGE=''

##############################################################################
# Note: Some code has been removed from generic PIMMS.  
# The code was commented out but are now completely removed.
# See git history for details.
# Last commit with the comments was 2fed36609 on devel.

def qnhome(request, qnname):
    ''' 
    Project questionnaire main page
    '''
    
    ##c=Centre.objects.get(id=centre_id)
    
    # pull out the specific questionnaire
    qn = Questionnaire.objects.get(qnname=qnname)
    
    # Grab all models associated with this project
    models = [Component.objects.get(id=m.id) for m in qn.component_set.filter(scienceType='model').filter(isDeleted=False)]
    for m in models:
        m.url = reverse('pimms_apps.qn.views.componentEdit', args=(qn, m.id))
        m.cpURL = reverse('pimms_apps.qn.views.componentCopy', args=(qn, m.id))
    
    # Platforms
    platforms = [Platform.objects.get(id=p['id']) for p in qn.platform_set.values().filter(isDeleted=False)]
    for p in platforms:
        p.url = reverse('pimms_apps.qn.views.platformEdit', args=(qn, p.id))
    
    # Simulations
    sims = Simulation.objects.filter(qn=qn).filter(isDeleted=False).order_by('abbrev')
    for s in sims:
        s.url = reverse('pimms_apps.qn.views.simulationEdit', args=(qn, s.id))
    
    # Grids
    grids = Grid.objects.filter(qn=qn).filter(istopGrid=True).filter(isDeleted=False) 
    for g in grids:
        g.url = reverse('pimms_apps.qn.views.gridEdit', args=(qn, g.id))
        #g.cpURL=reverse('pimms_apps.qn.views.gridCopy',args=(c.id,g.id))
    
    # 'New' buttons 
    newmodURL  = reverse('pimms_apps.qn.views.componentAdd', args=(qn, ))
    newplatURL = reverse('pimms_apps.qn.views.platformEdit', args=(qn, ))
    viewsimURL = reverse('pimms_apps.qn.views.simulationList', args=(qn, ))
    newgridURL = reverse('pimms_apps.qn.views.gridAdd', args=(qn, ))
    
    refs=Reference.objects.filter(qn=qn)
#    files=DataContainer.objects.filter(centre=c)
#    parties=ResponsibleParty.objects.filter(centre=c)
    
    #get simulation info for sim table
    tablesims = []
    tablesims = getsims(qn)
    
    return render_to_response('qnhome/summary.html',
                              {'qnname'   : qn.qnname, 
                               'models'    : models,
                               'platforms' : platforms,
                               'grids'     : grids, 
                               'sims'      : sublist(sims, 3),
                               'newplat'   : newplatURL,
                               'newgrid'   : newgridURL,   
                               'newmod'    : newmodURL,    
                               'viewsimurl': viewsimURL,  
                               'refs'      : refs,
#                               'files':files, 
#                               'parties':parties, 
                               'tabs'      : tabs(request, qn, 'Summary'),                     
                               'notAjax'   : not request.is_ajax(),
                               'tablesims' : tablesims},
                                context_instance=RequestContext(request))



def genericDoc(request, qnname, docType, pkid, method):
    ''' 
    Handle the generic documents 
    '''
  
    logging.debug('entering generic document handler')
    
    try:
        klass = {'simulation':Simulation, 'experiment':Experiment, 'component':Component, 'platform':Platform}[docType]
    except Exception, e:
        return render_badrequest('error.html', {'message':'Document type %s not known (%s)' %(docType,e)})
    
    logging.debug('ok initially')
    
    try:
        obj = klass.objects.get(id=pkid)
    except:
        return render_badrequest('error.html', {'message':'Document id %s not known as %s' %(pkid,docType)})
    
    logging.debug('ok thus far')
    
    c = cimHandler(obj)
    
    try:
        cmethod = getattr(c,method)
    except:
        return render_badrequest('error.html', {'message':'Method %s not known as a generic document handler' %method})
    
    logging.debug('made it')
    
    return cmethod()



    
##### COMPONENT HANDLING ########################################################

# Provide a view interface to the component object 
def componentAdd(request, qnname):
    ''' 
    Add a component 
    '''
  
    # get current questionnaire
    qn = Questionnaire.objects.get(qnname=qnname)
  
    c = componentHandler(qn)
    
    return c.edit(request)


@gracefulNotFound
def componentEdit(request, qnname, component_id):
    ''' 
    Edit a component 
    '''
    
    # get current questionnaire
    qn = Questionnaire.objects.get(qnname=qnname)
  
    c = componentHandler(qn, component_id)
    
    return c.edit(request)
    
    
@gracefulNotFound   
def componentSub(request, qnname, component_id):
    ''' 
    Add a subcomponent onto a component 
    '''
    
    # get current questionnaire
    qn = Questionnaire.objects.get(qnname=qnname)
      
    c = componentHandler(qn, component_id)
    
    return c.addsub(request)
    
    
@gracefulNotFound
def componentRefs(request, qnname, component_id):
    ''' 
    Manage the references associated with a component 
    '''
    
    # get current questionnaire
    qn = Questionnaire.objects.get(qnname=qnname)
  
    c = componentHandler(qn, component_id)
    
    return c.manageRefs(request)
  
    
@gracefulNotFound
def componentTxt(request, qnname, component_id):
    ''' 
    Return a textual view of the component with possible values 
    '''
    
    # get current questionnaire
    qn = Questionnaire.objects.get(qnname=qnname)
  
    c = componentHandler(qn, component_id)
    
    return c.XMLasText()
  
  
@gracefulNotFound
def componentCup(request, qnname, component_id):
    ''' 
    Return couplings for a component 
    '''
    
    # get current questionnaire
    qn = Questionnaire.objects.get(qnname=qnname)
      
    c = couplingHandler(qn, request)
    
    return c.component(component_id)


@gracefulNotFound
def componentInp(request, qnname, component_id):
    ''' 
    Return inputs for a component 
    '''
    
    # get current questionnaire
    qn = Questionnaire.objects.get(qnname=qnname)
      
    c = componentHandler(qn, component_id)
    
    return c.inputs(request)
 
 
@gracefulNotFound
def componentCopy(request, qnname, component_id):
    # get current questionnaire
    qn = Questionnaire.objects.get(qnname=qnname)
  
    c = componentHandler(qn, component_id)
    
    return c.copy()

 
##### GRID HANDLING ###########################################################
#
## Provide a vew interface to the grid object 
def gridAdd(request, qnname):
    ''' 
    Add a grid 
    '''
    
    # get current questionnaire
    qn = Questionnaire.objects.get(qnname=qnname)
  
    g = gridHandler(qn)
    
    return g.edit(request)


@gracefulNotFound
def gridEdit(request, qnname, grid_id):
    ''' Edit a grid '''
    
    # get current questionnaire
    qn = Questionnaire.objects.get(qnname=qnname)
  
    g = gridHandler(qn, grid_id)
    
    return g.edit(request)



#    
####### SIMULATION HANDLING ####################################################
#
@gracefulNotFound
def simulationEdit(request, qnname, simulation_id):
    # get current questionnaire
    qn = Questionnaire.objects.get(qnname=qnname)
    
    s = simulationHandler(qn, simid=simulation_id)
    
    return s.edit(request)


def simulationAdd(request, qnname, experiment_id):
    # get current questionnaire
    qn = Questionnaire.objects.get(qnname=qnname)
    
    s = simulationHandler(qn, expid=experiment_id)
    
    return s.add(request)


def simulationDel(request, qnname, simulation_id):
    # get current questionnaire
    qn = Questionnaire.objects.get(qnname=qnname)
    
    s = simulationHandler(qn, simid=simulation_id)
    
    return s.markdeleted(request)


def simulationList(request, qnname):
    # get current questionnaire
    qn = Questionnaire.objects.get(qnname=qnname)
    
    s = simulationHandler(qn)
    
    return s.list(request)


@gracefulNotFound
def simulationCopy(request, qnname):
    # get current questionnaire
    qn = Questionnaire.objects.get(qnname=qnname)
    
    s = simulationHandler(qn)
    return s.copy(request)


@gracefulNotFound
def simulationCopyInd(request, qnname, simulation_id):
    # get current questionnaire
    qn = Questionnaire.objects.get(qnname=qnname)
    
    s = simulationHandler(qn, simid=simulation_id)
    
    return s.copyind(request)


@gracefulNotFound
def conformanceMain(request, qnname, simulation_id):
    # get current questionnaire
    qn = Questionnaire.objects.get(qnname=qnname)
    
    s = simulationHandler(qn, simulation_id)
    
    return s.conformanceMain(request)


@gracefulNotFound
def simulationCup(request, qnname, simulation_id, coupling_id=None, ctype=None):
    ''' 
    Return couplings for a component 
    '''
    # get current questionnaire
    qn = Questionnaire.objects.get(qnname=qnname)
    
    c = couplingHandler(qn,request)
    if ctype: # this method deprecated.
        return c.resetClosures(simulation_id, coupling_id, ctype)
    else:
        return c.simulation(simulation_id)

    
def simulationCupReset(request, qnname, simulation_id):
    # get current questionnaire
    qn = Questionnaire.objects.get(qnname=qnname)
    
    s = simulationHandler(qn, simulation_id)
    
    return s.resetCouplings()

   
##### CONFORMANCE HANDLING APPEARS IN THE SIMULATION FILE  ###########################################################
# 
#@gracefulNotFound
#def conformanceEdit(request,cen_id,sim_id,req_id):
#    s=simulationHandler(cen_id,simid=sim_id)
#    return s.conformanceEdit(request,req_id)
#            
##### PLATFORM HANDLING ###########################################################

class MyPlatformForm(PlatformForm):
    '''
    '''
  
    def __init__(self, qn, *args, **kwargs):
        PlatformForm.__init__(self, *args, **kwargs)
        
        self.vocabs={'hardware':        Vocab.objects.get(name='hardwareType', qn=qn),
                     'vendor':          Vocab.objects.get(name='vendorType', qn=qn),
                     'compiler':        Vocab.objects.get(name='compilerType', qn=qn),
                     'operatingSystem': Vocab.objects.get(name='operatingSystemType', qn=qn),
                     'processor':       Vocab.objects.get(name='processorType', qn=qn),
                     'interconnect':    Vocab.objects.get(name='interconnectType', qn=qn)}
        
        for key in self.vocabs:
            self.fields[key].queryset = Term.objects.filter(vocab=self.vocabs[key])
        
        ## qs = ResponsibleParty.objects.filter(centre=centre)|ResponsibleParty.objects.filter(party=centre)
        qs = ResponsibleParty.objects.filter(qn=qn)
        self.fields['contact'].queryset = qs
       
        
@gracefulNotFound
def platformEdit(request, qnname, platform_id=None):
    ''' 
    Handle platform editing 
    '''
    # get current questionnaire
    qn = Questionnaire.objects.get(qnname=qnname)
    
    urls = {}
    
    # start by getting a form ...
    if platform_id is None:
        urls['edit'] = reverse('pimms_apps.qn.views.platformEdit', args=(qnname, ))
        if request.method == 'GET':
            pform = MyPlatformForm(qn)
        elif request.method == 'POST':
            pform=MyPlatformForm(qn, request.POST)
            
        p = None
        puri = atomuri()
    else:
        urls['edit'] = reverse('pimms_apps.qn.views.platformEdit', args=(qnname, platform_id, ))
        p = Platform.objects.get(id=platform_id)
        puri = p.uri
        if request.method == 'GET':
            pform = MyPlatformForm(qn, instance=p)
        elif request.method == 'POST':
            pform = MyPlatformForm(qn, request.POST, instance=p)
        
        urls = commonURLs(p, urls)
        
    # now we've got a form, handle it        
    if request.method == 'POST':
        if pform.is_valid():
            p = pform.save(commit=False)
            p.qn = qn
            p.uri = puri
            p.save()
            
            return HttpResponseRedirect(reverse('pimms_apps.qn.views.qnhome', args=(qn, )))
    
    return render_to_response('platform.html',
                             {'pform': pform, 
                              'urls': urls, 
                              'p': p, 
                              'qn': qn,
                              'tabs': tabs(request, qn, 'Platform')},
                              context_instance=RequestContext(request))
                              # point cform at pform too so that the completion html can use a common variable.
        
        
########## EXPERIMENT VIEWS ##################
    
def viewExperiment(request, qnname, experiment_id):
    '''
    '''
    
    # get current questionnaire
    qn = Questionnaire.objects.get(qnname=qnname)
    
    e = Experiment.objects.get(id=experiment_id)
    r = e.requirements.all()
    
    return render_to_response('experiment.html', {'e'    :e,
                                                  'reqs' :r,
                                                  #'tabs':tabs(request,cen_id,'Experiment')
                                                  },
                                                  context_instance=RequestContext(request))


               

############ Simple Generic Views ########################

class ViewHandler(BaseViewHandler):
    ''' 
    Specialises Base View for the various resource understood as a "simple" view 
    '''
    
    # The base view handler needs a mapping between the resource type
    # as it will appear in a URL, the name it is used when an attribute, 
    # the resource class and the resource class form
    # (so keys need to be lower case)
    SupportedResources={'modelmod': {'attname': 'codeMod',
                                    'title'   : 'Model Modifications',
                                    'tab'     : 'ModelMods',
                                    'class'   : CodeMod,
                                    'form'    : CodeModForm,
                                    'filter'  : None},
                        
                        'inputmod': {'attname': 'inputMod',
                                    'title'   : 'Input Modifications', 
                                    'tab'     : 'InputMods',
                                    'class'   : InputMod, 
                                    'form'    : InputModIndex,
                                    'filter'  : None}, 
                        
                            'file': {'attname': 'dataContainer',
                                    'title'   : 'Files and Variables',
                                    'tab'     : 'Files & Vars',
                                    'class'   : DataContainer,
                                    'form'    : DataHandlingForm,
                                    'filter'  : Experiment},
                        
                       'reference': {'attname': 'references',
                                     'title'  : 'References',
                                     'tab'    : 'References',
                                     'class'  : Reference,
                                     'form'   : ReferenceForm,
                                     'filter' : None},
                        
                         'parties': {'attname': 'responsibleParty',
                                     'title'  : 'Parties', 
                                     'tab'    : 'Parties',
                                     'class'  : ResponsibleParty, 
                                     'form'   : ResponsiblePartyForm,
                                     'filter' : None},
                        
                        #'grid':{'attname':'grid','title':'Grid Definitions','class':Grid,
                         #       'form':GridForm,'filter':None,'tab':'Grids'},
                        }
    
    # Note that we don't expect to be able to assign files, since we'll directly
    # attach objects within files as appropriate.
                        
    # Some resources are associated with specific targets, so we need a mapping
    # between how they appear in URLs and the associated django classes
    # (so keys need to be lower case)     
    # FIXME: all of this could use ._meta.module_name ...               
                        
    SupportedTargets={'simulation'  : {'class':Simulation, 'attname':'simulation'},
                      'qn'          : {'class':Questionnaire, 'attname':'qn'},
                      'component'   : {'class':Component, 'attname':'component'},
                      'ensemble'    : {'class':Simulation, 'attname':'simulation'},
                      'experiment'  : {'class':Experiment, 'attname':'experiment'},
                      'grid'        : {'class':Grid, 'attname':'grid'},
                     }
                     
    # and for each of those we need to get back to the target view/edit, and for
    # that we need the right function name
    
    SupportedTargetReverseFunctions={
                      'simulation': 'pimms_apps.qn.views.simulationEdit',
                      'qn'        : 'pimms_apps.qn.views.home',
                      'component' : 'pimms_apps.qn.views.componentEdit',
                      'grid'      : 'pimms_apps.qn.views.gridEdit',
                      'ensemble'  : 'pimms_apps.qn.views.ensemble',
                      # not sure about the following: for files ...
                      'experiment': 'pimms_apps.qn.views.list',
                      }
                        
    # Now the expected usage of this handler is for
    # codemodifications associated with a given model (assign to a simulation and list)
    # references for a given component (assign to a component and list)
    # data objects in general (list)
    # initial conditions (assign to a simulation) and list
                        
    def __init__(self, qn, resourceType, resource_id, target_id, targetType):
        ''' 
        We can have some combination of the above at initialiation time 
        '''
        
        if resourceType not in self.SupportedResources:
            raise ValueError('Unknown resource type %s '%resourceType)
     
        if targetType is not None:
            # We grab an instance of the target
            if targetType not in self.SupportedTargets:
                raise ValueError('Unknown target type %s'%targetType)
            
            try:
                target = self.SupportedTargets[targetType]
                target['type'] = targetType
                target['instance'] = target['class'].objects.get(id=target_id)
            except Exception, e:
                # FIXME: Handle this more gracefully
                raise ValueError('Unable to find resource %s with id %s' %(targetType, target_id))
            
            # and work out what the url will be to return to this target instance
            try:
                target['url'] = reverse(self.SupportedTargetReverseFunctions[targetType], args=[qn, target_id])
            except: 
                target['url'] = ''
        else: 
            target=None 
        
        resource = self.SupportedResources[resourceType]
        resource['type'] = resourceType
        resource['id'] = resource_id
     
        BaseViewHandler.__init__(self, qn, resource, target)
                
    def objects(self):
        ''' 
        Returns a list of objects to display, as a function of the resource and target types
        '''
        
        objects = self.resource['class'].objects.all()
        
        if self.resource['type'] == 'modelmod' and self.target['type'] == 'simulation':
            # for code modifications, we need to get those associated with a model for a simulation
            constraintSet = Component.objects.filter(model=self.target['instance'].numericalModel)
            objects = objects.filter(component__in=constraintSet)
        
        if self.resource['type'] in ['reference', 'file']:
            objects = objects.filter(qn=None)|objects.filter(qn=self.qn)
            oby = {'reference':'name', 'file':'abbrev'}[self.resource['type']]
            if self.target:
                #d={self.target['type']+'__id':str(self.target['instance'].id)}
                #objects=objects.filter(**d)
                if self.target['type'] == 'experiment':
                    objects = objects.filter(experiments=self.target['instance'].id)
                    
            objects = objects.order_by(oby)
        elif self.resource['type'] == 'modelmod':
            objects=objects.filter(qn=self.qn)
            objects=objects.order_by('mnemonic')
        elif self.resource['type'] == 'parties':
            objects=objects.filter(qn=self.qn).order_by('name')
        elif self.resource['type'] == 'inputmod':
            objects=objects.filter(qn=self.qn)
            objects=objects.order_by('mnemonic')
        return objects
        
    def constraints(self):
        ''' 
        Return constraints for form specialisation 
        '''
        if self.resource['type'] == 'modelmod':
            if self.target['type'] == 'simulation':
                return self.target['instance'].numericalModel
            elif self.target['type'] == 'component':
                return self.target['instance']
            elif self.target['type'] == 'ensemble':
                return self.target['instance'].numericalModel
        if self.resource['type'] in ['reference', 'file', 'grid']:
            return self.qn 
        if self.resource['type'] == 'inputmod':
            if self.target['type'] == 'ensemble':
                return self.target['instance'] # which should be a simulation
                   
        return None

def edit(request, qnname, resourceType, resource_id, targetType=None, target_id=None, returnType=None):
    ''' 
    This is the generic simple view editor 
    '''
  
    # get current questionnaire
    qn = Questionnaire.objects.get(qnname=qnname)
    
    h = ViewHandler(qn, resourceType, resource_id, target_id, targetType)
    return h.edit(request, returnType)
  

def delete(request, qnname, resourceType, resource_id, targetType=None, target_id=None, returnType=None):
    ''' This is the generic simple item deleter '''
    qn = Questionnaire.objects.get(qnname=qnname)
    h = ViewHandler(qn, resourceType, resource_id, target_id, targetType)
    
    return h.delete(request, returnType)


def list(request, qnname, resourceType, targetType=None, target_id=None):
    ''' 
    This is the generic simple view lister 
    '''
    
    # get current questionnaire
    qn = Questionnaire.objects.get(qnname=qnname)
    
    h = ViewHandler(qn, resourceType, None, target_id, targetType)
    return h.list(request)
  

def filterlist(request,cen_id,resourceType):
    ''' Receives a list filter post and redirects to list '''
    h=ViewHandler(cen_id,resourceType,None,None,None)
    return h.filterlist(request)


def assign(request, qnname, resourceType, targetType, target_id):
    ''' 
    Provide a page to allow the assignation of resources of type resourceType
    to resource target_id of type targetType 
    '''
  
    # get current questionnaire
    qn = Questionnaire.objects.get(qnname=qnname)
  
    if resourceType == 'file':
        return render_badrequest('error.html', {'message':'Cannot assign files to targets, assign objects from within them!'})
   
    h = ViewHandler(qn, resourceType, None, target_id, targetType)
    
    return h.assign(request) 

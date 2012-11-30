# -*- coding: utf-8 -*-
# Create your views here.
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings

from pimms.apps.qn.models import *
from pimms.apps.qn.forms import *
from pimms.apps.qn.yuiTree import *
from pimms.apps.qn.layoutUtilities import tabs
from pimms.apps.qn.utilities import atomuri
from pimms.apps.qn.cimHandler import commonURLs

logging=settings.LOG

ConformanceFormSet=modelformset_factory(Conformance,
                                        form=ConformanceForm,
                                        exclude=('simulation','requirement'))
                                        #exclude=('simulation'))


class MyConformanceFormSet(ConformanceFormSet):
    ''' Mimics the function of a formset for the situation where we want to edit the
    known conformances '''
    def __init__(self,simulation,data=None):
        self.extra=0
        qset=Conformance.objects.filter(simulation=simulation)
        ConformanceFormSet.__init__(self,data,queryset=qset)
        self.s=simulation
    def specialise(self):
        for form in self.forms:
            form.specialise(self.s)
            
class simulationHandler(object):
    ''' 
    Simulation is an instance of a cim document which means there are some 
    common methods 
    '''
    
    def __init__(self, centre_id, simid=None, expid=None):
        ''' Initialise based on what the request needs '''
        self.centreid = centre_id
        self.centre = Centre.objects.get(pk=centre_id)
        self.pkid = simid
        self.expid = expid
        self.errors = {}
        if self.pkid:
            self.s = Simulation.objects.get(pk=self.pkid)
            self.Klass = self.s.__class__
        else:
            self.s = None
            self.Klass = 'Unknown as yet by simulation handler'

    def __handle(self,request,s,e,url,label):
        '''
        This method handles the form itself for both the add and edit methods
        '''

        logging.debug('entering simulation handle routine')

        if s.ensembleMembers > 1:
            eset = s.ensemble_set.all()
            assert(len(eset)==1, 'There can only be one ensemble set for %s' % s)
            members = eset[0].ensemblemember_set.all()
            ensemble = {'set':eset[0], 'members':members}
        else:
            ensemble = None

        urls = {'url':url}
        if label == 'Update':
            urls['ic']=reverse('pimms.apps.qn.views.assign',
                    args=(self.centreid,'initialcondition','simulation',s.id,))
            urls['bc']=reverse('pimms.apps.qn.views.simulationCup',
                    args=(self.centreid,s.id,))
            urls['con']=reverse('pimms.apps.qn.views.conformanceMain',
                    args=(self.centreid,s.id,))
            urls['ens']=reverse('pimms.apps.qn.views.ensemble',
                    args=(self.centreid,s.id,))
            urls['mod']=reverse('pimms.apps.qn.views.assign',
                     args=(self.centreid,'modelmod','simulation',s.id,))
            urls=commonURLs(s,urls)
            # dont think we should be able to get to input mods from here ...
            #urls['ics']=reverse('pimms.apps.qn.views.assign',
            #         args=(self.centreid,'inputmod','simulation',s.id,))        
        
        # A the moment we're only assuming one related simulation so we don't 
        # have to deal with a formset
        rsims = s.related_from.all()
        if len(rsims):
            r = rsims[0]
        else:
            r = None

        if request.method == 'POST':
            # do the simualation first ...
            simform = SimulationForm(request.POST,
                                     instance=s,
                                     prefix='sim')
            simform.specialise(self.centre)
            if simform.is_valid():
                simok = True
                if label == 'Add':
                    oldmodel = None
                    olddrs = None
                    oldstartyear = None
                else:
                    oldmodel = s.numericalModel
                    olddrs = s.drsMember
                    oldstartyear = s.duration.startDate.year

                news = simform.save()
                logging.debug('model before %s, after %s' % (oldmodel,
                                                        news.numericalModel))

                if news.numericalModel != oldmodel:
                    news.resetConformances()
                    news.resetCoupling()
                    news.updateDRS()

                logging.debug('drs before %s, after %s' % (olddrs,
                                                           news.drsMember))

                # making sure the original sim has a drsoutput
                if s.drsOutput.all().count() == 0:
                    s.updateDRS()
                    
                #update the drsouput if drsmember changes or new sim created
                if news.drsMember != olddrs:
                    news.updateDRS()
                
                #update the start year if necessary
                if news.duration.startDate.year != oldstartyear:
                    news.updateDRS()

            elif not simform.is_valid():
                simok = False
                logging.info('SIMFORM not valid [%s]' % simform.errors)
            relform = SimRelationshipForm(s,
                                          request.POST,
                                          instance=r,
                                          prefix='rel')

            if relform.is_valid():
                if simok: 
                    r=relform.save()
                    return HttpResponseRedirect(news.edit_url())    
            else:
                # if there is no sto, then we should delete this relationship instance and move on.
                pass
            
            #generate a drs string instance in DRS Output class
            
            
        else:
            relform=SimRelationshipForm(s,instance=r,prefix='rel')
            simform=SimulationForm(instance=s,prefix='sim')
            simform.specialise(self.centre)
            
        
        # work out what we want to say about couplings
        cset=[]
        if label !='Add': cset=s.numericalModel.couplings(s)
        for i in cset:
            i.valid=len(i.internalclosure_set.all())+len(i.externalclosure_set.all()) > 0 # need at least one closure
            
        # now work out what we want to say about conformances.
        cs=Conformance.objects.filter(simulation=s)
            
        return render_to_response('simulation.html',
            {'s':s,'simform':simform,'urls':urls,'label':label,'exp':e,
             'cset':cset,'coset':cs,'ensemble':ensemble,'rform':relform,
             'tabs':tabs(request,self.centreid,'Simulation',s.id or 0)})
            # note that cform points to simform too, to support completion.html
            
    def edit(self,request):
        ''' Handle providing and receiving edit forms '''
       
        s=self.s
        s.updateCoupling()
        
        e=s.experiment
        url=reverse('pimms.apps.qn.views.simulationEdit',args=(self.centreid,s.id,))
        label='Update'
        return self.__handle(request,s,e,url,label)
       
    def add(self,request):
        ''' Create a new simulation instance '''
        # first see whether a model and platform have been created!
        # if not, we should return an error message ..
        c=self.centre
        p=c.platform_set.values()
        m=c.component_set.values()
        url=reverse('pimms.apps.qn.views.centre',args=(self.centreid,))
        if len(p)==0:
            ''' Require them to create a platform '''
            message='You need to create a platform before creating a simulation'
            return render_to_response('error.html',{'message':message,'url':url})
        elif len(m)==0:
            ''' Require them to create a model'''
            message='You need to create a model before creating a simulation'
            return render_to_response('error.html',{'message':message,'url':url})
        url=reverse('pimms.apps.qn.views.simulationAdd',args=(self.centreid,self.expid,))
       
        u=atomuri()
        e=Experiment.objects.get(pk=self.expid)
        s=Simulation(uri=u,experiment=e,centre=self.centre)
        
        #grab the experiment duration if we can
        # there should be no more than one spatio temporal constraint, so let's 
        # get that one.
        
        stcg=e.requirements.filter(ctype__name='SpatioTemporalConstraint')
        if len(stcg)<>1:
            logging.info('Experiment %s has no duration (%s)?'%(e,len(stcg)))
        else:
            stc=stcg[0].get_child_object()
            print 'duration',stc.requiredDuration
            s.duration=stc.requiredDuration
        label='Add'
        
        return self.__handle(request,s,e,url,label)

    def list(self,request):
        ''' Return a listing of simulations for a given centre '''
        
        c=Centre.objects.get(pk=self.centreid)
       
        #little class to monkey patch up the stuff needed for the template
        class etmp:
            def __init__(self, abbrev, values, id, group):
                self.abbrev = abbrev
                self.values = values
                self.id = id
                self.url = reverse('pimms.apps.qn.views.viewExperiment',
                                 args=(c.id, id,))
                self.new = reverse('pimms.apps.qn.views.simulationAdd', 
                                 args=(c.id, id,))
                self.group = group
                
        csims = Simulation.objects.filter(centre=c).filter(isDeleted=False)
        cpurl = reverse('pimms.apps.qn.views.simulationCopy', args=(c.id, ))

        eset=Experiment.objects.all().filter(isDeleted=False)
        exp=[]
        for e in eset:
            sims = e.simulation_set.filter(centre=c.id).filter(isDeleted=False)
            group = e.abbrev.split()[1]
            for s in sims: 
                s.url = reverse('pimms.apps.qn.views.simulationEdit', 
                                args=(c.id,s.id,))    
            exp.append(etmp(e.abbrev, sims, e.id, group))

        return render_to_response('simulationList.html',
            {'c':c,'experiments':exp,'csims':csims,'cpurl':cpurl,
            'tabs':tabs(request,c.id,'Experiments'),
            'notAjax':not request.is_ajax()})
 
 
    def conformanceMain(self,request):
        ''' Displays the main conformance view '''

        s=self.s
        e=s.experiment
        
        urls={'self':reverse('pimms.apps.qn.views.conformanceMain',
                    args=(self.centreid,s.id,)),
              'mods':reverse('pimms.apps.qn.views.assign',
                    args=(self.centreid,'modelmod','simulation',s.id,)),
              'sim':reverse('pimms.apps.qn.views.simulationEdit',
                    args=(self.centreid,s.id,))
                    }
        #con=Conformance.objects.filter(simulation=s)
        if request.method=='POST':
            cformset=MyConformanceFormSet(s,request.POST)
            if cformset.is_valid():
                cformset.save()
                return HttpResponseRedirect(urls['self'])
            else:
                cformset.specialise()
        elif request.method=='GET':
            cformset=MyConformanceFormSet(s)
            cformset.specialise()
          
        return render_to_response('conformance.html',{'s':s, 'e':e, 'cform':cformset, 'urls':urls, 
                                                      'tabs':tabs(request, self.centreid, 'Conformance')})
  
  
    def copy(self,request):
        '''
        Makes a copy of myself
        '''
        if request.method=='POST':
            if request.POST['targetSim'] == '---':
                return HttpResponse('Error, please choose a simulation to \
                                    copy. You can use your browser back button')
            
            targetExp = request.POST['targetExp']
            exp = Experiment.objects.get(id=targetExp)
            targetSim = request.POST['targetSim']
            s = Simulation.objects.get(id=targetSim)
            ss = s.copy(exp)
            url = reverse('pimms.apps.qn.views.simulationEdit', 
                        args=(self.centreid,ss.id,))
            
            return HttpResponseRedirect(url)
        
        else:
            return self.list(request)
        
        
    def copyind(self,request):
        '''
        An individual copy (from main simulation table button) that copies 
        everything across, e.g. conformances/ensembles (unlike the 
        cross-experiment copying above)
        '''
        s = self.s
        ss = s.copy(s.experiment)
        url = reverse('pimms.apps.qn.views.simulationEdit', 
                    args=(self.centreid, ss.id, ))
        
        return HttpResponseRedirect(url)
        
        
    def markdeleted(self, request):
        '''
        Deletes me as a simulation (i.e marks me as isDeleted), having first
        confirmed that I am not already published.
        '''
        s = self.s
        s.isDeleted = True
        s.save()
        # return me to the summary page
        url = reverse('pimms.apps.qn.views.centre', args=(self.centreid, ))
        return HttpResponseRedirect(url)
        
        
    def resetCouplings(self):
        ''' 
        Resets ALL couplings and ALL closures from the originals in the model. 
        Note that copy does not do the closures, but this one does. One closure 
        at a time can be done via the coupling handler. 
        '''
        s = self.s
        s.resetCoupling(closures=True)
        # and return to the coupling view 
        url = reverse('pimms.apps.qn.views.simulationCup',
                    args=(self.centreid, s.id, ))
        
        return HttpResponseRedirect(url)
# -*- coding: utf-8 -*-
from django.conf import settings
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.forms.models import modelformset_factory

from pimms.apps.qn.models import *
from pimms.apps.qn.forms import *
from pimms.apps.qn.layoutUtilities import tabs


logging = settings.LOG

InternalClosureFormSet = modelformset_factory(InternalClosure,can_delete=True,
                                    form=InternalClosureForm,extra=0,
                                    exclude=('coupling'))
ExternalClosureFormSet = modelformset_factory(ExternalClosure,can_delete=True,
                                    form=ExternalClosureForm,extra=0,
                                    exclude=('coupling'))                                

#https://www.cduce.org/~abate/index.php?q=dynamic-forms-with-django


class ClosureReset:
    '''It's possible that when we show the simulation couplings that there have been new 
    closures created in the component interface, which haven't been replicated to the 
    simulation copy of the couplings. We will need to provide a button to reset closures 
    from the model copy. (It needs to be optional).'''
    def __init__(self,centre_id,simulation_id,coupling,ctype='None'):
        self.coupling=coupling
        self.closureModel={'ic':InternalClosure,'ec':ExternalClosure,'None':None}[ctype]
        args=[centre_id,simulation_id,coupling.id,]
        if ctype<>'None':args.append(ctype)
        self.url=reverse('pimms.apps.qn.views.simulationCup',args=args)
        self.returnURL=reverse('pimms.apps.qn.views.simulationCup',
                 args=(centre_id,simulation_id,))
    def reset(self):
        ''' Reset internal or external closures '''
        o=self.coupling.original
        set=self.closureModel.objects.filter(coupling=o)
        for i in set:
            i.makeNewCopy(self.coupling)
        return HttpResponseRedirect(self.returnURL)


class MyInternalClosures(InternalClosureFormSet):
    def __init__(self,q,data=None):
        prefix='ic%s'%q
        self.coupling=q
        qset=InternalClosure.objects.filter(coupling=q)
        InternalClosureFormSet.__init__(self,data,queryset=qset,prefix=prefix)    
    def save(self):
        instances=InternalClosureFormSet.save(self,commit=False)
        logging.debug('saving internal closures for %s'%self.coupling)
        for i in instances:
            i.coupling=self.coupling
            i.save()
    
    
class MyExternalClosures(ExternalClosureFormSet):
    def __init__(self,q,data=None):
        prefix='ec%s'%q
        self.coupling=q
        qset=ExternalClosure.objects.filter(coupling=q)
        ExternalClosureFormSet.__init__(self,data,queryset=qset,prefix=prefix)
        for i in self.forms:
            i.specialise()
        
    def save(self):
        instances=ExternalClosureFormSet.save(self,commit=False)
        logging.debug('saving external closures for %s'%self.coupling)
        for i in instances:
            i.coupling=self.coupling
            i.save()
            
            
class DualClosureForm(forms.Form):
    ''' To replace individual closures and simplify the input entry '''
    #existing file options
    empty=[(None,None)]
    efile=forms.ChoiceField(choices=empty,required=False)
    # new file options
    nurl=forms.URLField(required=False)
    nfname=forms.CharField(max_length=132,required=False)
    # component options
    component=forms.ChoiceField(choices=empty,required=False)
    # detail:
    spatialRegrid=forms.ChoiceField(choices=empty,required=False)
    temporalTransform=forms.ChoiceField(choices=empty,required=False)
    
    def specialise(self,centre,q,vocabs,efiles,components):
        ''' Initialise the target for processing this form '''
        self.vocabs=vocabs
        for k in vocabs:
            self.fields[k].choices=[(i.id,str(i)) for i in vocabs[k]]
        self.fields['component'].choices=self.empty+[(i.id,str(i)) for i in components]
        self.fields['efile'].choices=self.empty+[(i.id,str(i)) for i in efiles]
        self.efiles=[e.abbrev for e in efiles]
        self.coupling=q
        self.centre=centre
    
    def process(self):
        ''' Takes the cleaned data and loads into the appropriate closure '''
        # It's not a save, because it's not a save directly to a model
        if self.selectedOption is None: return
        
        #FIXME This is a bit of a hack for now. In those cases where the binding is for an initial 
        # condition request, we do not ask for timetransformation information - do for now I am 
        # hardcoding it as 'Exact' in the 'Term' terms
        tt=self.cleaned_data['temporalTransform']
        v=Vocab.objects.get(name='TimeTransformation')
                    
        if tt == '':
            tTransform = Term.objects.filter(vocab=v).get(name='Exact')
        else:
            tTransform = Term.objects.get(id=self.cleaned_data['temporalTransform'])   
             
        if self.selectedOption=='efile':
            e=ExternalClosure(coupling=self.coupling,
                              targetFile=DataContainer.objects.get(id=self.cleaned_data['efile']),
                              temporalTransform=tTransform,
                              #temporalTransform=Term.objects.get(id=self.cleaned_data['temporalTransform']),
                              spatialRegrid=Term.objects.get(id=self.cleaned_data['spatialRegrid']))
            e.save()
        elif self.selectedOption=='nurl':
            #create new DataContainer, then create new External Closure
            d=DataContainer(abbrev=self.cleaned_data['nfname'],
                            link=self.cleaned_data['nurl'], 
                            centre=self.centre)
            d.save()
            e=ExternalClosure(coupling=self.coupling,
                              targetFile=d,
                              temporalTransform=tTransform,
                              #temporalTransform=Term.objects.get(id=self.cleaned_data['temporalTransform']),
                              spatialRegrid=Term.objects.get(id=self.cleaned_data['spatialRegrid']))
            e.save()
        elif self.selectedOption=='component':
            #create new internal closure
            
            i=InternalClosure(coupling=self.coupling,
                              target=Component.objects.get(id=self.cleaned_data['component']),
                              #temporalTransform=Term.objects.get(id=self.cleaned_data['temporalTransform']),
                              temporalTransform=tTransform,
                              spatialRegrid=Term.objects.get(id=self.cleaned_data['spatialRegrid']))
            i.save()
        else: raise ValueError('Unexpected condition in DualClosureForm.process %s'%self.selectedOption)

        
    def clean(self):
        ''' Need to make sure we have only one option submitted (and in the case of a new file,
        both the url and mnemonic '''
        logging.debug(self.cleaned_data)
        efile=(self.cleaned_data['efile'] <> 'None')
        nurl,nfname=False,False
        if 'nurl' in self.cleaned_data: nurl=self.cleaned_data['nurl'] <> ''
        if 'nfname' in self.cleaned_data: nfname=self.cleaned_data['nfname'] <> ''
        component=self.cleaned_data['component'] <> 'None' and self.cleaned_data['component'] <> ''
        ok=True
        selected=int(efile)+int(nurl or nfname)+int(component)
        if selected>1: 
            raise ValidationError('Choose only one binding (ie only one of the OR options)!')
        if (nurl or nfname) and not (nurl and nfname):
            raise ValidationError('You need to choose both a new url and a new mnemonic for a new file!')
        if nfname:
            if self.cleaned_data['nfname'] in self.efiles: 
                raise ValidationError('Your new file short name is already in use!')

        logging.debug('acceptable dual form')
        # which option (for use in processing so we don't have to repeat the logic)
        self.selectedOption={0:None,1:'efile',2:'nurl',3:'component'}[efile*1+nurl*2+component*3]
        return self.cleaned_data
        
            
class MyCouplingForm(object):
    def __init__(self,dict):
        for k in dict:
            self.__setattr__(k,dict[k])
    def __str__(self):
        s=self.title+str(self.cf)+str(self.ec)+str(self.ic)+str(self.dcf)
        return s 

class MyCouplingFormSet:
    
    ''' Unlike a regular django formset, this one has to handle the closures within each 
    coupling instance, and we can do that using formsets, but not the couplings themselves '''
     #http://docs.djangoproject.com/en/dev/topics/forms/modelforms/#id1
    
    def __init__(self,model,simulation,queryset,data=None):
        ''' Initialise the forms needed to interact for a (model) component (indicated by the coupling group).'''
        
        self.model=model
        self.simulation=simulation
         
        # build up a queryset, chunked into the various types of component inputs
        ctypes=Term.objects.filter(vocab=Vocab.objects.get(name='InputTypes'))
        bcvalue=ctypes.get(name='BoundaryCondition')  #used for layout on coupling form
        afvalue=ctypes.get(name='AncillaryFile') #used for layout on closure form
        icvalue=ctypes.get(name='InitialCondition') # used for layout on closure form

        # setup our vocabularies
        inputTechnique=Term.objects.filter(vocab=Vocab.objects.get(name='InputTechnique'))
        FreqUnits=Term.objects.filter(vocab=Vocab.objects.get(name='FreqUnits'))
        
        # for closures
        spatialRegrid=Term.objects.filter(vocab=Vocab.objects.get(name='SpatialRegrid'))
        temporalTransform=Term.objects.filter(vocab=Vocab.objects.get(name='TimeTransformation'))
        
        self.couplingVocabs={ 'inputTechnique':inputTechnique,
                'FreqUnits':FreqUnits}
        self.closureVocabs={'spatialRegrid':spatialRegrid,
                'temporalTransform':temporalTransform}
               
        # rather than use a django formset for the couplings, we'll do them by
        # hand, but do the closures using a formset ... this made sense when
        # we had lots of closures, but less now ...
        
        self.forms=[]
        # this is the list of relevant realm level components:
        BaseInternalQueryset=Component.objects.filter(model=self.model).filter(isRealm=True)
        for q in queryset:
            cf=CouplingForm(data,instance=q,prefix=q)
            if self.simulation:
                centre_id=self.model.centre.id
                cf.icreset=ClosureReset(centre_id,simulation.id,q,'ic')
                cf.ecreset=ClosureReset(centre_id,simulation.id,q,'ec')
            title='Binding for %s %s'%(q.targetInput.ctype,q.targetInput)
            if self.simulation: title+=' for simulation %s'%self.simulation
            for key in self.couplingVocabs:
                cf.fields[key].queryset=self.couplingVocabs[key]
            ic=MyInternalClosures(q,data)
            ec=MyExternalClosures(q,data)
            # need to collect rows of forms here to simplify template
            formrows=[]
            for i in range(max(len(ic.forms),len(ec.forms))):
                entry=['','']
                if i < len(ec.forms): entry[0]=ec.forms[i]
                if i < len(ic.forms): entry[1]=ic.forms[i]
                formrows.append(entry)
            print len(ic.forms),len(ec.forms),formrows
            dcf=DualClosureForm(data,prefix='dcf%s'%q)
            #make sure we don't offer up the target input owner component:
            iqs=BaseInternalQueryset.exclude(id__exact=q.targetInput.owner.id)
            # and only offer up our files.
            efiles = DataContainer.objects.filter(centre=self.model.centre)| DataContainer.objects.filter(centre=None)
            dcf.specialise(self.model.centre,q,self.closureVocabs,efiles,iqs)
            self.forms.append(MyCouplingForm({'title':title,'formrows':formrows,'dc':dcf,
                                              'cf':cf,'ic':ic,'ec':ec,'iqs':iqs,
                                              'bcv':bcvalue,'afv':afvalue,'icv':icvalue}))
            
    def is_valid(self):
        ok=True
        for f in self.forms:
            indok=True
            r1=f.cf.is_valid()
            if not r1: 
                ok=False
                indok=False
            r2=f.ec.is_valid()
            if not r2: 
                ok=False
                indok=False
            r3=f.ic.is_valid()
            if not r3: 
                ok=False
                indok=False
            r4=f.dc.is_valid()
            if not r4: 
                ok=False
                indok=False
            #logging.debug('%s-%s-%s-%s'%(r1,r2,r3,r4))
            #logging.debug('%s[cf#%s#_ec#%s#_ic#%s#_dc#%s#]'%(ok,f.cf.errors,f.ec.errors,f.ic.errors,f.dc.errors))
            
            # Adding individual form level error messages
            f.FormError = not indok
            if not indok:
                errorslist = []
                for err in f.ec.errors:
                    for key in err.itervalues():
                        errorslist.append(key[0])
                
                f.FormErrorMsg = errorslist
        
        self.FormError=not ok   # used in coupling.html
        return ok
                
    def specialise(self):
        for f in self.forms:
            for i in f.ic.forms+f.ec.forms:
                #print i.fields.keys()
                #i.fields['inputDescription']=self.widgets['inputDescription']
                for key in self.closureVocabs:
                    i.fields[key].queryset=self.closureVocabs[key]
            for i in f.ic.forms:
                i.fields['target'].queryset=f.iqs
                
    def save(self):
        for f in self.forms:
            # first the coupling form
            cf=f.cf.save(commit=False)
            #cf.parent=self.parent
            #cf.targetInput=self.queryset.get(id=cf.id).targetInput
            cf.save()
            # now the external, internal closures formsets ...
            instances=f.ec.save()
            instances=f.ic.save()
            # and finally, the dual closure (new) entries
            dc=f.dc.process()
        
        if self.simulation: 
            # aggregate up the files in our closures
            self.simulation._updateIO()
            
class couplingHandler:
    ''' Handles couplings for models and simuations '''
    def __init__(self,centre_id,request):
        self.request=request
        self.method=request.method
        self.centre_id=centre_id
    def component(self,component_id):
        ''' Handle's model couplings '''
        self.component=Component.objects.get(id=component_id)
        # we do the couplings for the parent model of a component
        self.urls={'ok':reverse('pimms.apps.qn.views.componentCup',args=(self.centre_id,component_id,)),
              'return':reverse('pimms.apps.qn.views.componentEdit',args=(self.centre_id,component_id,)),
              'returnName':'component'
              }
        return self.__handle()
    def simulation(self,simulation_id):
        simulation=Simulation.objects.get(id=simulation_id)
        self.component=simulation.numericalModel
        self.urls={'ok':reverse('pimms.apps.qn.views.simulationCup',args=(self.centre_id,simulation_id,)),
              'return':reverse('pimms.apps.qn.views.simulationEdit',args=(self.centre_id,simulation_id,)),
              'returnName':'simulation',
              'nextURL':reverse('pimms.apps.qn.views.assign',
                     args=(self.centre_id,'modelmod','simulation',simulation_id,)),
              'reset':reverse('pimms.apps.qn.views.simulationCupReset',args=(self.centre_id,simulation_id,)),
              }
        print self.urls['nextURL']
        return self.__handle(simulation)
    def __handle(self,simulation=None):
        model=self.component.model
        assert model != None,'Component %s has no model'%self.component
        queryset=model.couplings(simulation)
        self.urls['model']=reverse('pimms.apps.qn.views.componentEdit',
                    args=(self.centre_id,model.id,))
        logging.debug('Handling %s coupling request for %s (simulation %s)'%(self.method,model,simulation))
       
        if self.method=='POST':
            Intform=MyCouplingFormSet(model,simulation,queryset,self.request.POST)
            if Intform.is_valid():
                Intform.save()
                return HttpResponseRedirect(self.urls['ok'])
            else:
                Intform.specialise()
        elif self.method=='GET':
            Intform=MyCouplingFormSet(model,simulation,queryset)
            Intform.specialise()
        labelstr='Coupling for %s'%model
        if simulation: labelstr+=' (in %s)'%simulation
        return render_to_response('coupling.html',{'c':model,'s':simulation,'urls':self.urls,
        'Intform':Intform,
        'tabs':tabs(self.request,self.centre_id,labelstr)})
        
    def resetClosures(self,simulation_id,coupling_id,ctype):
        logging.info('Deprecated reset closure method used for %s'%ctype)
        coupling=Coupling.objects.get(id=coupling_id)
        reset=ClosureReset(self.centre_id,simulation_id,coupling,ctype)
        return reset.reset()
    
    def update(self,coupling_id):
        ''' Used to update just one coupling, probably as an ajax activity '''
        pass

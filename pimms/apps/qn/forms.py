from django import forms
from django.forms.models import modelformset_factory, BaseModelFormSet

from pimms.apps.qn.dropdown import *
#from pimms.apps.qn.fields import *
from pimms.apps.qn.models import *
#from pimms.apps.qn.utilities import atomuri
from pimms.apps.qn.modelUtilities import uniqueness, refLinkField
from pimms.apps.qn.autocomplete import TermAutocompleteField


class ConformanceForm(forms.ModelForm):
    
    description    = forms.CharField(widget=forms.Textarea(attrs={'cols':"80",'rows':"3"}), required=False) 
    # We need the queryset, note that the queryset is limited in the specialisation
    q1, q2, q3, q4 = CodeMod.objects.all(), Coupling.objects.all(), Term.objects.all(), RequirementOption.objects.all()
    mod            = forms.ModelMultipleChoiceField(required=False, queryset=q1, widget=DropDownWidget(attrs={'size':'3'}))
    coupling       = forms.ModelMultipleChoiceField(required=False, queryset=q2, widget=DropDownWidget(attrs={'size':'3'}))
    ctype          = forms.ModelChoiceField(required=False, queryset=q3, widget=DropDownSingleWidget)
    option         = forms.ModelChoiceField(required=False, queryset=q4, widget=DropDownSingleWidget)
    
    class Meta:
        model   = Conformance
        exclude = ('simulation')
        
    def specialise(self, simulation):
        #http://docs.djangoproject.com/en/dev/ref/models/querysets/#in
        #relevant_components=Component.objects.filter(model=simulation.model)
        self.fields['mod'].queryset = simulation.codeMod.all()
        groups = CouplingGroup.objects.filter(simulation=simulation)  # we only expect one
        #it's possible we might end up trying to add conformances with no inputs ....
        if len(groups) <> 0:
            assert (len(groups)==1, 'Simulation %s should have one or no coupling groups' %simulation)
            self.fields['coupling'].queryset = Coupling.objects.filter(parent=groups[0])
        else:
            self.fields['coupling'].queryset = []
        v = Vocab.objects.get(name='ConformanceTypes')
        self.fields['ctype'].queryset = Term.objects.filter(vocab=v)
        self.fields['option'].queryset = GenericNumericalRequirement.objects.get(id=self.instance.requirement_id).options.all()
        self.showMod = len(self.fields['mod'].queryset)
        self.showCoupling = len(self.fields['coupling'].queryset)
        self.showOptions = len(self.fields['option'].queryset)
    
    def clean_option(self):
        '''
        adding an additional validation that checks the req option is filled 
        out when a conformance type has been selected
        '''
        # get current info from cleaned data
        cleaned_data = self.cleaned_data
        cd_ctype = cleaned_data.get("ctype")
        cd_option = cleaned_data.get("option")
        # check for missing option in case of ctype and report error
        if len(GenericNumericalRequirement.objects.get(id=self.instance.requirement_id).options.all()):
            if cd_ctype and str(cd_ctype) != 'Not Applicable' and str(cd_ctype) != 'Not Conformant' and cd_option is None:
                raise forms.ValidationError("A requirement option must be selected")
        
        return cd_option
            

class CouplingForm(forms.ModelForm):
    ''' 
    '''
    manipulation = forms.CharField(widget=forms.Textarea({'cols':'120','rows':'2'}), required=False)
    notInUse     = forms.BooleanField(required=False)
    
    def __init__(self, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        
        for k in ('parent', 'targetInput', 'original'):
            self.fields[k].widget = forms.HiddenInput()
    
    class Meta:
        model = Coupling
        
        
class InternalClosureForm(forms.ModelForm):
    ''' '''
    class Meta:
        model = InternalClosure
    
    def specialise(self):
        pass


class ExternalClosureForm(forms.ModelForm):    
    ''' '''
    class Meta:
        model = ExternalClosure
        
    def specialise(self):
        # GD - making sure targetfiles are only within the current centre
        if self.instance.targetFile:
            self.fields['targetFile'].queryset = DataContainer.objects.filter(centre=self.instance.targetFile.centre)
        if self.instance.targetFile:
            self.fields['target'].queryset = DataObject.objects.filter(container=self.instance.targetFile)
    
    def clean_targetFile(self):
        '''
        adding an additional validation that checks the file title is supplied
        '''
        # get current info from cleaned data
        value = self.cleaned_data['targetFile']
        # check for missing targetfile
        if value is None:
            raise forms.ValidationError("A file must be selected")
        
        return value


class ComponentForm(forms.ModelForm):
    ''' '''
    # it appears that when we explicitly set the layout for forms, we have to 
    # explicitly set required=False, it doesn't inherit that from the model as 
    # it does if we don't handle the display.
    
    abbrev         = forms.CharField() #widget is specialised below
    description    = forms.CharField(widget=forms.Textarea(attrs={'cols':"80", 'rows':"4"}), required=False)
    geneology      = forms.CharField(widget=forms.Textarea(attrs={'cols':"80", 'rows':"4"}), required=False)
    title          = forms.CharField(max_length=128, widget=forms.TextInput(attrs={'size':'80'}), required=True)
    implemented    = forms.BooleanField(required=False)
    yearReleased   = forms.IntegerField(widget=forms.TextInput(attrs={'size':'4'}), required=False)
    otherVersion   = forms.CharField(widget=forms.TextInput(attrs={'size':'40'}), required=False)
    controlled     = forms.BooleanField(widget=forms.HiddenInput, required=False)
    
    class Meta:
        model = Component
        exclude = ('qn', 'uri', 'model', 'realm', 'isRealm', 'isModel', 
                   'isParamGroup', 'visited', 'references', 'components', 
                   'paramGroup', 'isComplete')
    
    def __init__(self, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        
        qs = ResponsibleParty.objects.filter(qn=self.instance.qn)
        for i in ['author', 'contact', 'funder']: 
            self.fields[i].queryset = qs
        
        self.fields['grid'].queryset = Grid.objects.filter(qn=self.instance.qn).filter(
                                    istopGrid=True).filter(isDeleted=False)
        
        # allowing for name dropdown on top level model only
        if self.instance.isModel:
            self.fields['abbrev'].widget = forms.TextInput(attrs={'class':'inputH1'})
        else:
            self.fields['abbrev'].widget = forms.TextInput(attrs={'class':'inputH2'})
        
        if self.instance.controlled: 
            # We don't want this to be editable 
            self.fields['scienceType'].widget = forms.HiddenInput()
            self.viewableScienceType = self.instance.scienceType
            # implementable only matters if it's controlled
            self.showImplemented = True
        else:
            self.fields['scienceType'].widget = forms.TextInput(
                                                    attrs={'size':'40'})
            self.viewableScienceType = ''
            self.showImplemented = False
    
    def clean_abbrev(self):
        ''' 
        validation checks for model short name
        '''
            
        # abbrev name needs to be unique within a particular questionnaire
        value = self.cleaned_data['abbrev']
        m = Component.objects.filter(qn=self.instance.qn).filter(isDeleted=False).filter(isModel=True)
        
        ModelList=[]
        for x in m:
            ModelList.append(x.abbrev)
            
        # In the case of a page update, ignore the currently valid component 
        # name
        if self.instance.abbrev in ModelList:
            ModelList.remove(self.instance.abbrev)
        
        if value in ModelList:
            raise ValidationError('Model name must be unique from other Model names')
        
        return value
    

class ComponentInputForm(forms.ModelForm):
    ''' '''
    description   = forms.CharField(max_length=128, widget=forms.TextInput(attrs={'size':'60'}), required=False)
    abbrev        = forms.CharField(max_length=24, widget=forms.TextInput(attrs={'size':'24'}), required=True)
    units         = forms.CharField(widget=forms.TextInput(attrs={'size':'48'}), required=False)
    #cfname        = TermAutocompleteField(Vocab, 'CFStandardNames', Term, required=False, size=60)
 
    class Meta:
        model=ComponentInput
        exclude=('owner', 'realm') # we know these
    
    def __init__(self, *args, **kwargs):       
        forms.ModelForm.__init__(self, *args, **kwargs)
        v = Vocab.objects.get(name='InputTypes')
        self.fields['ctype'].queryset = Term.objects.filter(vocab=v)
        # this can't go in the attributes section, because of import issues, deferring it works ...    
           
           
class DataContainerForm(forms.ModelForm):
    ''' 
    This is the form used to edit "files" ... 
    '''
    title       = forms.CharField(widget=forms.TextInput(attrs={'size':'45'}))
    #link       = extURLField(widget=forms.TextInput(attrs={'size':'45'}), required=False)
    link        = URLField(required=False)
    description = forms.CharField(widget=forms.Textarea({'cols':'50', 'rows':'4'}), required=False)
    
    class Meta:
        model = DataContainer
        exclude = ('centre', 'dataObject', 'funder', 'author', 'contact', 'metadataMaintainer')
    
    def __init__(self, qn, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        v = Vocab.objects.get(name='FileFormats', qn=qn)
        self.fields['format'].widget = DropDownSingleWidget()
        self.fields['format'].queryset = Term.objects.filter(vocab=v)
        self.fields['experiments'].widget = DropDownWidget()
        self.fields['experiments'].queryset = Experiment.objects.all().filter(isDeleted=False)
        self.hostCentre=None
    
    def specialise(self, qn):
        self.fields['reference'].widget = DropDownSingleWidget()
        self.fields['reference'].queryset = Reference.objects.filter(qn=qn)   #|Reference.objects.filter(centre=None)
    
    def save(self):
        ''' Need to add the centre, and save the subform too '''
        o=forms.ModelForm.save(self,commit=False)
        o.centre=self.hostCentre
        o.save()
        return o
    
    def clean(self):
        ''' Needed to ensure name uniqueness within a centre, and handle the subform '''
        return uniqueness(self,self.hostCentre,'title')


class DataObjectForm(forms.ModelForm):
    '''
    '''
    description = forms.CharField(widget=forms.Textarea({'cols':'50', 'rows':'2'}), required=False)
    variable    = forms.CharField(widget=forms.TextInput(attrs={'size':'45'}))
    #cfname      = TermAutocompleteField(Questionnaire, Vocab, 'CFStandardNames', Term, required=False, size=50)
    
    class Meta:
        model = DataObject
        exclude = ('featureType', 'drsAddress', 'container')
        
    def __init__(self, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        self.qn = None
    
    def specialise(self, qn):
        self.fields['reference'].queryset = Reference.objects.filter(qn=qn)    #|Reference.objects.filter(qn=None)
        
        
class DataHandlingForm(object):
    ''' 
    This is a fudge to allow baseview to think it's dealing with one form, 
    when it's really dealing with two
    '''
    
    # Base view will send datacontainer objects as the instance... we need to handle them,
    # and the objects within them, and the request
    DataObjectFormSet = modelformset_factory(DataObject, form=DataObjectForm, can_delete=True)
    
    def __init__(self, postData=None, instance=None):
        self.cform = DataContainerForm(postData, instance=instance, prefix='cform')
        if instance:
            qset = DataObject.objects.filter(container=instance)
        else:
            qset = DataObject.objects.none()
        
        self.oform=self.DataObjectFormSet(postData,queryset=qset,prefix='oform')
        self.hostCentre=None
        
    def is_valid(self):
        return self.cform.is_valid() and self.oform.is_valid()
        
    def specialise(self,constraints):
        self.cform.specialise(constraints)
        for f in self.oform.forms:
            f.specialise(constraints)
            
    def save(self):
        c = self.cform.save()
        oset = self.oform.save(commit=False)
        for o in oset: 
            o.container = c
            o.save()
        
        return c
    
    def handleError(self):
        return str(self.cform.errors) + str(self.oform.errors)
    
    def getCentre(self):
        return self.cform.hostCentre
    
    def setCentre(self,val):
        self.oform.hostCentre = val
        self.cform.hostCentre = val
    
    errors = property(handleError, None)
    hostCentre = property(getCentre, setCentre)


#class EnsembleForm(forms.ModelForm):
#    description=forms.CharField(widget=forms.Textarea({'cols':'80','rows':'4'}),required=False)
#    riphidden = forms.BooleanField(required=False)
#    class Meta:
#        model=Ensemble
#        exclude=('simulation')
#    def __init__(self,*args,**kwargs):
#        logging.debug('initialising ensemble form')
#        forms.ModelForm.__init__(self,*args,**kwargs)
#        self.fields['etype'].queryset=Term.objects.filter(vocab=Vocab.objects.get(name='EnsembleTypes'))
#
#
#class EnsembleMemberForm(forms.ModelForm):
#    drsMember=forms.CharField(max_length=12,widget=forms.TextInput(attrs={'size':'12'}))
#    # Currently not asking for data file version information
#    #dataVersion=forms.IntegerField(widget=forms.TextInput(attrs={'size':'16'}),required=False)
#    
#    class Meta:
#        model=EnsembleMember
#    
#    def __init__(self,*args,**kwargs):
#        forms.ModelForm.__init__(self,*args,**kwargs)
#        logging.debug('initialising ensemble set')
#        if self.instance:
#            # find the set of modifications which are appropriate for the 
#            # current centre
#            etype=self.instance.ensemble.etype
#            vet=Vocab.objects.get(name='EnsembleTypes')
#            self.fields['cmod'].queryset=CodeMod.objects.filter(
#                                centre=self.instance.ensemble.simulation.centre)
#            self.fields['imod'].queryset=InputMod.objects.filter(
#                                centre=self.instance.ensemble.simulation.centre)
#    
#    def clean_drsMember(self):
#        # needs to parse into DRS member format
#        value=self.cleaned_data['drsMember']
#        p=re.compile(r'(?P<r>\d+)i(?P<i>\d+)p(?P<p>\d+)$')
#        try:
#            m=p.search(value)
#            [r,i,p]=map(int,[m.group('r'),m.group('i'),m.group('p')])
#            return value
#        except:
#            raise ValidationError('Please enter a valid CMIP5 ensemble member \
#                                   string of the format rLiMpN where L,M and \
#                                   N are integers')
#    
#    def specialise(self,requirementset):
#        ''' 
#        Limits the numerical requirements to only those within the 
#        requirement set 
#        '''
#        if requirementset:
#            self.fields['requirement'].queryset=requirementset.members.all()
#
#
#class BaseEnsembleMemberFormSet(BaseModelFormSet):
#    def clean(self):
#        ''' 
#        Checks that no two ensemble members have the same drs string 
#        '''
#        if any(self.errors):
#            # Don't bother validating the formset unless each form is valid on 
#            # its own
#            return
#        drsnums = []
#        #Start by adding the main simulation rip value
#        ensemb = self.forms[0].save(commit=False).ensemble
#        #ensemb = model_instance.ensemble
#        simrip = ensemb.simulation.drsMember
#        drsnums.append(simrip)
#        for i in range(0, self.total_form_count()):
#            form = self.forms[i]
#            drsn = form.cleaned_data['drsMember']
#            if drsn in drsnums:
#                raise ValidationError('''
#                Ensemble members must have distinct rip values. This includes 
#                the rip value given for the simulation itself. 
#                ''')
#            drsnums.append(drsn)
#        
#        # Now also check for matching rip values in linked simulations (i.e. in 
#        # cmip5 drs terms
#        mysim = ensemb.simulation
#        mycentre = mysim.centre
#        mymodel = mysim.numericalModel
#        myexp = mysim.experiment
#        
#        # grab the startdate also for checking the decadal experiments
#        mystartdate = str(ensemb.simulation.duration.startDate).partition('-')[0]
#        
#        # search through expgroups to decide if I am part of a linked experiment
#        for expgroup in expgroups:
#            #make a copy of the inner list (for possible editing) 
#            myexpgroup = list(expgroup)
#            if myexp.abbrev in myexpgroup:
#                #mark that it has been found
#                expfound = True
#                # remove the current sim from the group, then break
#                #myexpgroup.remove(myexp.abbrev)
#                break
#            else:
#                expfound = False
#        
#                
#        if expfound:
#            #collect all current rip values
#            linkedrips = []    
#            for exp in myexpgroup:
#                linkedsims = Simulation.objects.filter(
#                                centre=mycentre).filter(
#                                numericalModel=mymodel).filter(
#                                experiment__abbrev__exact=exp).filter(
#                                isDeleted=False)
#                
#                # remove the current sim if it is in current queryset, i.e. if 
#                # this isn't a new sim being created
#                if mysim in linkedsims:
#                    linkedsims = linkedsims.exclude(id=mysim.id)
#                
#                # in the case of decadal exps, only check across sims with the 
#                # same start year, i.e. a decadal1960 can have the same rip 
#                # values as a decadal1965
#                for linkedsim in linkedsims:
#                    if exp.partition(' ')[2] == 'decadal' and \
#                      str(linkedsim.duration.startDate).partition('-')[0] != mystartdate:
#                        linkedsims = linkedsims.exclude(id=linkedsim.id)
#                
#                for simul in linkedsims:
#                    #add the rip value of the simulation
#                    linkedrips.append(simul.drsMember)
#                    #get my ensemblemember rip values
#                    ensem = Ensemble.objects.get(simulation = simul)
#                    allmems = EnsembleMember.objects.filter(ensemble=ensem)
#                    for ensmem in allmems[1:]:
#                        #add the rip value of the ensemble member
#                        linkedrips.append(ensmem.drsMember)
#                    
#            # do any of the rip values appear in this linked sim?
#            for i in range(0, self.total_form_count()):
#                form = self.forms[i]
#                drsn = form.cleaned_data['drsMember']
#                if drsn in linkedrips:
#                    raise ValidationError("This rip value is already used in \
#                                           the linked simulation '%s' being \
#                                           run for experiment '%s'" 
#                                           %(simul, simul.experiment))

        
class ModForm(forms.ModelForm):
    '''
    '''
    mnemonic    = forms.CharField(widget=forms.TextInput(attrs={'size':'25'}))
    description = forms.CharField(widget=forms.Textarea({'cols':'80', 'rows':'4'}))
    
    def __init__(self, *args, **kwargs):  
        forms.ModelForm.__init__(self, *args, **kwargs)
        self.qn = None
        
    def save(self, attr=None):
        o = forms.ModelForm.save(self, commit=False)
        o.qn = self.qn
        if attr is not None:
            o.__setattr__(attr[0], attr[1])
        o.save()
        return o
    
    def clean(self):
        ''' 
        Needed to ensure reference name uniqueness within a project 
        '''
      
        return uniqueness(self, self.qn, 'mnemonic')
        

#class InputClosureModForm(forms.ModelForm):
#    '''
#    '''
#  
#    class Meta:
#        model    = InputClosureMod
#        exclude  = 'targetClosure'  # that's set by the input modd
#    
#    def specialise(self):
#         if self.instance.targetFile:
#            self.fields['target'].queryset = DataObject.objects.filter(container=self.instance.targetFile)
            
                 
class InputModForm(ModForm):
    #memberStartDate=SimDateTimeFieldForm2()
    class Meta:
        model   = InputMod
        exclude = ('centre', 'dataset', 'dataRelationship')
        #we're not using datasets at the moment
    
    def __init__(self, *args, **kwargs):
        ModForm.__init__(self, *args, **kwargs)
        self.ivocab = Vocab.objects.get(name='InputTypes')
        self.ic = Term.objects.filter(vocab=self.ivocab).get(name='InitialCondition')
    
    def specialise(self, group):
        self.group = group
        self.simulation = group.simulation
        self.fields['inputTypeModified'].queryset = Term.objects.filter(vocab=self.ivocab)
        self.fields['memberStartDate'].initial = self.simulation.duration.startDate
    def save(self):
        f = ModForm.save(self, attr=('mtype', self.ic))
        self.save_m2m()
        
        return f
        
    
class InputModIndex(object):
    ''' 
    Used to bundle the form and child formsets together to help base view 
    '''
       
    def __init__(self, postData=None, instance=None):
        self.master = InputModForm(postData, instance=instance, prefix='mform')
        self.hostCentre = None
        
    def specialise(self, simulation):
        self.cg = CouplingGroup.objects.get(simulation=simulation)
        self.s = simulation
        self.master.specialise(self.cg)
    
    def is_valid(self):
        return self.master.is_valid()
    
    def save(self):
        m = self.master.save()
        return m
    
    def handleError(self):
        return self.master.errors
    
    def getCentre(self):
        return self.master.hostCentre
    
    def setCentre(self,val):
        self.master.hostCentre = val
     
    errors = property(handleError, None)
    hostCentre = property(getCentre, setCentre)  
 
 
class CodeModForm(ModForm):
    '''
    '''
    #ivocab = Vocab.objects.get(name='ModelModTypes', qn=self.qn)
    #mtype = forms.ModelChoiceField(queryset=Term.objects.filter(vocab=ivocab), required=True)
    
    class Meta:
        model = CodeMod
        exclude = ('centre', 'mods')  # ignoring mods for now ...
    
    def specialise(self, model, qn):
        self.fields['component'].queryset = Component.objects.filter(model=model).filter(isDeleted=False)
        ivocab = Vocab.objects.get(name='ModelModTypes', qn=qn)
        self.fields['mtype'].queryset=Term.objects.filter(vocab = ivocab)


class PlatformForm(forms.ModelForm):
    '''
    Form for a computing platform
    '''      
   
    description = forms.CharField(widget=forms.Textarea(attrs={'class':'optin', 'cols':"60", 'rows':"4"}), required=False)
    maxProcessors = forms.IntegerField(widget=forms.TextInput(attrs={'class':'optin', 'size':10}), required=False)
    coresPerProcessor = forms.IntegerField(widget=forms.TextInput(attrs={'class':'optin', 'size':10}), required=False)
    
    class Meta:
        model = Platform
        exclude = ('qn', 'uri', 'metadataMaintainer')        
     
        
class ReferenceForm(forms.ModelForm):
    '''
    '''
    citation = forms.CharField(widget=forms.Textarea({'cols':'140', 'rows':'2'}))
    #link=forms.URLField(widget=forms.TextInput(attrs={'size':'55'}))
    link=refLinkField(widget=forms.TextInput(attrs={'size':'55'}),required=False)
    
    class Meta:
        model   = Reference
        exclude = ('qn', )
        
    def __init__(self, qn, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        v = Vocab.objects.get(name='ReferenceTypes', qn=qn)
        self.fields['refType'].queryset = Term.objects.filter(vocab=v)
        self.hostQn = None
        
    def save(self):
        r = forms.ModelForm.save(self, commit=False)
        r.qn = self.hostQn
        r.save()
        return r
      
    def specialise(self,centre):
        pass
      
    def clean(self):
        ''' 
        Needed to ensure reference name uniqueness within a qn
        '''
        return uniqueness(self, self.hostQn, 'name')
        
        
class ResponsiblePartyForm(forms.ModelForm):
    '''
    '''
    email    = forms.EmailField(widget=forms.TextInput(attrs={'size':'80'}), required=False)
    webpage  = forms.CharField(widget=forms.TextInput(attrs={'size':'80'}), required=False)
    name     = forms.CharField(widget=forms.TextInput(attrs={'size':'80'}))
    abbrev   = forms.CharField(widget=forms.TextInput(attrs={'size':'24'}))
    address  = forms.CharField(widget=forms.Textarea(attrs={'cols':"80", 'rows':"4"}), required=False)
    uri      = forms.CharField(widget=forms.HiddenInput(), required=False)
    
    class Meta:
        model   = ResponsibleParty
        exclude = ('qn')
    
    def __init__(self, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        self.hostQn = None
    
    def clean_uri(self):
        ''' 
        On creating a responsible party we need a uri, once we have one, it should stay the same 
        '''
        data = self.cleaned_data['uri']
        if data == u'': 
            data = atomuri()
        
        return data
    
    def save(self):
        r = forms.ModelForm.save(self, commit=False)
        r.centre = self.hostQn
        r.save()
        return r
               
                              
class SimulationForm(forms.ModelForm):
    # It appears that when we explicitly set the layout for forms, we have to 
    # explicitly set required=False, it doesn't inherit that from the model as 
    # it does if we don't handle the display.
    description = forms.CharField(widget=forms.Textarea({'cols': "100", 'rows': "4"}), required=False)
    title       = forms.CharField(widget=forms.TextInput(attrs={'size': '80'}), required=False)
    authorList  = forms.CharField(widget=forms.Textarea({'cols': "100", 'rows':"4"}))
    duration    = DateRangeFieldForm2()
    drsMember   = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'size': '25'}))
    # Currently not asking for data file version information
    
    class Meta:
        model=Simulation
        # The first three are enforced by the workflow leading to the form, 
        # the second two are dealt with on other pages. NB: note that if you 
        # don't exclude things, then a form will expect them, and set them to 
        # None if they don't come back in the post ... a quiet
        # loss of information ...
        exclude=('qn', 'experiment', 'uri', 'codeMod', 'inputMod', 
                 'relatedSimulations', 'drsOutput', 'datasets', 'isComplete')
       
    
    def clean_drsMember(self):
        '''
        Checks for uniqueness and correct format of a simulation level rip 
        value. The uniqueness test applies to ensemble members within the 
        simulation itself as well as any linked simulations (by cmip5 exp)        
        '''
        value = self.cleaned_data['drsMember']
        #grab the startdate also for checking the decadal experiments in 3 below
        #startdate = str(self.cleaned_data['duration'].startDate).partition('-')[0]
        
        # 1. check for correct drs format
        p=re.compile(r'(?P<r>\d+)i(?P<i>\d+)p(?P<p>\d+)$')
        try:
            m=p.search(value)
            [r, i, p] = map(int, [m.group('r'), m.group('i'), m.group('p')])
        except:
            raise ValidationError('Please enter a valid CMIP5 ensemble member \
                string of the format rLiMpN where L,M and N are integers')
            
        # 2. check that no ensemble members (of this simulation) exist with the 
        # same rip value
        simul = self.instance
        try:
            ensem = Ensemble.objects.get(simulation = simul)
            allmems = EnsembleMember.objects.filter(ensemble=ensem)
            #collect all current rip values
            ensrips = []
            for mem in allmems[1:]:
                ensrips.append(mem.drsMember)
            if value in ensrips:
                raise ValidationError('This rip value is already used in one \
                                       of the ensemble members')
        except:
            logging.debug('This is a new simulation, hence no ensemble members \
                            to test as of yet ')
               
        # grab the startdate also for checking the decadal experiments
        try: 
            mystartdate = str(self.cleaned_data['duration'].startDate).partition('-')[0]
        except:
            raise ValidationError('A valid start date is needed in Duration')
        
        if mystartdate == 'None':
                raise ValidationError('A valid start date is needed in Duration')
                    
        return value
    
    
    def clean_abbrev(self):
        value=self.cleaned_data['abbrev']
        
        # first check that the abbreviation is not being changed when a 
        # simulation has already been published (as this affects Curator 
        # trackback display)
        currentname = self.instance.abbrev
        if currentname != '' and currentname != value: #i.e. a change
            if CIMObject.objects.filter(uri=self.instance.uri):
                raise ValidationError('Changing the short name of an already \
                                   published simulation is not allowed ')
        
        # abbrev name needs to be unique within a particular centre
        s=Simulation.objects.filter(centre=self.instance.centre).filter(
                                                                isDeleted=False)
        
        SimulList=[]
        for x in s:
            SimulList.append(x.abbrev)
        # In the case of a page update, ignore the currently valid simulation 
        # name
        if self.instance.abbrev in SimulList:
            SimulList.remove(self.instance.abbrev)
        if value in SimulList:
            raise ValidationError('Simulation name must be unique from other \
                                   simulation names')
        return value
    
    
    def clean_title(self):
        '''
        Check that the title (long name) text is less than 128 characters
        '''
         
        value=self.cleaned_data['title']
        
        if len(value) > 128:
            raise ValidationError('Long name text must be less than 128 \
                                   characters')
        
        return value
    
    def specialise(self, qn):
        self.fields['platform'].queryset = Platform.objects.filter(qn=qn).filter(isDeleted=False)
        self.fields['numericalModel'].queryset = Component.objects.filter(scienceType='model').filter(qn=qn).filter(isDeleted=False)
        qs = ResponsibleParty.objects.filter(qn=qn)
        
        for i in ['author', 'funder', 'contact']: 
            self.fields[i].queryset = qs
        
        self.fields['contact'].required = True 
    
    def save(self):
        s=forms.ModelForm.save(self)
        try:
            e=Ensemble.objects.get(simulation=s)
        except:
            #couldn't find it? create it!
            e=Ensemble(simulation=s)
            e.save()
        e.updateMembers()
        return s
        
        
class SimRelationshipForm(forms.ModelForm):
    '''
    '''
    
    description = forms.CharField(widget=forms.Textarea({'cols':"80", 'rows':"2"}), required=False)
    
    class Meta:
        model    = SimRelationship
        exclude  = ('vocab', 'sfrom')
    
    def __init__(self, simulation, qn, *args, **kwargs):
        self.simulation = simulation
        self.vocab      = Vocab.objects.get(name='SimRelationships', qn=qn)
        
        forms.ModelForm.__init__(self,*args,**kwargs)
        self.fields['value'].queryset = Term.objects.filter(vocab=self.vocab)
        self.fields['sto'].queryset = Simulation.objects.filter(centre=self.simulation.centre).filter(isDeleted=False)
    
    def clean(self):
        tmp = self.cleaned_data.copy()
        
        for k in 'value', 'sto':
            if k in tmp:
                if tmp[k] is None: 
                    del tmp[k]
        
        if 'sto' in tmp or 'value' in tmp:
            if 'sto' not in tmp or 'value' not in tmp:
                raise forms.ValidationError('Need both related simulation and relationship')
        
        return self.cleaned_data
    
    def save(self):
        s = forms.ModelForm.save(self, commit=False)
        s.sfrom = self.simulation
        s.save()
        

class GridForm(forms.ModelForm):
    ''' '''
    abbrev       = forms.CharField(widget=forms.TextInput(attrs={'class':'inputH1'}))
    description  = forms.CharField(widget=forms.Textarea(attrs={'cols':"80",'rows':"4"}), required=False)
    title        = forms.CharField(widget=forms.TextInput(attrs={'size':'80'}), required=True)
    
    class Meta:
        model = Grid
        exclude = ('qn', 'uri', 'topGrid', 'istopGrid', 'references', 'grids', 'paramGroup', 'isParamGroup')   
    
    def __init__(self, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        
        qs = ResponsibleParty.objects.filter(qn=self.instance.qn)
        for i in ['author','contact','funder']: 
            self.fields[i].queryset = qs

        
class BaseParamForm(forms.ModelForm):
    class Meta:
        model = BaseParam
        exclude = ['controlled', 'definition', 'constraint']
    
    def __init__(self, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        #self.fields['constraint'].widget=forms.HiddenInput()
        if self.instance:
            self.showname = {0:False, 1:True}[self.instance.controlled]
        else: 
            self.showname = False
            
        if self.showname:
            self.fields['name'].widget = forms.HiddenInput()
        else:
            self.fields['name'].widget = forms.TextInput(attrs={'size':'36'})


class OrParamForm(BaseParamForm):
    value = forms.ModelMultipleChoiceField(queryset=Term.objects.all(), widget=forms.SelectMultiple(attrs={'size': 3}), required=False)
    
    class Meta(BaseParamForm.Meta):
        model = OrParam
        exclude = BaseParamForm.Meta.exclude+['vocab']
    
    def __init__(self, *args, **kwargs):
        BaseParamForm.__init__(self, *args, **kwargs)
        # These always have instances.
        self.fields['value'].queryset = Term.objects.filter(vocab=self.instance.vocab).order_by('id')
        self.model = 'OR'
    
    
class XorParamForm(BaseParamForm):
    value = forms.ModelChoiceField(queryset=Term.objects.all(), widget=DropDownSingleWidget(), required=False)
    
    class Meta(BaseParamForm.Meta):
        model = XorParam
        exclude = BaseParamForm.Meta.exclude+['vocab']
    
    def __init__(self, *args, **kwargs):
        BaseParamForm.__init__(self, *args, **kwargs)
        # These always have instances
        self.fields['value'].queryset = Term.objects.filter(vocab=self.instance.vocab).order_by('id')
        self.model = 'XOR'
   
     
class KeyBoardParamForm(BaseParamForm):
    value = forms.CharField(max_length=1024, widget=forms.TextInput(attrs={'size':'64'}), required=False)
    
    class Meta(BaseParamForm.Meta):
        model = KeyBoardParam
        exclude = BaseParamForm.Meta.exclude+['numeric', 'units']
    def __init__(self, *args, **kwargs):
        BaseParamForm.__init__(self, *args, **kwargs)
        self.model = 'Keyboard'
    
    
class ParamGroupForm:
    ''' 
    This is an aggregation form for handling the multiple forms that will appear
    on a component layout page 
    '''
    
    UserFormSet = modelformset_factory(KeyBoardParam, form=KeyBoardParamForm, can_delete=True)
    
    def __init__(self, component, POST=None, prefix=''):
        self.prefix = prefix
        self.component = component
        self.pgset = self.component.paramGroup.all().order_by('id')
        
        fid = 0 # a form id, so we get unique forms for each parameter 
        for pg in self.pgset:
            pg.cgset = []
            for cg in pg.constraintgroup_set.all().order_by('id'):
                pg.cgset.append(cg)
                cg.forms = []
                for p in cg.baseparam_set.filter(controlled=True).order_by('id'):
                    fid += 1
                    n = p.get_child_name() # kill this line when we know it works
                    f = {'orparam':OrParamForm, 'xorparam':XorParamForm, 'keyboardparam':KeyBoardParamForm}[p.get_child_name()]
                    cg.forms.append(f(POST,instance=p.get_child_object(),prefix='%s-%s'%(prefix,fid)))
            # Get direct to uncontrolled keyboards for the last constraint group in a param group
            q=KeyBoardParam.objects.filter(constraint=cg).filter(controlled=False).order_by('id')
            #if len(q):
            logging.debug('Userparams for %s in %s'%(cg.id,pg))
            cg.userforms=self.UserFormSet(POST,queryset=q,prefix='%s-uf-%s'%(prefix,cg.id))
            #else:
            #    cg.userforms=None  
                 
    def save(self):
        ''' Try and save what we can, return status, and return form for reuse '''
        ok=True
        for pg in self.pgset:
            for cg in pg.cgset:
                for p in cg.forms:
                    pok=p.is_valid()
                    if pok:
                        p.save()
                    else:
                        logging.debug('%s:\n%s'%(p,p.errors))
                        ok=False
            # The last one has a userforms parameter set
            # (adding an initial check that these are present as grids page means they don't have to be
            
            #if cg.userforms is not None:
            if cg.userforms.is_valid():
                instances=cg.userforms.save(commit=False)
                for uf in instances:
                    uf.constraint=cg
                    uf.save()
                # now build a new userform in case the overarching form is not ok, to avoid sending the
                # same userform formset over and over again (and multiply entering the same stuff).
                q=KeyBoardParam.objects.filter(constraint=cg).filter(controlled=False)
                cg.userforms=self.UserFormSet(queryset=q,prefix='%s-uf-%s'%(self.prefix,cg.id))
            else: 
                ok=False
        return ok
                
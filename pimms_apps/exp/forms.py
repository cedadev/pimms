'''
Created on 17 Aug 2011

@author: gerarddevine
'''

from django import forms
from django.forms import ModelForm
from django.forms.widgets import CheckboxSelectMultiple

from pimms.apps.exp.models import Experiment, NumericalRequirement


class ExperimentForm(ModelForm):
    def __init__(self, *args, **kwargs):
      user = kwargs.pop('user', None)
      self.validate = kwargs.pop('validate', False)
      super(ExperimentForm, self).__init__(*args, **kwargs)

      self.fields['requirements'].queryset = NumericalRequirement.objects.filter(author=user)

    class Meta:
        model = Experiment
        exclude = ('author',) 
        widgets = {
            'abbrev': forms.TextInput(attrs={'class':'input-xlarge'}),
            'title': forms.TextInput(attrs={'class':'input-xlarge'}),
            #'author': forms.TextInput(attrs={'class':'input-xlarge'}),
            'project': forms.TextInput(attrs={'class':'input-xlarge'}),
            'description': forms.Textarea(attrs={'class':'input-xlarge'}),
            'rationale': forms.Textarea(attrs={'class':'input-xlarge'}),
            'requirements': CheckboxSelectMultiple(),
        }        
        
        
class RequirementForm(ModelForm):
    CHOICES = (('--------------','-------------'),
               ('BoundaryCondition','Boundary Condition'),
               ('InitialCondition','Initial Condition'),
               ('SpatioTemporalConstraint','SpatioTemporal Constraint'),)
    
    reqtype = forms.CharField(widget=forms.Select(choices=CHOICES, attrs={'size':'1', 'class':'input-xlarge'}))


    class Meta:
        model = NumericalRequirement
        exclude = ('author',) 
        widgets = {
            'name': forms.TextInput(attrs={'class':'input-xlarge'}),
            'docid': forms.TextInput(attrs={'class':'input-xlarge'}),
            'description': forms.Textarea(attrs={'class':'input-xlarge'}),
        }
        
        
    def clean_reqtype(self):
        '''Check that an actual valid choice is selected'''
        reqtype = self.cleaned_data['reqtype']
        if reqtype == u'--------------':
            raise forms.ValidationError("This field is required")
          
        return reqtype 
        
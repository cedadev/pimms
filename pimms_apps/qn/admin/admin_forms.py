from django.forms import ModelForm
from django import forms
from pimms.apps.qn.models import *


class CompCopyForm(forms.Form):
    '''
    view for model copying from one centre to another
    '''
    
    centres = Centre.objects.all()
    comps = Component.objects.filter(isModel=True).filter(isDeleted=False)
    
    targetcentre = forms.ModelChoiceField(queryset=centres,  
                                          required=False)
    
    sourcemodel = forms.ModelChoiceField(queryset=comps, 
                                         required=False)
    


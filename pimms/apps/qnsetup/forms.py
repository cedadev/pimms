from django import forms

from pimms.apps.qnsetup.models import Questionnaire


class qnSetupForm(forms.ModelForm):
    ''' form class for collecting qn setup parameters
    
    '''
    class Meta:
        model = Questionnaire
        
        exclude = ('author', 'creator', 'cvs', 'creationDate') 

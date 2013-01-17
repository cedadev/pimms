from django import forms

from pimms.apps.qn.models import Questionnaire


class qnSetupForm(forms.ModelForm):
    ''' form class for collecting qn setup parameters
    
    '''
    class Meta:
        model = Questionnaire
        
        exclude = ('creator', 'cvs', 'exps', 'creationDate') 
        
        
class UploadCVForm(forms.Form):
    abbrev = forms.CharField(max_length=50)
    cvfile  = forms.FileField(required=False)
    

class UploadExpForm(forms.Form):
    abbrev = forms.CharField(max_length=50)
    expfile  = forms.FileField(required=False)
        
        
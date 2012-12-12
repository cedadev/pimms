from django import forms

from pimms.apps.qnsetup.models import Questionnaire


class qnSetupForm(forms.ModelForm):
    ''' form class for collecting qn setup parameters
    
    '''
    class Meta:
        model = Questionnaire
        
        exclude = ('author', 'creator', 'cvs', 'creationDate') 
        
        
class UploadCVForm(forms.Form):
    title = forms.CharField(max_length=50)
    cvfile  = forms.FileField(required=False)
    

class UploadExpForm(forms.Form):
    title = forms.CharField(max_length=50)
    expfile  = forms.FileField(required=False)
        
        
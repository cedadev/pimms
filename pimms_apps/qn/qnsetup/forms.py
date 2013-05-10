from django import forms
from pimms_apps.qn.models import Questionnaire


class qnSetupForm(forms.ModelForm):
    ''' 
    Form class for collecting qn setup parameters    
    '''
  
    class Meta:
        model = Questionnaire
        
        exclude = ('creator', 'cvs', 'exps', 'creationDate') 
        
        
class UploadCVForm(forms.Form):
    cvfile  = forms.FileField(required=False)


class UploadGridCVForm(forms.Form):
    gridcvfile  = forms.FileField(required=False)
    

class UploadExpForm(forms.Form):
    expfile  = forms.FileField(required=False)
        
        
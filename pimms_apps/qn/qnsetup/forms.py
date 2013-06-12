from django import forms
from pimms_apps.qn.models import Questionnaire

import re

VALID_PROJECT_REXP = r'^\D+$'

class qnSetupForm(forms.ModelForm):
    ''' 
    Form class for collecting qn setup parameters    
    '''
  
    class Meta:
        model = Questionnaire
        
        exclude = ('creator', 'cvs', 'exps', 'creationDate') 
        

    def clean(self):
        cleaned_data = super(qnSetupForm, self).clean()
        project = cleaned_data.get('project')

        if not re.match(VALID_PROJECT_REXP, project):
            self._errors['project'] = ['Projects cannot contain digits']
            raise forms.ValidationError('Invalid project name')

        return cleaned_data
        
class UploadCVForm(forms.Form):
    cvfile  = forms.FileField(required=False)


class UploadGridCVForm(forms.Form):
    gridcvfile  = forms.FileField(required=False)
    

class UploadExpForm(forms.Form):
    expfile  = forms.FileField(required=False)
        
        

from django import forms


class MMForm(forms.Form):
    ''' simple form class for mindmap file uploading
    
    '''
    mmfile = forms.FileField(required=False)
    igWarnings = forms.BooleanField(required=False)

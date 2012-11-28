from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm

from apps.person.models import Person


class RegistrationForm(ModelForm):
    
    username    = forms.CharField(label=(u'Username'))
    email       = forms.EmailField(label=(u'Email'))
    password1   = forms.CharField(label=(u'Password'), widget=forms.PasswordInput(render_value=False))
    password2   = forms.CharField(label=(u'Re-enter Password'), widget=forms.PasswordInput(render_value=False))
    
    class Meta:
        model = Person
        exclude = ('user',)
        
    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError("That username is taken")
    
        
    def clean(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("The passwords do not match")
        return self.cleaned_data
    

class LoginForm(forms.Form):
    ''' Username Password login form '''
    
    username        = forms.CharField(label=(u'Username'))
    password        = forms.CharField(label=(u'Password'), widget=forms.PasswordInput(render_value=False))
    
    
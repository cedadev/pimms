from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response
from django.template import RequestContext

from apps.person.forms import RegistrationForm, LoginForm
from apps.person.models import Person
from apps.helpers import genurls


def UserRegistration(request):
    ''' Registers credentials for a user '''
    
    # get my urls
    urls = genurls()
        
    if request.user.is_authenticated():
        return HttpResponseRedirect(urls['home'])
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(username=form.cleaned_data['username'],
                                                      email=form.cleaned_data['email'],
                                                      password=form.cleaned_data['password1'],)
            user.save()
            person = Person(user=user, 
                            firstname=form.cleaned_data['firstname'],
                            surname=form.cleaned_data['surname'], 
                            institute=form.cleaned_data['institute'])
            person.save()
            
            return HttpResponseRedirect(urls['home'])
        else:
            # get my urls
            urls = genurls()
            return render_to_response('page/register.html', {'form': form, 'urls':urls}, context_instance=RequestContext(request))
            
    else:
        ''' user is not submitting a form therefore show a registration form '''
        urls = genurls()
        form = RegistrationForm()
        context = {'form': form, 'urls':urls}
        return render_to_response('page/register.html', context, context_instance=RequestContext(request))
        

def LoginRequest(request):
    # get my urls
    urls = genurls()
    
    if request.user.is_authenticated():
        return HttpResponseRedirect(urls['home'])
    
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            person = authenticate(username=username, password=password)
            if person is not None:
                login(request, person)
                return HttpResponseRedirect(urls['explist'])
            else:
                error = "Username and Password do not match. Please try again"
                return render_to_response('page/login.html', {'form': form, 'error': error, 'urls': urls}, context_instance=RequestContext(request))
        else:
            return render_to_response('page/login.html', {'form': form, 'urls': urls}, context_instance=RequestContext(request))        
    else:
        ''' user is not submitting the form, therefore show the login form '''
        form = LoginForm()        
        context = {'form': form, 'urls':urls}
        return render_to_response('page/login.html', context, context_instance=RequestContext(request))
    
    
def LogoutRequest(request):
    logout(request)
    
    # get my urls
    urls = genurls()
    
    return HttpResponseRedirect(urls['home'])

    
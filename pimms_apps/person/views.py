from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response
from django.template import RequestContext

from pimms_apps.person.forms import RegistrationForm, LoginForm
from pimms_apps.person.models import Person
from pimms_apps.helpers import getsiteurls


def UserRegistration(request):
    ''' Registers credentials for a user '''
    
    # get my urls
    urls = {}
    urls = getsiteurls(urls)
        
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
            
            #automatically log this new person in 
            new_user = authenticate(username=request.POST['username'],
                                    password=request.POST['password1'])
            login(request, new_user)            
            return HttpResponseRedirect(urls['home'])
        else:
            return render_to_response('register.html', {'form': form, 'urls':urls}, context_instance=RequestContext(request))
            
    else:
        ''' user is not submitting a form therefore show a registration form '''
        form = RegistrationForm()
        context = {'form': form, 'urls':urls}
        return render_to_response('register.html', context, context_instance=RequestContext(request))
        

def LoginRequest(request):
    # get my urls
    urls = {}
    urls = getsiteurls(urls)
    
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
                return HttpResponseRedirect(urls['home'])
            else:
                error = "Username and Password do not match. Please try again"
                return render_to_response('login.html', {'form': form, 'error': error, 'urls': urls}, context_instance=RequestContext(request))
        else:
            return render_to_response('login.html', {'form': form, 'urls': urls}, context_instance=RequestContext(request))        
    else:
        ''' user is not submitting the form, therefore show the login form '''
        form = LoginForm()        
        context = {'form': form, 'urls':urls}
        return render_to_response('login.html', context, context_instance=RequestContext(request))
    
    
def LogoutRequest(request):
    logout(request)
    
    # get my urls
    urls = {}
    urls = getsiteurls(urls)
    
    return HttpResponseRedirect(urls['home'])

    

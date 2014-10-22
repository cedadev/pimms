from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response 
from django.http import Http404
from django.template.context import RequestContext

from pimms_apps.helpers import getsiteurls
from pimms_apps.exp.helpers import getexpurls
from pimms_apps.cv.helpers import getcvurls
from pimms_apps.qn.qnsetup.helpers import getqnsetupurls
from pimms_apps.person.models import Person


def home(request):
    '''Controller for app home page
    '''
    # get my urls
    urls = {}
    urls = getsiteurls(urls)
    urls = getexpurls(urls)
    urls = getcvurls(urls)
    urls = getqnsetupurls(urls)

    user = request.user
    person = None
    page = 'main/userhome.html'

    if user.is_authenticated():
       person = Person.objects.get(user=user)
       if user.has_perm('qn.create_questionnaire'):
          page = 'main/adminhome.html'
    
    return render_to_response(page, {'urls': urls, 'person': person},
                              context_instance=RequestContext(request))


def about(request):
    '''Controller for app about page
    '''
    # get my urls
    urls = {}
    urls = getsiteurls(urls)
      
    return render_to_response('main/about.html', {'urls': urls},
                              context_instance=RequestContext(request))


from django.shortcuts import render_to_response 
from django.http import Http404
from django.template.context import RequestContext

from pimms_apps.helpers import getsiteurls
from pimms_apps.exp.helpers import getexpurls
from pimms_apps.cv.helpers import getcvurls
from pimms_apps.qn.qnsetup.helpers import getqnsetupurls


def home(request):
    '''Controller for app home page
    '''
    # get my urls
    urls = {}
    urls = getsiteurls(urls)
    urls = getexpurls(urls)
    urls = getcvurls(urls)
    urls = getqnsetupurls(urls)
    
    return render_to_response('main/home.html', {'urls': urls},
                              context_instance=RequestContext(request))


def about(request):
    '''Controller for app about page
    '''
    # get my urls
    urls = {}
    urls = getsiteurls(urls)
      
    return render_to_response('main/about.html', {'urls': urls},
                              context_instance=RequestContext(request))


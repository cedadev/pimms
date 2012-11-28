'''

Generic helpers for PIMMS infrastructure

'''

from django.core.urlresolvers import reverse


# set up generic urls
def genurls():
    '''Create a dictionary of general URL reversals
    
    '''
    
    urls = {}
    # generic home page, about page etc (main app)
    urls['home'] = reverse('home', args=())
    urls['about'] = reverse('about', args=())
    
    # accounts management (person app)
    urls['login'] = reverse('login', args=())
    urls['logout'] = reverse('logout', args=())
    urls['register'] = reverse('register', args=())
    
    # cv urls (cv app)
    urls['cvhome'] = reverse('cvhome', args=())
    
    # exp urls (exp app) 
    urls['exphome'] = reverse('exphome', args=())
    
    return urls

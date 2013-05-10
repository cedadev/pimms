'''
Generic helpers for PIMMS infrastructure
'''

from django.core.urlresolvers import reverse


# set up generic urls
def getsiteurls(urls):
    '''Add site wide urls to url dictionary
    
    - urls : dictionary (potentially empty) passed in to append to 
    
    '''
    
    # generic home page, about page etc (main app)
    urls['home']  = reverse('home', args=())
    urls['about'] = reverse('about', args=())
    
    # accounts management (person app)
    urls['login']    = reverse('login', args=())
    urls['logout']   = reverse('logout', args=())
    urls['register'] = reverse('register', args=())
    
    return urls

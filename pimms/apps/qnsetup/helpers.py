'''
Helpers for CV application
'''

from django.core.urlresolvers import reverse


# set up generic urls
def getqnsetupurls(urls={}):
    '''Append qnsetup related urls to master dictionary
    
    Expects an already existing  
    
    '''
  
    urls['qnsetuphome'] = reverse('qnsetuphome', args=())
    
    return urls

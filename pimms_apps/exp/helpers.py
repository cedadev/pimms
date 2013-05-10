'''
helpers for exp application
'''

from django.core.urlresolvers import reverse


# set up generic urls
def getexpurls(urls):
    '''Append exp related urls to master dictionary
    
    '''
  
    urls['exphome'] = reverse('exphome', args=())
    urls['expadd'] = reverse('expadd', args=())
    urls['reqlist'] = reverse('reqlist', args=())
    urls['reqadd'] = reverse('reqadd', args=())
    
    return urls

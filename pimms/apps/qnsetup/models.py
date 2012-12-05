from django.db import models
from django.contrib.auth.models import User


class Questionnaire(models.Model):
    ''' Outer layer class representing a questionnaire instance and it's setup 
        parameters
    '''
    
    project         = models.CharField(max_length=32)
    description     = models.TextField(max_length=1024,blank=True, null=True)
    creator         = models.ForeignKey(User)
    # These are added automatically
    creationDate    = models.DateField(auto_now_add=True, editable=False)
    
    def __unicode__(self):
        return self.project
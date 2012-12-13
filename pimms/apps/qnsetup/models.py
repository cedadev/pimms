from django.db import models
from django.contrib.auth.models import User


class Questionnaire(models.Model):
    ''' Outer layer class representing a questionnaire instance and it's setup 
        parameters
    '''
    
    # Top layer attributes
    abbrev          = models.CharField(max_length=32)
    project         = models.CharField(max_length=32)
    description     = models.TextField(max_length=1024, blank=True, null=True)
    creator         = models.ForeignKey(User, blank=True, null=True)
    cvs             = models.ManyToManyField('CVFile', blank=True, null=True)
    exps            = models.ManyToManyField('ExpFile', blank=True, null=True)
    creationDate    = models.DateField(auto_now_add=True, editable=False)
    
    # Qn frontend specialiations
    idontknows      = models.BooleanField(default = False)
         
      
    def __unicode__(self):
        return self.abbrev    
      
      
class CVFile(models.Model):
    abbrev          = models.CharField(max_length=64, blank=True, null=True)
    filename        = models.CharField(max_length=128)
    
    def __unicode__(self):
        return self.abbrev
      

class ExpFile(models.Model):
    abbrev          = models.CharField(max_length=64, blank=True, null=True)
    filename        = models.CharField(max_length=128)
    
    def __unicode__(self):
        return self.abbrev  
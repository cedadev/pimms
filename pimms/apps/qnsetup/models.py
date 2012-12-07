from django.db import models
from django.contrib.auth.models import User


class SetupFile(models.Model):
    setupfile = models.FileField(upload_to='setupfiles')

    def __unicode__(self):
        return self.setupfile.name


class Questionnaire(models.Model):
    ''' Outer layer class representing a questionnaire instance and it's setup 
        parameters
    '''
    
    # Top layer attributes
    abbrev          = models.CharField(max_length=32)
    project         = models.CharField(max_length=32)
    description     = models.TextField(max_length=1024, blank=True, null=True)
    creator         = models.ForeignKey(User)
    cvs             = models.ManyToManyField('CVfile', blank=True, null=True)
    creationDate    = models.DateField(auto_now_add=True, editable=False)
    
    # Qn frontend specialiations
    idontknows      = models.BooleanField(default = False)
         
      
    def __unicode__(self):
        return self.abbrev
      

class CVfile(models.Model):
    '''Class to represent a CV file '''
    
    name          = models.CharField(max_length=64)
        
    def __unicode__(self):
        return self.name
    
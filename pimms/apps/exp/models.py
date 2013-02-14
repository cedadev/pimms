from django.db import models
from django.contrib.auth.models import User

from lxml import etree as ET
  
 
class Experiment(models.Model):
    ''' 
    Class to represent numericalExperiment  
    '''
    
    abbrev          = models.CharField(max_length=40)
    title           = models.CharField(max_length=128, blank=True, null=True)
    project         = models.CharField(max_length=64, blank=True, null=True)
    author          = models.ForeignKey(User)
    control         = models.BooleanField(default=False)
    description     = models.TextField(blank=True, null=True)
    rationale       = models.TextField(blank=True, null=True)
    requirements    = models.ManyToManyField('NumericalRequirement', blank=True, null=True)
    # These are added automatically
    created         = models.DateField(auto_now_add=True, editable=False)
    updated         = models.DateField(auto_now=True, editable=False)
    
    class Meta:
      permissions = (
            ('manage_exp', 'Can manage experiment'),
        )
    
    def __unicode__(self):
        return self.abbrev
    
    def gencimxml(self):
        #Generate an xml instance string of myself
        return ET.tostring(self.xmlobject(), pretty_print=True)
        

class NumericalRequirement(models.Model):
    '''Class to represent a numerical requirement '''
    
    docid         = models.CharField(max_length=64)
    description   = models.TextField(blank=True, null=True)
    name          = models.CharField(max_length=128)
    reqtype       = models.CharField(max_length=32)
    options       = models.ManyToManyField('RequirementOption', blank=True, null=True)
    author        = models.ForeignKey(User)
    # These are added automatically
    created       = models.DateField(auto_now_add=True, editable=False)
    updated       = models.DateField(auto_now=True, editable=False)
        
    def __unicode__(self):
        return self.name
    
    class Meta:
      permissions = (
            ('manage_req', 'Can manage requirement'),
        )
    

class RequirementOption(models.Model):
    ''' Class to represent a numerical requirement option '''
    
    option           = models.CharField(max_length=64)
    optionID         = models.TextField(blank=True, null=True)
    
    def __unicode__(self):
        return self.option

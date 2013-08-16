from django.db import models
from django.contrib.auth.models import User


class Person(models.Model):
    ''' Class to represent a user profile '''
    
    user      = models.OneToOneField(User)
    firstname = models.CharField(max_length=100)
    surname   = models.CharField(max_length=100)
    institute = models.CharField(max_length=512)
    
    def __unicode__(self):
        return '%s %s' % (self.firstname, self.surname)
    

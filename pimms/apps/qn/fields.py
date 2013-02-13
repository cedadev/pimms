# -*- coding: utf-8 -*-

# Holds all the field forms needed for my special types ... extended from django types.

import re

from django import forms
from django.forms.fields import URLField
from django.db import models
from django.forms.util import ValidationError
from django.conf import settings

from pimms.apps.qn.XMLutilities import *
from pimms.apps.qn.dropdown import DurationWidget, SDTwidget, TimeLengthWidget

logging=settings.LOG
#
# Start with the three new types we're adding to django
#  SimDateTime, TimeLength and Date Range
#
# Then for each of those have a ThingField, and then a ThingFieldForm.
#
class Calendar(object):
    #FIXME, look at cdtime for this ...
    def __init__(self,name='realCalendar'):
        if name in ['perpetualPeriod','daily-360']:
            self.mlength=[0,30,30,30,30,30,30,30,30,30,30,30,30]
        else: self.mlength=[0,31,29,31,30,31,30,31,31,30,31,30,31]
    def validate(self,sdt):
        if sdt.hh<0 or sdt.hh>23:
            raise ValueError('Invalid Hour')
        if sdt.mm<0 or sdt.mm>59:
            raise ValueError('Invalid minute')
        if sdt.ss<0 or sdt.ss>59:
            raise ValueError('Invalid seconds')
        if sdt.mon<1 or sdt.mon>12:
            raise ValueError('Invalid Month')
        if sdt.day<1 or sdt.day > self.mlength[sdt.mon]:
            raise ValueError('Invalid Day')

class SimDateTime(object):
    def __init__(self,s,calendar=Calendar('realCalendar')):
        ''' Expect ISO8601 [yyyy-mm-dd hh:mm:ss] plus optional calendar '''
        #FIXME: Should validate against calendar types
        if s is None or s=='None': 
            return None
        self.s=s.strip()
        s=self.s
        # allow a date time without a time, and set that to 00:00:00
        self.calendar=calendar
        try:
            d=s.split('-')
            neg=1
            if len(d)==4: 
                neg=-1
                d=d[1:]
            if 'T' not in d[2]: d[2]+='T00:00:00'
            b=d[2].split(':')
            d[2],b[0]=b[0].split('T')

            # re-format our input string to make sure it has
            # the correct number of leading 0's 
            d[0]=d[0].zfill(4)
            d[1]=d[1].zfill(2)    
            d[2]=d[2].zfill(2)
            self.s='-'.join(d)+'T'+':'.join(b)

            self.year,self.mon,self.day=map(int,d)
            self.year=self.year*neg
            b[2]=b[2].strip('Z')
            self.hh,self.mm,self.ss=map(int,b)
            self.time=':'.join(b)+'Z'
            self.calendar.validate(self)
        except Exception,e:
            raise ValueError('"%s" is not a valid SimDateTime ("%s")'%(s,e))
    def xml(self,parent='SimDateTime'):
        e=ET.Element(parent)
        e.text=self.s
        return e
    def __unicode__(self):
        return self.s
    def __str__(self):
        try:
            return self.s
        except:
            return u''
    def __len__(self):
        return len(str(self))
        
class TimeLength(object):
    def __init__(self,s):
        '''Time lengths consist of a integer number and a unit '''
        try:
            # standard string format
            l,u=s.split(' ')
            l=int(float(l))
        except:
            try :
                # CIM1.5 format
                mappingUnits={'D':'Days','Y':'Years'}
                assert s[0]=='P'
                l=s[1:len(s)-1]
                u=s[len(s)-1]
                assert u in mappingUnits
                u=mappingUnits[u]
                #logging.debug('duration '+s+' : '+l+','+u)
            except :
                raise ValueError('"%s" is not a valid TimeLength'%s)
        self.s='%s %s'%(l,u)
        self.period=l
        self.units=u
    def __unicode__(self):
        return self.s
    def __str__(self):
        return self.s
    def xml(self,parent='duration'):
        mappingUnits={'Years':'Y','Days':'D','years':'Y','days':'D'}
        length='P'+str(int(self.period))+mappingUnits[self.units]
        e=ET.Element(parent)
        e.text=length
        return e
        
class DateRange(object):
    def __init__(self,startDate,endDate=None,length=None,description=None):
        #startDate can be None if we have an open date range
        #if startDate is None:
        #    raise ValidationError('A start date is required')
        self.startDate=startDate
        self.endDate=endDate
        self.length=length
        self.description=description
    def __unicode__(self):
        return self.__str__()
    def __len__(self):
        return len(str(self))
    def __str__(self):
        s=str(self.startDate)
        if self.endDate: s+=' to %s'%self.endDate
        if self.length:s+=' plus %s'%self.length
        if self.description: s+=' (%s)'%self.description
        return s
    def xml(self,parent='DateRange'):
        top=ET.Element(parent)
        if self.startDate:
            e=ET.SubElement(top,"closedDateRange")
        else:
            e=ET.SubElement(top,"openDateRange")
        
        if self.length is not None: e.append(self.length.xml('duration'))
        if self.endDate is not None: e.append(self.endDate.xml('endDate'))
        if self.startDate is not None: e.append(self.startDate.xml('startDate'))
        if self.description is not None: ET.SubElement(e,'description').text=self.description
        return top
    def strxml(self,parent='DateRange'):
        e=self.xml(parent)
        return ET.tostring(e)
    def copy(self):
        new=DateRange(startDate=self.startDate,endDate=self.endDate,
            length=self.length,description=self.description)
        return new
    @staticmethod
    def fromxml(xml):
        ''' Where we expect an xml string, with no namespace '''
        e=ET.fromstring(xml)
        return DateRange.fromXML(e)
    @staticmethod
    def fromXML(e):
        getter=etTxt(e)
        s0=getter.find(e,'closedDateRange')
        if s0 is None: s0=getter.find(e,'ClosedDateRange')
        if s0 is None: s0=getter.find(e,'openDateRange')
        if s0 is None: s0=getter.find(e,'OpenDateRange')
        if s0 is None: s0=e
        s1=getter.getN(s0,'startDate')
        if s1 is not None: s1=SimDateTime(s1)
        #logging.debug('startDate '+str(s1))
        s2=getter.getN(s0,'endDate')
        if s2 is not None: s2=SimDateTime(s2)
        #logging.debug('endDate '+str(s2))
        # length is an out of date format used by the experiment configuration documents
        tl=getter.find(s0,'length')
        if tl is not None:
            tl=TimeLength('%s %s'%(tl.text,tl.attrib['units']))
        else:
            # duration is the CIM1.5 format
            tl=getter.find(s0,'duration')
            if tl is not None:
                tl=TimeLength(tl.text)
        #logging.debug('timelength '+str(tl))
        dr=DateRange(startDate=s1,endDate=s2,length=tl)
        dr.description=getter.getN(e,'description')
        return dr
    @staticmethod
    def hack(s):
        ''' Interim method for taking a string and creating a date range '''
        #FIXME: expect we will replace this with a multivalue field
        # Assume we have two ISO8601 dates ...
        ss=s.split(' ')
        dr=DateRange(startDate=SimDateTime(ss[0]))
        if len(ss)==2: dr.endDate=SimDateTime(ss[1])
        return dr
#
# For each of these new ttypes, we need a way of handing them to and from django storage as attributes,
# so we need foreach Thing, we need a ThingField ...
#


class SimDateTimeField(models.CharField):
    ''' We are creating a specific type of field that we want to see on forms. It's a bit like
    a date, but not exactly, since it includes (optionally) a calendar designate. If not 
    calendar is included, it's a real calendar. However, for now, it is just a char field '''
    
    description = ' A simulation date time (with optional calendar)'
    __metaclass__ = models.SubfieldBase

    def __init__(self,*args,**kwargs):
        ''' Force the maximum length since we know what it is '''
        kwargs['max_length']=32
        models.CharField.__init__(self,*args,**kwargs)
    
    def formfield(self, **kwargs):
        return SimDateTimeFieldForm2 (*kwargs)
        
    def clean(self, s, y=None):
        if isinstance(s,list):
            # this is a hack, it ought not be, but these nested multi widgets 
            # cause naughtiness that I haven't time to fix #FIXME
            if s==['','','','']: 
                return None
            d='-'.join(s[0:3])
            if s[3]<>'':
                d+='T%s'%s[3]
            s=d
        elif s<> '':
            pass
        else: 
            return None
        
        if isinstance(s,SimDateTime): 
            return s
        
        try:
            sdt=SimDateTime(s)
            return sdt
        except:
            raise ValidationError('Please enter a valid simulation date  (not "%s")'%s)
            
    def to_python(self, value):
        ''' Handle two cases: an instance of a date, or a string (which is what we get)'''
        if value=='':
            if self.blank:
                return value
            else:
                raise ValidationError(
                    ugettext_lazy("This field cannot be blank."))
        elif isinstance(value, basestring):
            return SimDateTime(value)
        elif isinstance(value,SimDateTime):
            return value
        elif value is None:
            if self.null:
                return value
            else:
                raise ValidationError(
                    ugettext_lazy("This field cannot be null."))
        else:
            raise ValueError('Unable to coerce value [%s] into SimDateTime'%value)

    def get_db_prep_value(self, value):
        ''' From python to db character field '''
        return str(value)
    
    
class TimeLengthField(models.CharField):
    ''' It turns out that it's unbelievably clunky to pass in a vocabulary for
    timelengths in and out of Django Widgets and Forms. So, sadly, in the spirit
    of getting something done, we're hardcoding the timelength units here.'''
    description = ' A time length '
    __metaclass__ = models.SubfieldBase
    def __init__(self,units,**kwargs):
        ''' Force the maximum length since we know what it is '''
        kwargs['max_length']=32
        models.CharField.__init__(self,**kwargs)
        self.units={}
        for u in units: self.units[u[0]]=u[1]
    def to_python(self,value):
        if isinstance(value,basestring):
            return TimeLength(value)
        elif isinstance(value,TimeLength):
            return value
        else:
            return None
    def formfield(self, **kwargs):
        defaults = {'max_length': self.max_length}
        defaults.update(kwargs)
        return super(models.CharField, self).formfield(**defaults)
    def get_db_prep_value(self, value):
        ''' From python to db character field '''
        return str(value)
    def clean(self,value):
        ''' Take a form instance and see if can be turned into a time length field '''
        # The form returns the number and an id from a term list. 
        # we've loaded that into the terms attribute of the widget so we have it now
        if value[0]=='': 
            return None
        #checking that string value is not akin to a float
        elif '.' in value[0]:
            raise ValidationError('Please enter an integer value here for duration')
        
        try:
            tlv=TimeLength('%s %s'%(value[0],self.units[value[1]]))
            return tlv
        except Exception,e:
            raise ValidationError('Please enter a valid time length field  (not "%s")'%value)
        
        
class DateRangeField(models.CharField):
    ''' We are creating a specific type of field that we want to see on forms.
    It's a bit like a date, but not exactly, since it includes (optionally) a
    calendar designate. If no calendar is included, it's a real calendar.'''
    description = ' A date range '
    __metaclass__ = models.SubfieldBase
    def __init__(self,*args,**kwargs):
        ''' Force the charfield maximum length since we've decided about this stuff '''
        kwargs['max_length']=600
        models.CharField.__init__(self,*args,**kwargs)
    def to_python(self,value):
        ''' This is called by a form which will have a string.'''
        if isinstance(value,basestring):
            # for the moment, just hand it off to the hack
            if value[0:1]=='<': 
                return DateRange.fromxml(value)
            else: return DateRange.hack(value)
        elif isinstance(value,DateRange):
            return value
        else:
            return None
    def formfield(self, **kwargs):
        return DateRangeFieldForm2 (*kwargs)
    def value_to_string(self,value):
        ''' Take our storage value, and return a string '''
        logging.debug('from storage %s'%value.__class__)
        if value is None:
            return None
        else:
            return DateRange.fromxml(value)
    def get_db_prep_value(self, value):
        ''' From python to db character field for storage '''
        if value is None:
            return None
        else:
            return value.strxml()

#
# And for each ThingField, we need a ThingFieldForm
# The TimeLengthFieldForm is in the cmip5 models.py because it needs knowledge of the term models
#


class SimDateTimeFieldForm(forms.CharField):
    ''' Used to ensure that the clean method validates date range entries '''
    def __init__(self,*args,**kwargs):
        forms.CharField.__init__(self,*args,**kwargs)

class SimDateTimeFieldForm2(forms.MultiValueField):
    def __init__(self,*args,**kwargs):
        fields=(forms.CharField(),forms.CharField(),forms.CharField(),forms.CharField() )
        mywidget = SDTwidget()
        forms.MultiValueField.__init__(self,fields,widget=mywidget,required=False)
    def compress(self,data_list):
        #logging.debug('compressing in SimDateTimeFieldForm2 %s'%data_list)
        if data_list == []:
            return None
        else:
            d='-'.join(data_list[0:3])
            if data_list[3]<>None:
                d+='T%s'%data_list[3]
        try:
            return SimDateTime(d)
        except ValueError:
            raise ValidationError('Please enter a valid date time')

class DateRangeFieldForm(forms.CharField):
    ''' Used to ensure that the clean method validates date range entries '''
    def __init__(self,*args,**kwargs):
        #logging.debug('instantiating date range field form')
        kwargs['max_length']=132
        forms.CharField.__init__(self,*args,**kwargs)
       
    def clean(self,value):
        try:
            d=DateRange.hack(value)
            return d
        except:
            raise ValidationError('Please enter a valid date range')

class TimeLengthFieldForm(forms.MultiValueField):
    ''' Provides a multiwidget for a time period, based on 
        http://www.hoboes.com/Mimsy/hacks/django-forms-edit-inline/multiwidgets-templates/ '''
    def __init__(self):
        fields=(forms.IntegerField(),forms.ModelChoiceField(queryset=terms) )
        mywidget = TimeLengthWidget()
        forms.MultiValueField.__init__(self,fields,widget=mywidget,required=False)
    def compress(self,data_list):
        ''' Takes the thing returned by the form and converts them to a time length '''
        if data_list == []:
            return None
        else:
            d=TimeLength('%s %s'%tuple(data_list))
        return d
        
        
class DateRangeFieldForm2(forms.MultiValueField):
    ''' 
    Provides a multiwidget for a date range, based on 
    http://www.hoboes.com/Mimsy/hacks/django-forms-edit-inline/multiwidgets-templates/ 
    '''
    
    def __init__(self,*args,**kwargs):
        units          = kwargs.pop('units',[('0','Years'),('1','Days')])
        fields         = (SimDateTimeField(),SimDateTimeField(), TimeLengthField(units) )
        mywidget       = DurationWidget(units=units)
        mywidget.units = units
        
        forms.MultiValueField.__init__(self,fields,widget=mywidget,required=False)
    
    ## Note that the base class cleans all the objects against the clean methods
    ## exposed by each of the fields listed.
    
    def compress(self,data_list):
        ''' At which point we have the three *field* objects to compress, and this
        is where we have to do any cross object validation '''
        if data_list[1] is None and data_list[2] is None:
            raise ValidationError('Require either an end date or a length ')
        if data_list[1] is not None and data_list[2] is not None:
            raise ValidationError('Cannot have both an enddate and a length')
        if data_list == []:
            return None
        else:
            d=DateRange(startDate=data_list[0],endDate=data_list[1],length=data_list[2])
        return d
        
try:
    from django.conf import settings
    URL_VALIDATOR_USER_AGENT = settings.URL_VALIDATOR_USER_AGENT
except ImportError:
    # It's OK if Django settings aren't configured.
    URL_VALIDATOR_USER_AGENT = 'Django (http://www.djangoproject.com/)'


#pulling in an extended regex list to allow for ftp urls (which are not 
# available at current django version)     
url_re = re.compile(
r'^(?:http|ftp)s?://' # http:// or https://
#r'^https?://' # http:// or https://
#r'^ftps?://' # http:// or https://
r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|' #domain...
r'localhost|' #localhost...
r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
r'(?::\d+)?' # optional port
r'(?:/?|/\S+)$', re.IGNORECASE)


class extURLField(URLField):
    '''
    extends URLField to allow ftp prefixes
    '''
    default_error_messages = {
        'invalid': 'Enter a valid URL.',
        'invalid_link': 'This URL appears to be a broken link.',
    }

    def __init__(self, max_length=None, min_length=None, verify_exists=False,
            validator_user_agent=URL_VALIDATOR_USER_AGENT, *args, **kwargs):
        super(URLField, self).__init__(url_re, max_length, min_length, *args, **kwargs)
        self.verify_exists = verify_exists
        self.user_agent = validator_user_agent
  
    

## South needs information on custom fields:
#from south.modelsinspector import add_introspection_rules

#add_introspection_rules([], ["pimms.apps.qn.fields.SimDateTimeField"])
#add_introspection_rules([], ["pimms.apps.qn.fields.DateRangeField"])




       
       

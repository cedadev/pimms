# -*- coding: utf-8 -*-
## http://dropdown-check-list.googlecode.com/svn/trunk/src/demo.html
from django import forms
from django.utils.safestring import mark_safe
from django.conf import settings
from django.template.loader import render_to_string

logging=settings.LOG

SCRIPT='''<script type="text/javascript">$(document).ready($("#id_%s").dropdownchecklist( {icon: {placement:"right",toOpen:"ui-icon-triangle-1-s"} , %s } ));</script>'''


def displayAttributes(**kwargs):
    if 'attrs' in kwargs:
        a=kwargs['attrs']
    else: a={}
    if 'maxDropHeight' not in a: a['maxDropHeight']=200
    if 'size' in a:
        # hack to get from "django" size to something appropriate for a screen
        a['width']=int(a['size'])*6  
        del(a['size'])
    logging.debug(str(a))
    return ','.join(['%s:%s'%(k,a[k]) for k in a]) 

class DropDownWidget(forms.SelectMultiple):
    ''' Implements a javascript assisted dropdown '''
    def __init__(self,*args,**kwargs):
        forms.SelectMultiple.__init__(self,*args,**kwargs)
        self.stratt=displayAttributes(**kwargs)
    def render(self,name, value, attrs):
        s=forms.SelectMultiple.render(self,name,value,attrs)
        s+=mark_safe(SCRIPT%(name,self.stratt))
        return s
    
class DropDownSingleWidget(forms.Select):
    ''' Implements a javascript assisted dropdown '''
    def __init__(self,*args,**kwargs):
        forms.Select.__init__(self,*args,**kwargs)
        self.stratt=displayAttributes(**kwargs)
    def render(self,name, value, attrs):
        s=forms.Select.render(self,name,value,attrs)
        #s+=mark_safe(SCRIPT%(name,self.stratt))  # not sure I think I really like these ...
        return s
        
class SimDateTimeWidget(forms.TextInput):
    '''Implmements a formatted text widget to return a sim date time object '''
    def __init__(self,*args,**kwargs):
        forms.TextInput.__init__(self,*args,**kwargs)
    def render(self,name,value,attrs):
        ''' Now this is fun. Not quite sure what the class is of this thing ...'''
        #logging.debug('widget 1 log %s %s %s %s'%(name,value,value.__class__,attrs))
        return forms.TextInput.render(self,name,value,attrs)
    
class DateRangeWidget(forms.TextInput):
    '''Implmements a formatted text widget to return a date range object '''
    def __init__(self,*args,**kwargs):
        forms.TextInput.__init__(self,*args,**kwargs)
    def render(self,name,value,attrs):
        ''' Now this is fun. Not quite sure what the class is of this thing ...'''
        logging.debug('widget 2 log %s'%value)
        return forms.TextInput.render(self,name,value,attrs)
        
class TimeLengthWidget(forms.MultiWidget):
    def __init__(self,units):
        widgets=(forms.TextInput(attrs={'size':'6'}),forms.Select(choices=units))
        forms.MultiWidget.__init__(self,widgets)
    def decompress(self,value):
        if value is not None:
            return [value.period,value.units]
        else: return [None,None]
    def format_output(self,rendered_widgets):
        return '%s %s'%tuple(rendered_widgets)
        
class DurationWidget(forms.MultiWidget):
    # following http://www.hoboes.com/Mimsy/hacks/django-forms-edit-inline/multiwidgets-templates/
    def __init__(self,units=None):
        widgets = (SDTwidget(), SDTwidget(), TimeLengthWidget(units) )
        forms.MultiWidget.__init__(self,widgets)
    def decompress(self, value):
        if value is not None:
            return [value.startDate, value.endDate, value.length]
        else: return [None,None,None]
    def format_output(self, rendered_widgets):
        widgetContext = {'from':rendered_widgets[0],'to':rendered_widgets[1],'for':rendered_widgets[2]}
        return render_to_string("DateRange.html", widgetContext)

class SDTwidget(forms.MultiWidget):
    def __init__(self):
        widgets = (forms.TextInput(attrs={'size':'4'}), forms.TextInput(attrs={'size':'2'}),
                   forms.TextInput(attrs={'size':'2'}), forms.TextInput(attrs={'size':'8'}) )
        forms.MultiWidget.__init__(self,widgets)
    def decompress(self, value):
        try:
            return [value.year,value.mon,value.day,value.time]
        except:
            return [None,None]
    def format_output(self, rendered_widgets):
        return '%s-%s-%s T%s'%tuple(rendered_widgets)

        

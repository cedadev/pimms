# -*- coding: utf-8 -*-
from django.forms.util import ErrorList
from django.forms.fields import URLField

def uniqueness(form,centre,field='name'):
    '''  This utility function is to be called within a model clean method to ensure uniqueness
    of a field within a model in a given centre (as opposed to within all instances of the model
    which can be dealt with by the django infrastructure.
             Expect a form instance,,
                    the centre,
                    and the field, as arguments '''
    #http://docs.djangoproject.com/en/dev/ref/forms/validation/#cleaning-and-validating-fields-that-depend-on-each-other
    cleaned_data=form.cleaned_data
    name=cleaned_data.get(field)
    if form.instance: 
        # it's already in there, so we don't need to check it unless the mnenonic has changed
        if name==form.instance.__getattribute__(field):return cleaned_data
    existing=form.Meta.model.objects.all()
    if centre is not None:
        existing=existing.filter(centre=centre)      
    #Assume we don't want something with no centre clashing with anything
    #since it might want to be copied in later.
    kw={field:name}
    result=existing.filter(**kw)
    if len(result)>0:
        #It's already there ... reject
        msg=u'%s is aready in use, please choose a unique %s'%(name,field)
        form._errors[field] = ErrorList([msg])
        del cleaned_data[field]
    return cleaned_data

class refLinkField(URLField):
    ''' Used to override the check to check DOIs as valid URLs ...'''
    def clean(self, value):
        # first sort out whether it's a doi
        parsed=value.split(':')
        if parsed[0] in ['DOI','doi']:
            #value='http://dx.doi.org/'+parsed[1]
            # we can't use URLfield because doi.org doens't return a 404 .
            return value
        else:
            return URLField.clean(self,value)
            
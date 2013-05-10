from pimms.apps.qn.models import Component, Centre, Experiment
from django.contrib import admin

admin.site.register(Centre)
admin.site.register(Experiment)


class ComponentAdmin(admin.ModelAdmin):
    '''
    Customising admin table for Components
    '''
    list_display = ('abbrev', 'title', 'centre', 'isModel', 'isDeleted', 
                    'isComplete', 'created')
    list_filter = ['isModel', 'isDeleted', 'isComplete']
    search_fields = ['abbrev']
    date_hierarchy = 'created'

admin.site.register(Component, ComponentAdmin)



from pimms_apps.exp.models import Experiment, NumericalRequirement
from pimms_apps.qn.models import Questionnaire
from django.contrib import admin


admin.site.register(Experiment)
admin.site.register(NumericalRequirement)

admin.site.register(Questionnaire)


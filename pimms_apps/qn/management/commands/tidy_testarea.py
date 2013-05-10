'''
This standalone script shall clear out all information added in the test centre and replace everything in 
the example centre with the most recent information in the Met Office centre

Created on 19 Apr 2011

@author: Gerry Devine
'''

from django.core.management.base import BaseCommand, CommandError
from pimms_apps.qn.models import *

class Command(BaseCommand):
        
    help = 'Tidies up the test and example centres'

    def handle(self, *args, **options): 
        #state which centres to work with
        exc = Centre.objects.get(abbrev='1. Example')
        testc = Centre.objects.get(abbrev='2. Test Centre')
        mohc = Centre.objects.get(abbrev='MOHC')
        
        #grab all current info sitting in the example and test centre
        exmodels = Component.objects.filter(centre=exc)
        exgrids = Grid.objects.filter(centre=exc)
        exsims = Simulation.objects.filter(centre=exc)
        explats = Platform.objects.filter(centre=exc)
    
        testmodels = Component.objects.filter(centre=testc)
        testgrids = Grid.objects.filter(centre=testc)
        testsims = Simulation.objects.filter(centre=testc)
        testplats = Platform.objects.filter(centre=testc)
        
        for mod in exmodels:
            mod.isDeleted=True
            mod.save()
        for grid in exgrids:
            grid.isDeleted=True
            grid.save()
        for sim in exsims:
            sim.isDeleted=True
            sim.save()
        for plat in explats:
            plat.isDeleted=True
            plat.save()
        
        for mod in testmodels:
            mod.isDeleted=True
            mod.save()
        for grid in testgrids:
            grid.isDeleted=True
            grid.save()
        for sim in testsims:
            sim.isDeleted=True
            sim.save()
        for plat in testplats:
            plat.isDeleted=True
            plat.save()

        # Now make a copy of official example (Mark Elkington's at this point)
        
        original=Component.objects.filter(abbrev='HadGEM2-ES').get(centre=mohc)
        new=original.copy(exc)
        
#
## Parse the output of Controlled vocab	xml files (produced by XSL on MindMap XML)
## Author : Matt Pritchard
## 

from django.conf import settings

from xml.etree import ElementTree as ET

from pimms_apps.qn.models import *
from pimms_apps.qn.utilities import atomuri
from pimms_apps.qn.qnsetup.XMLinitialiseQ.VocabList import Realms

logging=settings.LOG


class XMLVocabReader:

	''' Reads XML vocab structure. '''
	def __init__(self,filename, centre, authorName, authorEmail):
		''' Initialise from mindmap file '''
		self.etree=ET.parse(filename)
		self.root=self.etree.getroot() # should be the "vocab" element
		self.centreID=centre
                self.authorName=authorName
                self.authorEmail=authorEmail
		try:
                    self.modelCentre=Centre.objects.get(pk=centre)
                except:
                    raise 'Cannot find centre %s'%centre
                
	def doParse(self):
                #!TODO: I have patched this block to return when there are no components.
		#       Check this is works with the rest of the code.
		model = self.root.find('component')
		if model is None:
			logging.info("No components found for centre %s" % self.centreID)
			return

		model = self.root.findall('component')[0]
		# top of tree / start of model
		logging.info("New component: %s for centre %s"%(model.attrib['name'],self.centreID))
		# remember element that is immediate child of vocab
		# Initiate new top-level component in django
		modelParser = ComponentParser(model, self.root, self.modelCentre, (self.authorName, self.authorEmail))
		modelParser.add(True)
                self.topLevelID=modelParser.topLevelID
		
class Parser:
	''' class for handling all elements '''

	def __init__(self, item, parent, centre, author):
		''' initialise  parser '''
		self.item = item
		self.parent = parent
		self.centre = centre
                self.author = author
		logging.debug("instantiated Parser for %s"% item.tag)
		if item.attrib['name']:
			logging.debug("name = %s"%item.attrib['name'])
		else:
			logging.debug("[no name]")

class ComponentParser(Parser):

	''' parser for component '''

        def __handleParam(self,elem):
            ''' Handle parameters and add their properties to parent component '''
            paramName=elem.attrib['name']
            choiceType=elem.attrib['choice']
            logging.debug('For %s found parameter %s with choice %s'%(self.item.attrib['name'],paramName,choiceType))
            if choiceType in ['OR','XOR']:
                #create and load vocabulary
                v=Vocab(uri=atomuri(),name=paramName+'Vocab')
                v.save()
                logging.debug('Created vocab %s'%v.name)
                for item in elem:
                    if item.tag=='value':
                        value=Value(vocab=v,value=item.attrib['name'])
                        value.save()
                        logging.debug('Added %s to vocab %s'%(value.value,v.name))
                    else:
                        logging.info('Found unexpected tag %s in %s'%(item.tag,paramName))
                p=Param(name=paramName,component=self.component,ptype=choiceType,vocab=v)
                p.save()
                logging.info('Added parameter %s to component %s (%s)'%(paramName,self.component.abbrev,self.component.id))
               
	def add(self, doSubs, model=None, realm=None):
                u=atomuri()
		component = Component(
                        title='',
			scienceType=self.item.attrib['name'],
			abbrev=self.item.attrib['name'],
                        uri=u,centre=self.centre,contact=self.author[0],email=self.author[1])
		component.save() # we need a primary key value so we can add subcomponents later
                self.component=component # used to assign parameters ...
                
		if self.parent.tag != "component":
			logging.debug("Top-level component %s"%self.item.attrib['name'])
                        self.topLevelID=component.id
                        model=component
                elif component.scienceType in Realms:
                    realm=component
                    component.model=model
                else:
                    component.model=model
                    # if realm doesn't exist, then somehow we've broken our controlled vocab
                    # realm relationship.
                    component.realm=realm
                  
		if doSubs:
			''' go ahead and process subelements, too '''
			# 1. Component children of this parent
			for subchild in self.item:
				if subchild.tag == "component":
					logging.debug("Found child : %s"%subchild.tag)
					subComponentParser = ComponentParser(subchild, self.item, self.centre, self.author)
					# Handle child components of this one (True = recursive)
					child=subComponentParser.add(True,model=model,realm=realm)
                                        logging.debug("Adding sub-component %s to component %s"%(child.abbrev, component.abbrev))
		                        component.components.add(child)
                                #2. Parameter children of this parent
                                ## FIXME, pretty sure we need to do something more sophisticated here:
                                if subchild.tag == 'parameter': self.__handleParam(subchild)
                                    
                # 3. ComponentRef children of this parent 
		# 4. ParameterRef children of this parent		
		component.save()
                return component
                                
if __name__=="__main__":
	import sys
	filename=sys.argv[1]
	centre=sys.argv[2]
	XMLVocabReader(filename, centre,'Joe Bloggs','a@foo.bar').doParse()
	

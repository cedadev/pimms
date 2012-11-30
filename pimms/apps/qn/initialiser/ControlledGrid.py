
# This file really needs to be joined up with ControlledModel to avoid repeated code. 

from pimms.apps.qn.models import *
from pimms.apps.qn.utilities import atomuri
from pimms.apps.initialiser.XMLinitialiseQ import VocabList

# move from ElementTree to lxml.etree
#from xml.etree import ElementTree as ET
from lxml import etree as ET
import unittest
import os
import datetime

from django.conf import settings
logging=settings.LOG


def initialiseGrid():
    ''' Setup a template for grid copying in the dummy CMIP5 centre '''
    try:
        c=Centre.objects.get(abbrev='CMIP5')
    except:
        cl=Centre.objects.all().order_by('id')
        logging.debug('Unable to read dummy CMIP5 centre description, existing centres are %s'%cl)
        return False
    m=NumericalGrid(c,xml=True)
    return True

class NumericalGrid:
    
    ''' Handles the creation of a grid instance in the database, either from XML storage
    or from a pre-existing instance '''
    
    def __init__(self,centre,id=0,xml=False):
        ''' Initialise by copy from django storage, or build a new one from the XML '''
        
        klass=centre.__class__
        if klass != Centre:
            raise ValueError('Need a valid django centre class for NumericalGrid, got %s'%klass)
        self.centre=centre
        self.joe=ResponsibleParty.objects.filter(centre=centre)[0]
        
        if id==0: xml=True
        if xml and id<>0:
            raise ValueError('Incompatible arguments to numerical model')
        if id<>0:
            self.top=Grid.objects.get(id=id)
        elif xml:
            self.makeEmptyGrid(centre)
            self.read()
        else:
            raise ValueError('Nothing to do in NumericalGrid')
        
    def copy(self):
        
        new=self.top.makeNewCopy(self.centre)
        logging.debug('Made new grid %s with id %s in %s'%(new,new.id,self.centre))
        return new
    
    def makeEmptyGrid(self,
                      centre,
                      author=None,
                      contact=None,
                      funder=None,
                      title='Grid Template',
                      abbrev='Grid Template'):
        
        if author is None: author=self.joe
        if funder is None: funder=self.joe
        if contact is None: contact=self.joe
        
        grid=Grid(centre=centre,abbrev='',uri=atomuri(),
                            author=author,contact=contact,funder=funder)
        grid.istopGrid=True
        grid.title=title
        grid.abbrev=abbrev
        grid.save()
        grid.topgrid=grid
        grid.save()
        self.top=grid
        logging.debug('Created empty top level grid %s'%grid)
        # now get a placeholder paramgroup and constraint group
        p=ParamGroup()
        p.save() 
        grid.paramGroup.add(p)
        cg=ConstraintGroup(constraint='',parentGroup=p)
        cg.save()
        
    def read(self):
       
        ''' Read mindmap XML document(s) to build a complete grid description '''
            
        mindMapDir = os.path.join(settings.PROJECT_ROOT, "static/data/mindmaps/grid")
                                
        logging.debug('Looking for grid mindmaps in %s'%mindMapDir)
        mindmaps=[os.path.join(mindMapDir, f) for f in os.listdir(mindMapDir)
                    if f.endswith('.xml')]
        
        #TODO: should only ever have to deal with one grid mindmap? 
        
        mindmaps.sort()  # at least go in alphabetical order.
                    
        for m in mindmaps:
            x=XMLVocabReader(m, self.top)
            x.doParse()
            #self.top.grids.add(x.component)
            self.top=x.component
            logging.debug('Mindmap %s added with grid id %s'%(m,x.component.id))
        
        self.top.save()
        logging.info('Created new grid %s'%self.top.id)
    

class XMLVocabReader:
    # original author, Matt Pritchard
    ''' Reads XML vocab structure. '''
    def __init__(self,filename, grid):
        ''' Initialise from mindmap file '''
        self.etree=ET.parse(filename)
        self.root=self.etree.getroot() # should be the "vocab" element
        self.grid=grid
     
    def doParse(self):
        first = self.root.findall('component')[0]
        logging.info("New component: %s for grid %s"%(first.attrib['name'],self.grid))
        # Initiate new top-level component in django:
        modelParser = GridParser(first, self.grid)
        self.component=modelParser.add(True,True)
        self.component.metadataVersion='Mindmap Version %s,  Translation Version %s  (using %s). CMIP5 Questionnaire Version alpha10.'%(
        self.root.attrib['mmrevision'],self.root.attrib['transrevision'],
        self.root.attrib['mmlcrevision'])

class GridParser:
    ''' class for handling all elements '''
    def __init__(self, item, grid, isParamGroup=False):
        ''' initialise  parser '''
        self.item = item
        self.grid = grid
        self.isParamGroup = isParamGroup
        #logging.debug("Instantiated Parser for %s"% item.tag)
        if item.attrib['name']:
            logging.debug("name = %s"%item.attrib['name'])
        else:
            logging.debug("[no name]")
            
    def __handleParamGrp(self,elem):
        ''' Handle the parameter groups consisting of parameters and constraints '''
        p=ParamGroup(name=elem.attrib['name'])
        p.save()
        self.grid.paramGroup.add(p)
        cg=None
        empty=True
        for item in elem:
            empty=False
            if item.tag=='constraint':
                self.__handleConstraint(item,p)
            elif item.tag=='parameter':
                cg=self.__handleParam(item,p,cg)
        if empty:
            #create an empty constraint group so new parameters can be added.
            cg=ConstraintGroup(constraint='',parentGroup=p)
            cg.save()
            
    def __handleConstraint(self,elem,pg):
        ''' Handle Constraints'''
        c=ConstraintGroup(constraint=elem.attrib['name'],parentGroup=pg)
        c.save()
        for item in elem:
            self.__handleParam(item,pg,c)
    
    def __handleKeyboardValue(self,elem):
        ''' Parse for and handle values from the keyboard, e.g.
        <value format="string" name="list of 2D species emitted"/>
        <value format="numerical" name="lat_min" units="degN"/>'''
        # currently ignoring the value names ...
        velem=elem.find('value')
        if velem is None:
            logging.info('ERROR: Unable to parse %s(%s)'%(elem.tag,elem.text))
            return False,None
        keys=velem.attrib.keys()
        numeric,units=False,None
        if 'format' in keys: 
            if velem.attrib['format']=='numerical': numeric=True
        if 'units' in keys: units=velem.attrib['units']
        return numeric,units
    
    def __handleParam(self,elem,pg,cg):
        ''' Add new parameter to cg, if cg none, create one in pg '''
        if cg is None:
            cg=ConstraintGroup(constraint='',parentGroup=pg)
            cg.save()
        paramName=elem.attrib['name']
        choiceType=elem.attrib['choice']
        logging.debug('For %s found parameter %s with choice %s'%(self.item.attrib['name'],paramName,choiceType))
        try:
            Param={'OR':OrParam,'XOR':XorParam,'keyboard':KeyBoardParam}[choiceType]
        except KeyError:
            logging.info('ERROR: Ignoring parameter %s'%paramName)
            return
        if choiceType in ['OR','XOR']:
            #create and load vocabulary
            v=Vocab(uri=atomuri(),name=paramName+'Vocab')
            v.save()
            logging.debug('Created vocab %s'%v.name)
            co,info=None,None
            for item in elem:
                if item.tag=='value':
                    value=Term(vocab=v,name=item.attrib['name'])
                    value.save()
                elif item.tag=='definition':
                    defn=item.text
                else:
                    logging.info('Found unexpected tag %s in %s'%(item.tag,paramName))
            logging.debug('L %s %s '%(paramName,defn))
            p=Param(name=paramName,constraint=cg,vocab=v,definition=defn,controlled=True)
            p.save()
        elif choiceType in ['keyboard']:
            defn,units='',''
            delem=elem.find('definition')
            if delem is not None: defn=delem.text
            numeric,units=self.__handleKeyboardValue(elem)
            p=Param(name=paramName,constraint=cg,definition=defn,units=units,numeric=numeric,controlled=True)
            p.save()
        elif choiceType in ['couple']:
            # we create an input requirement here and now ...
            ci=ComponentInput(owner=self.component,abbrev=paramName,
                              description='Required by controlled vocabulary for %s'%self.component,
                              realm=self.component.realm)
            ci.save()
            #and we have to create a coupling for it too
            cp=Coupling(component=self.component.model,targetInput=ci)
            cp.save()
        logging.info('Added component input %s for %s in %s'%(paramName,cg,pg))
        return cg
               
    def add(self, doSubs, isTop):
        u=atomuri()
        # add spaces before any capital letters to make the tree formatting look nicer
        name=self.item.attrib['name']
        nameWithSpaces=''
        idx=0
        for char in name :
            if idx>0 : # skip first string value as we do not want spaces at the beginning of a string
                if char.isupper() and name[idx-1].isalpha() :
                    nameWithSpaces+=' '
            nameWithSpaces+=char
            idx+=1
        # check length
        if len(nameWithSpaces)> 29: 
            logging.debug('TOOLONG: name %s will be abbreviated'%nameWithSpaces)
            nameWithSpaces=nameWithSpaces[0:29]
        if isTop <> True:
            grid = Grid(title='',
                    abbrev=nameWithSpaces,
                    isParamGroup=self.isParamGroup,
                    uri=u,
                    centre=self.grid.centre,
                    contact=self.grid.contact,
                    author=self.grid.author,
                    funder=self.grid.funder)
            grid.save() # we need a primary key value so we can add subcomponents later
            self.grid=grid # used to assign parameters ...
        
            logging.debug('Handling Grid %s'%(grid.abbrev))
        else:
            grid=self.grid

            
        if doSubs:
            #temporary
            for subchild in self.item:
                if subchild.tag == "component":
                    logging.debug("Found child : %s"%subchild.tag)
                    subGridParser = GridParser(subchild, self.grid)
                    # Handle child components of this one (True = recursive)
                    child=subGridParser.add(True, False)
                    logging.debug("Adding sub-grid %s to K %s"%(child.abbrev, grid.abbrev))
                    grid.grids.add(child)
                elif subchild.tag == 'parametergroup':
                    if subchild.attrib['componentView'] == 'False' or subchild.attrib['componentView'] == 'false': 
                        self.__handleParamGrp(subchild)
                    else:
                        # treating the componentView=true as a grid component
                        subGridParser = GridParser(subchild, self.grid, isParamGroup=True)
                        # Handle child grid components of this one (True = recursive)
                        child=subGridParser.add(True,False)
                        logging.debug("Adding sub-grid (parameter group) (paramgroup %s to grid %s)"%(child.abbrev, grid.abbrev))
                        grid.grids.add(child)                  
                elif subchild.tag == 'parameter':
                    print logging.info('OOOOOOOPPPPPPs')
                    self.__handleParam(subchild)
                else:
                    logging.debug('Ignoring tag %s for %s'%(subchild.tag,self.grid))

        grid.save()
        return grid
    
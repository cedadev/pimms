from lxml import etree as ET
from pimms.apps.qn.models import *
from pimms.apps.qn.utilities import atomuri
from pimms.apps.qn.qnsetup.XMLinitialiseQ import VocabList

# This file has the NumericalModel class, which is independent of the django views (but not
# the django strage), used to instantiate numerical models from xml versions of the mindmaps,
# and to produce xml instances of the django storage.


#os.environ['DJANGO_SETTINGS_MODULE'] = 'pimms.settings'
from django.conf import settings
logging=settings.LOG

Realms=VocabList['Realms']


def initialiseModel(qn, cvlist):
    ''' 
    Setup a dummy template for model copying 
    '''

    m = NumericalModel(qn, cvlist, xml=True)
    return True


class NumericalModel:
    
    ''' Handles the creation of a model instance in the database, either from XML storage
    or from a pre-existing instance '''
    
    def __init__(self, qn, cvlist, id=0, xml=False):
        ''' Initialise by copy from django storage, or build a new one from the XML '''
        
        self.qn = qn
        
        if id == 0: 
            xml=True
            
        if xml and id <> 0:
            raise ValueError('Incompatible arguments to numerical model')
          
        if id <> 0:
            self.top = Component.objects.get(id=id)
        elif xml:
            self.makeEmptyModel(qn)
            self.read(cvlist)
        else:
            raise ValueError('Nothing to do in NumericalModel')
        
    def copy(self):
        new=self.top.makeNewCopy(self.centre)
        logging.debug('Made new model %s with id %s in %s'%(new,new.id,self.centre))
        return new
    
    def makeEmptyModel(self,
                      qn,
                      author=None,
                      contact=None,
                      funder=None,
                      title='Model Template',
                      abbrev='Model Template'):
        
        component = Component(qn=qn, scienceType='model', abbrev='', uri=atomuri(), author=author, contact=contact, funder=funder)
        component.isModel = True
        component.isRealm = False
        component.title = title
        component.abbrev = abbrev
        component.save()
        component.model = component
        component.controlled = True
        component.save()
        
        self.top = component
        logging.debug('Created empty top level model %s' %component)
        # now get a placeholder paramgroup and constraint group
        p = ParamGroup()
        p.save() 
        component.paramGroup.add(p)
        cg = ConstraintGroup(constraint='', parentGroup=p)
        cg.save()

    def read(self, cvlist):
        ''' 
        Read mindmap XML documents to build a complete model description 
        '''
      
        for cv in cvlist:
            x = XMLVocabReader(cv, self.top) 
            x.doParse()   
            self.top.components.add(x.component)
            logging.debug('Mindmap xml file %s added with component id %s' %(cv, x.component.id))
                
        self.top.save()
        logging.info('Created new Model %s' %self.top.id)
    

class XMLVocabReader:
    # original author, Matt Pritchard
    ''' 
    Reads XML vocab structure. 
    '''
  
    def __init__(self, filename, model):
        ''' 
        Initialise from mindmap file 
        '''
        
        self.etree = ET.parse(filename)
        self.root = self.etree.getroot() # should be the "vocab" element
        self.model = model
     
    def doParse(self):
        #!TODO: I have patched this block to return when there are no components.
        #       Check this is works with the rest of the code.
        first = self.root.find('component')
        if first is None:
            logging.info("No components found for model %s" % self.model)
            return

        logging.info("New component: %s for model %s"%(first.attrib['name'],self.model))
        # Initiate new top-level component in django:
        modelParser = ComponentParser(first, self.model)
        self.component=modelParser.add(True)
        self.component.metadataVersion='Mindmap Version %s,  Translation Version %s  (using %s). CMIP5 Questionnaire Version alpha10.'%(
        self.root.attrib['mmrevision'],self.root.attrib['transrevision'],
        self.root.attrib['mmlcrevision'])
        
        
class ComponentParser:
    ''' class for handling all elements '''
    def __init__(self, item, model, isParamGroup=False):
        ''' initialise  parser '''
        self.item = item
        self.model = model
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
        self.component.paramGroup.add(p)
        
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
    
    def __handleParam(self, elem, pg, cg):
        ''' Add new parameter to cg, if cg none, create one in pg '''
        if cg is None:
            cg=ConstraintGroup(constraint='',parentGroup=pg)
            cg.save()
        paramName=elem.attrib['name']
        choiceType=elem.attrib['choice']
        logging.debug('For %s found parameter %s with choice %s'%(self.item.attrib['name'],paramName,choiceType))
        try:
            Param={'OR':OrParam,'XOR':XorParam,'keyboard':KeyBoardParam,'couple':ComponentInput}[choiceType]
        except KeyError:
            logging.info('ERROR: Ignoring parameter %s'%paramName)
            return
        if choiceType in ['OR','XOR']:
            #create and load vocabulary
            v=Vocab(qn=self.model.qn, uri=atomuri(), name=paramName+'Vocab')
            v.save()
            logging.debug('Created vocab %s'%v.name)
            co, info = None, None
            for item in elem:
                if item.tag=='value':
                    # RF append any value definitions to the parameter definition
                    assert len(item)==0 or len(item)==1, "Parse error: a value should have 0 or 1 children"
                    if len(item)==1 :
                        assert item[0].tag=='definition', "Parse error, the child of a value must be a definition element"
                        defn += " "+item.attrib['name']+": "+item[0].text
                    # RF end append
                    value=Term(vocab=v,name=item.attrib['name'])
                    value.save()
                elif item.tag=='definition':
                    defn=item.text
                else:
                    logging.info('Found unexpected tag %s in %s'%(item.tag,paramName))
            logging.debug('L %s %s '%(paramName, defn))
            p=Param(name=paramName, constraint=cg, vocab=v,definition=defn, controlled=True)
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
               
    def add(self, doSubs, realm=None):
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
        component = Component(
                title='',
                scienceType=self.item.attrib['name'],
                abbrev=nameWithSpaces,
                controlled=True,
                isParamGroup=self.isParamGroup,
                uri=u,
                qn=self.model.qn,
                contact=self.model.contact,
                author=self.model.author,
                funder=self.model.funder)
        component.save() # we need a primary key value so we can add subcomponents later
        self.component=component # used to assign parameters ...
        
        logging.debug('Handling Component %s (%s)'%(component.abbrev,component.scienceType))
        if component.scienceType in Realms:
            realm=component
            component.model=self.model
            component.isRealm=True
            component.realm=component
        else:
            component.model=self.model
            # if realm doesn't exist, then somehow we've broken our controlled vocab
            # realm relationship.
            component.realm=realm
            
        if doSubs:
            #temporary
            for subchild in self.item:
                if subchild.tag == "component":
                    logging.debug("Found child : %s"%subchild.tag)
                    subComponentParser = ComponentParser(subchild, self.model)
                    # Handle child components of this one (True = recursive)
                    child=subComponentParser.add(True,realm=realm)
                    logging.debug("Adding sub-component %s to component %s (model %s, realm %s)"%(child.abbrev, component.abbrev,child.model,child.realm))
                    component.components.add(child)
                elif subchild.tag == 'parametergroup': 
                    if subchild.attrib['componentView'] == 'False' or subchild.attrib['componentView'] == 'false':
                        self.__handleParamGrp(subchild)
                    else:
                        # treating the componentView=true as a component
                        subComponentParser = ComponentParser(subchild, self.model, isParamGroup=True)
                        # Handle child components of this one (True = recursive)
                        child=subComponentParser.add(True,realm=realm)
                        logging.debug("Adding sub-component (parameter group) (paramgroup %s to component %s (model %s, realm %s)"%(child.abbrev, component.abbrev,child.model,child.realm))
                        component.components.add(child)
                elif subchild.tag == 'parameter':
                    print logging.info('OOOOOOOPPPPPPs')
                    self.__handleParam(subchild)
                else:
                    logging.debug('Ignoring tag %s for %s'%(subchild.tag,self.component))
   	
        component.save()
        return component
                
class TestFunctions(unittest.TestCase):
    ''' We can have real unittests for this, because it's independent of the webserver '''
    def setUp(self):
        try:
            self.centre=Centre.objects.get(abbrev="CMIP5")
        except: 
            u=atomuri()
            c=Centre(abbrev='CMIP5',name='Dummy testing version',
                     uri=u)
            logging.debug('Created dummy centre for testing')
            c.save()
            self.centre=c 
       
    def test0ReadFromXML(self):
        
        nm=NumericalModel(self.centre,xml=True)
        
        c=nm.top
        self.assertEqual(c.scienceType,'model')
        self.assertEqual(True,c.isModel)
        self.assertEqual(False,c.isRealm)
        
        for c in nm.top.components.all().order_by('id'):
            self.assertEqual(True,c.scienceType in Realms)
            self.assertEqual(True,c.isRealm)
            self.assertEqual(False,c.isModel)
        
        self.nm=nm
            
    def NOtest1CopyModel(self):
        
        model=Component.objects.filter(abbrev='GCM Template')[0]
        logging.info('Test 1 using component %s'%model.id)
        nm=NumericalModel(self.centre,id=model.id)
        
        model=nm.top
        copy=nm.copy()
         
        self.assertEqual(str(model.title),str(copy.title))
        self.assertEqual(str(model.model),str(copy.model))
            
        originalRealms=model.components.all().order_by('id')
        copyRealms=copy.components.all().order_by('id')
        
        for i in range(len(originalRealms)):
            self.assertEqual(str(originalRealms[i].abbrev),str(copyRealms[i].abbrev))
        

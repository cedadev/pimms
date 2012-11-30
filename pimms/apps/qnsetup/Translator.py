
from pimms.apps.qn.models import *

from pimms.apps.initialiser.XMLinitialiseQ import QuestionniareConfiguration

from lxml import etree as ET
import uuid
import datetime
import string
import re

from django.conf import settings
logging=settings.LOG

# setting up regular expression mapper for illegal xml characters
# from http://boodebr.org/main/python/all-about-python-and-unicode#UNI_XML
RE_XML_ILLEGAL = u'([\u0000-\u0008\u000b-\u000c\u000e-\u001f\ufffe-\uffff])' + \
                 u'|' + \
                 u'([%s-%s][^%s-%s])|([^%s-%s][%s-%s])|([%s-%s]$)|(^[%s-%s])' % \
                  (unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),
                   unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),
                   unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff))


class Translator:


    ''' Translates a questionnaire Doc class (Simulation, Component, (Ensemble) or Platform) into a CIM document (as an lxml etree instance) '''

    # only valid CIM will be output if the following is set to true. This means that all information will not be output as some does not align with the CIM structure (ensembles and genealogy in particular).
    VALIDCIMONLY=True

    CIM_NAMESPACE = "http://www.purl.org/org/esmetadata/cim/1.5/schemas"
    SCHEMA_INSTANCE_NAMESPACE = "http://www.w3.org/2001/XMLSchema-instance"
    SCHEMA_INSTANCE_NAMESPACE_BRACKETS = "{"+SCHEMA_INSTANCE_NAMESPACE+"}"
    CIM_URL = CIM_NAMESPACE+"/"+"cim.xsd"
    GML_NAMESPACE = "http://www.opengis.net/gml/3.2"
    GML_NAMESPACE_BRACKETS="{"+GML_NAMESPACE+"}"    
    GMD_NAMESPACE = "http://www.isotc211.org/2005/gmd"
    GMD_NAMESPACE_BRACKETS="{"+GMD_NAMESPACE+"}"
    GCO_NAMESPACE = "http://www.isotc211.org/2005/gco"
    GCO_NAMESPACE_BRACKETS="{"+GCO_NAMESPACE+"}"
    XLINK_NAMESPACE = "http://www.w3.org/1999/xlink"
    XLINK_NAMESPACE_BRACKETS="{"+XLINK_NAMESPACE+"}"
    NSMAP = {None    : CIM_NAMESPACE,             \
             "xsi"   : SCHEMA_INSTANCE_NAMESPACE, \
             "gml"   : GML_NAMESPACE,             \
             "gmd"   : GMD_NAMESPACE,             \
             "gco"   : GCO_NAMESPACE,             \
             "xlink" : XLINK_NAMESPACE}

    def __init__(self):
        ''' Set any initial state '''
        self.recurse=True
        self.outputComposition=False # aka coupling information
        self.simClass=None

    def c2text(self,c):
        ''' provide a textual (html) view of the status of a component '''
        comp=ET.Element('div')
        
        ET.SubElement(comp,'h1').text='Component details'

        # component location in the hierarchy
        tmpComp=c
        compHierarchy=''
        while not tmpComp.isModel :
            parents=Component.objects.filter(components=tmpComp)
            assert len(parents)==1 ,'I am expecting one and only one parent'
            tmpComp=parents[0]
            compHierarchy='/'+tmpComp.abbrev+compHierarchy
        ET.SubElement(comp,'p').text='Location : '+compHierarchy
            
        '''shortName'''
        ET.SubElement(comp,'p').text='Short Name : '+c.abbrev
        '''longName'''
        ET.SubElement(comp,'p').text='Long Name : '+c.title
        '''description'''
        ET.SubElement(comp,'p').text='Description : '+c.description

        # add any references
        ET.SubElement(comp,'h1').text='References ['+str(len(c.references.all()))+']'
        for reference in c.references.all():
            #ET.SubElement(comp,'p').text='name: '+reference.name
            ET.SubElement(comp,'p').text=reference.citation
            #ET.SubElement(comp,'p').text='link: '+reference.link
            #if reference.refType :
            #    ET.SubElement(comp,'p').text='type: '+reference.refType.value

        ET.SubElement(comp,'h1').text='Properties'
        
        table=ET.SubElement(comp,'table',{'border':'1'})
        titleRow=ET.SubElement(table,'tr')
        ET.SubElement(titleRow,'td').text='Property'
        ET.SubElement(titleRow,'td').text='Definition'
        ET.SubElement(titleRow,'td').text='Type'
        ET.SubElement(titleRow,'td').text='Options'
        ET.SubElement(titleRow,'td').text='Value'

        for pg in c.paramGroup.all().order_by('id'):
            constraintSet=ConstraintGroup.objects.filter(parentGroup=pg).order_by('id')
            for con in constraintSet:
                #
                # we need to keep the parameters in the same order
                # as they are in the questionnaire. Therefore we can
                # not treat XOR, then OR, then KeyBoard. I don't know
                # how to determine a derived class from a base class.
                # So here is a rubbish solution that works!
                # RF: one can now get at a child object (get_child)
                # so we could simplify the code below, but as it works ...
                #
                # Needed to add .order_by('id') as the database does not guarantee
                # to return objects in the same order, hence the order of the baseclass
                # objects might not be the same as the Xor, Or, or KeyBoard objects
                # whereas this code assumes the same order.
                #
                BaseParamSet=BaseParam.objects.filter(constraint=con).order_by('id')
                XorParamSet=XorParam.objects.filter(constraint=con).order_by('id')
                OrParamSet=OrParam.objects.filter(constraint=con).order_by('id')
                KeyBoardParamSet=KeyBoardParam.objects.filter(constraint=con).order_by('id')
                XorIDX=0
                OrIDX=0
                KeyBoardIDX=0
                for bp in BaseParamSet:
                    found=False
                    if not(found) and XorIDX<XorParamSet.count() :
                        if bp.name == XorParamSet[XorIDX].name :
                            found=True
                            p=XorParamSet[XorIDX]
                            XorIDX+=1
                            ptype="XOR"
                    if not(found) and OrIDX<OrParamSet.count() :
                        if bp.name == OrParamSet[OrIDX].name :
                            found=True
                            p=OrParamSet[OrIDX]
                            OrIDX+=1
                            ptype="OR"
                    if not(found) and KeyBoardIDX<KeyBoardParamSet.count() :
                        if bp.name == KeyBoardParamSet[KeyBoardIDX].name :
                            found=True
                            p=KeyBoardParamSet[KeyBoardIDX]
                            KeyBoardIDX+=1
                            ptype="KeyBoard"
                    assert found, "Found must be true at this point"
                    row=ET.SubElement(table,'tr')
                    if con.constraint!='' :
                        ET.SubElement(row,'td').text=pg.name+':['+con.constraint+']'+p.name
                    else :
                        ET.SubElement(row,'td').text=pg.name+':'+p.name
                    '''definition'''
                    ET.SubElement(row,'td').text=p.definition
                    '''value'''
                    if ptype=='XOR' :
                        ET.SubElement(row,'td').text='One value from list'
                    elif ptype=='OR' :
                        ET.SubElement(row,'td').text='One or more values from list'
                    elif ptype=='KeyBoard' :
                        myUnits=""
                        if p.units :
                            myUnits=p.units
                        ValueType=""
                        if p.numeric :
                            ValueType="numeric"
                        else :
                            ValueType="string"
                        myType=""
                        ET.SubElement(row,'td').text='Unrestricted (units="'+myUnits+'") (type="'+ValueType+'")'
                    else :
                        assert False, "Unrecognised type"

                    if ptype=='XOR' or ptype=='OR' :
                        ''' I should be constrained by vocab '''
                        assert p.vocab, 'I should have a vocabulary'
                        ''' find all values associated with this vocab '''
                        # all values that are part of this vocab
                        valset=Term.objects.filter(vocab=p.vocab)
                        vocabValues=""
                        counter=0
                        for v in valset:
                            '''name'''
                            counter+=1
                            vocabValues+=v.name
                            if counter != len(valset) :
                                vocabValues+=", "
                        ET.SubElement(row,'td').text=vocabValues
                    elif ptype=='KeyBoard':
                        ET.SubElement(row,'td').text='n/a'
                    else :
                        assert False, "Unrecognised type"

                    values=''
                    if ptype=='KeyBoard':
                        values=p.value
                    elif ptype=='XOR':
                        if p.value :
                            values=p.value.name
                    elif ptype=='OR':
                        if p.value :
                            valset=p.value.all()
                            counter=0
                            for value in valset :
                                counter+=1
                                values+=value.name
                                if counter != len(valset) :
                                    values+=", "
                    else:
                        assert False, "Unrecognised type"
                    ET.SubElement(row,'td').text=values

        return comp

    def cimDocumentSetRoot(self):
        ''' return the top level cim document invarient structure for a recordset'''
        root=ET.Element('CIMDocumentSet', \
                             attrib={self.SCHEMA_INSTANCE_NAMESPACE_BRACKETS+"schemaLocation": self.CIM_URL}, \
                             nsmap=self.NSMAP)
        return root

    def q2cim(self,ref,docType):

        # check whether this object is marked as deleted. This code should never called if the object is deleted so throw an error if this is the case.
        assert not(ref.isDeleted),"GerryWobbler error: An object that has been marked as deleted is being translated to XML"
        ''' primary public entry point. '''
        method_name = 'add_' + str(docType)
        logging.debug("q2cim calling "+method_name)
        method = getattr(self, method_name)
        # make a special case for simulation as we output
        # all information associated with a simulation
        # using a CIMDocumentSet
        if method_name=='add_simulation' :
            # save our simulation instance so the composition can pick it up
            self.simClass=ref
            root=self.cimDocumentSetRoot()
            #modelElement=self.cimRecord(root)
            #self.add_component(ref.numericalModel,modelElement)
            self.add_component(ref.numericalModel,root)
            #simulationElement=self.cimRecord(root)
            #self.add_simulation(ref,simulationElement)
            self.add_simulation(ref,root)
            if ref.ensembleMembers>1 :
                #ensembleElement=self.cimRecord(root)
                #self.add_ensemble(ref,ensembleElement)
                self.add_ensemble(ref,root)
            #experimentElement=self.cimRecord(root)
            #self.add_experiment(ref.experiment,experimentElement)
            if str(ref.experiment).partition(' ')[2] in ["decadal", "noVolc"]:
                # if start date is january 1st this will apply to a simulation
                # for the year before
                if str(ref.duration.startDate.mon) == '1' and str(ref.duration.startDate.day) == '1':
                    startyear = str(ref.duration.startDate.year - 1)
                else: 
                    startyear = str(ref.duration.startDate.year)
                    
                self.add_experiment(ref.experiment, root,
                                    startyear = startyear)
            else:
                self.add_experiment(ref.experiment,root)
            #platformElement=self.cimRecord(root)
            #self.add_platform(ref.platform,platformElement)
            self.add_platform(ref.platform,root)

            uniqueFileList=[]
            couplings=ref.numericalModel.couplings(simulation=self.simClass)
            for coupling in couplings :
                externalClosures=ExternalClosure.objects.filter(coupling=coupling)
                for externalClosure in externalClosures :
                    if externalClosure.targetFile not in uniqueFileList :
                        uniqueFileList.append(externalClosure.targetFile)
            for fileObject in uniqueFileList :
                #dataObjectElement=self.cimRecord(root)
                #self.add_dataobject(fileObject,dataObjectElement)
                self.add_dataobject(fileObject,root)

            # find all unique grid references in our model
            uniqueGridList=[]
            myModel=ref.numericalModel
            self.componentWalkGrids(myModel,uniqueGridList)
            for gridObject in uniqueGridList :
                #gridObjectElement=self.cimRecord(root)
                #self.add_gridobject(gridObject,gridObjectElement)
                self.add_gridobject(gridObject,root)
            cimDoc=root
        else :
            root=ET.Element("tmp_container",nsmap=self.NSMAP)
            cimDoc=method(ref,root)
            # remove our temporary container element
            cimDoc=cimDoc[0]
            # add in our namespace. Note NSMAP is propogated to children so should be OK as we set it for the original root element tmp_container
            cimDoc.attrib[self.SCHEMA_INSTANCE_NAMESPACE_BRACKETS+"schemaLocation"]=self.CIM_URL
        return cimDoc
        
    def componentWalkGrids(self,c,uniqueGridList) :
        if c.implemented :
            if c.grid :
                if c.grid not in uniqueGridList :
                    uniqueGridList.append(c.grid)
            for child in c.components.all():
                self.componentWalkGrids(child,uniqueGridList)

    def componentWalkComposition(self,c,rootElement) :
        if c.implemented :
            self.addComposition(c,rootElement)
            rootElement.append(ET.Comment('Looking in component '+c.abbrev))
            for child in c.components.all():
                self.componentWalkComposition(child,rootElement)

    def add_gridobject(self,gridObject,rootElement) :

        # get mnemonic from the top level
        MnemonicValue=''
        for pg in gridObject.paramGroup.all():
            if pg.name=="General Attributes" :
                constraintSet=ConstraintGroup.objects.filter(parentGroup=pg)
                for con in constraintSet :
                    BaseParamSet=BaseParam.objects.filter(constraint=con).order_by('id')
                    for bp in BaseParamSet:
                        if bp.name=="Mnemonic":
                            childBP=bp.get_child_object()
                            MnemonicValue=childBP.value

        # get our horizontal and vertical grid property pages
        # the assumption here is that horizontal is stored before vertical.
        childList=gridObject.grids.all().order_by('id')
        assert len(childList)==2, "expecting 2 grid subcomponents (horizontal and vertical properties) but found "+len(childList)
        horizontalPropertiesObject=childList[0]
        verticalPropertiesObject=childList[1]

        # extract our horizontal properties
        HorizGridDiscretization=""
        HorizGridType=""
        HorizResProps={}
        HorizGridMnemonic=""
        for pg in horizontalPropertiesObject.paramGroup.all():
            if pg.name=="HorizontalCoordinateSystem" :
                # We rely on the constraint set objects appearing in our list in the same order as they appear in the questionnaire. We rely on this as the information we gather from this affects what we need to read from the others. The order_by('id') should sort this out but I've put a check in the code (for the first constraint only) just in case.
                first=True
                constraintSet=ConstraintGroup.objects.filter(parentGroup=pg).order_by('id')
                for con in constraintSet:
                    assert (con.constraint=="" and first) or (con.constraint!="" and not(first)), "Error, the first constraint set should have no associated constraint and there should only be one constraint set with no constraint"
                    #rootElement.append(ET.Comment('constraint : '+con.constraint))
                    BaseParamSet=BaseParam.objects.filter(constraint=con).order_by('id')
                    for bp in BaseParamSet :
                        p=bp.get_child_object()
                        if con.constraint=="" :
                            first=False
                            # first set of values have no constraint
                            if bp.name=="GridMnemonic" :
                                HorizGridMnemonic=unicode(str(p.value))
                            if bp.name=="GridDiscretization" :
                                if p.value!="None" :
                                    HorizGridDiscretization=unicode(str(p.value))
                                else :
                                    HorizGridDiscretization=""
                            elif bp.name=="GridResolution" :
                                #HorizGridResolution=unicode(str(p.value))                                
                                HorizGridResolution = p.value
                            elif bp.name=="GridRefinementScheme" :
                                HorizGridRefinement=unicode(str(p.value))
                        elif HorizGridDiscretization!="" and str(con.constraint).find(HorizGridDiscretization)!=-1 and str(con.constraint).find("GridDiscretization")!=-1 :
                            if bp.name=="GridType" :
                                HorizGridType=unicode(str(p.value))
                            elif bp.name=="CompositeGridDiscretization" :
                                HorizGridChildNames=[]
                                for term in p.value.all() :
                                    HorizGridChildNames.append(term.name)
                            elif bp.name=="CompositeGrid" :
                                HorizGridCompositeName=unicode(str(p.value))
                            elif bp.name=="SpectralTruncatureNumber" :
                                HorizResProps[str(bp.name)]=unicode(str(p.value))
                            else :
                                assert False, "Error : Unknown grid property found: "+bp.name
                        elif HorizGridType!="" and str(con.constraint).find(HorizGridType)!=-1 and str(con.constraint).find("GridType")!=-1 :
                            HorizResProps[str(bp.name)]=unicode(str(p.value))
                        else :
                            # I am called if all the information has not been filled in.
                            pass
                            
            elif pg.name=="HorizontalExtent" :
                constraintSet=ConstraintGroup.objects.filter(parentGroup=pg)
                for con in constraintSet:
                    BaseParamSet=BaseParam.objects.filter(constraint=con).order_by('id')
                    for bp in BaseParamSet :
                        p=bp.get_child_object()
                        if bp.name=="LatMin" :
                            HorizExtentLatMin=unicode(str(p.value))
                        elif bp.name=="LatMax" :
                            HorizExtentLatMax=unicode(str(p.value))
                        elif bp.name=="LonMin" :
                            HorizExtentLonMin=unicode(str(p.value))
                        elif bp.name=="LonMax" :
                            HorizExtentLonMax=unicode(str(p.value))
                        else :
                            assert False, "Error : Unknown grid extent property found: "+bp.name

        # extract our vertical properties
        vertCoordType=""
        vertCoord=""
        vertCoordProps={}
        VertResProps={}
        VertDomain=""
        for pg in verticalPropertiesObject.paramGroup.all():
            if pg.name=="VerticalCoordinateSystem" :
                # We rely on the constraint set objects appearing in our list in the same order as they appear in the questionnaire. We rely on this as the information we gather from this affects what we need to read from the others. The order_by('id') should sort this out but I've put a check in the code (for the first constraint only) just in case.
                foundVertCoordType=False
                foundVertCoord=False
                constraintSet=ConstraintGroup.objects.filter(parentGroup=pg).order_by('id')
                for con in constraintSet:
                    assert (con.constraint=="" and not foundVertCoordType) or (con.constraint!="" and foundVertCoordType), "Error, the first constraint set should have no associated constraint and there should only be one constraint set with no constraint"
                    BaseParamSet=BaseParam.objects.filter(constraint=con).order_by('id')
                    for bp in BaseParamSet :
                        p=bp.get_child_object()
                        if con.constraint=="" : 
                            assert not foundVertCoordType,"Error expecting unconstrained property to appear first"
                            foundVertCoordType=True
                            # first set of values have no constraint
                            if bp.name=="VerticalCoordinateType" :
                                vertCoordType=unicode(str(p.value))
                        elif str(con.constraint).find(vertCoordType)!=-1 and foundVertCoordType :
                            if bp.name=="VerticalCoordinate" :
                                assert not foundVertCoord, "Error expecting VerticalCoordinate to appear first"
                                foundVertCoord=True
                                vertCoord=unicode(str(p.value))
                            else:
                                assert foundVertCoord, "Error expecting VerticalCoordinate to appear first"
                                # pick up any other properties within this constraint
                                vertCoordProps[bp.name]=unicode(str(p.value))
                        elif str(con.constraint).find(vertCoord)!=-1 and foundVertCoord :
                            # pick up any properties that depend on vertCoord
                            vertCoordProps[bp.name]=unicode(str(p.value))
                        else :
                            pass

            elif pg.name=="VerticalExtent" :
                first=True
                constraintSet=ConstraintGroup.objects.filter(parentGroup=pg).order_by('id')
                for con in constraintSet:
                    assert (con.constraint=="" and first) or (con.constraint!="" and not(first)), "Error, the first constraint set should have no associated constraint and there should only be one constraint set with no constraint"
                    BaseParamSet=BaseParam.objects.filter(constraint=con).order_by('id')
                    for bp in BaseParamSet :
                        p=bp.get_child_object()
                        if con.constraint=="" :
                            assert first, "Error expecting unconstrained property to appear first"
                            first=False
                            # first set of values have no constraint
                            if bp.name=="Domain" :
                                VertDomain=unicode(str(p.value))
                            else:
                                assert False,"Unknown parameter, expecting 'Domain' but found "+bp.name
                        elif str(con.constraint).find(VertDomain)!=-1 :
                            assert not first, "Error expecting constraint to appear first"
                            assert VertDomain=="atmospheric" or VertDomain=="oceanic", "Error, expecting either ocean or atmosphere but found constraint "+str(con.constraint)
                            VertResProps[str(bp.name)]=unicode(str(p.value))
                        else : # VertDomain should be other or n/a
                            pass
            elif pg.name=="General Attributes" :
                pass
            else :
                assert False, "Found an unknown param group in vertical coordinates"
        
        # now we start creating our grid
        # gml:id can not just be a uuid as it needs to start with a letter so prepend with 'metafor'
        gridElement=ET.SubElement(rootElement,'gridSpec',{self.GML_NAMESPACE_BRACKETS+'id':'metafor'+gridObject.uri})
        #CV expects "_" instead of " " in CV so simply replace any spaces here
        CVHorizGridType=HorizGridType.replace(' ','_')
        # quick bug fix. Should change CV in the questionnaire.
        if CVHorizGridType=='ying_yang' : CVHorizGridType='yin_yang'
        # another CV mapping fix due to CV/CIM mismatch
        if CVHorizGridType=='latitude-longitude' : CVHorizGridType='regular_lat_lon'

        esmModelGridElement=ET.SubElement(gridElement,'esmModelGrid',{'gridType':CVHorizGridType,'id':''})
        # before the simple replacement solution I did an explicit mapping
        #MappingHorizGridType={'displaced pole':'displaced_pole','ying yang':'ying_yang'}
        #esmModelGridElement=ET.SubElement(gridElement,'esmModelGrid',{'gridType':MappingHorizGridType[HorizGridType],'id':''})
        ''' shortName [0..1] '''
        if gridObject.abbrev :
            ET.SubElement(esmModelGridElement,'shortName').text=gridObject.abbrev
        ''' longName [0..1] '''
        if gridObject.title :
            ET.SubElement(esmModelGridElement,'longName').text=gridObject.title
        ''' description [0..1] '''
        if gridObject.description :
            ET.SubElement(esmModelGridElement,'description').text=gridObject.description
        ''' citationList [0..1] '''
        if len(gridObject.references.all())>0:
            refList=ET.SubElement(esmModelGridElement,'citationList')
            self.addReferences(gridObject.references,refList)
        ''' extent [0..1] '''
        ''' mnemonic [0..1] '''
        if MnemonicValue :
            ET.SubElement(esmModelGridElement,'mnemonic').text=MnemonicValue
        ''' gridMosaic or gridTile '''
        CVHorizGridType=HorizGridType.replace(' ','_')
        mappingHorizDiscretizationType={'logically rectangular':'logically_rectangular','structured triangular':'structured_triangular','unstructured triangular':'unstructured_triangular','unstructured polygonal':'unstructured_polygonal','pixel-based catchment':'pixel-based_catchment','spherical harmonics':'spherical_harmonics','other':'other','composite':'composite'}
        if HorizGridDiscretization!="composite" :
            esmModelGridElement.set('isLeaf','true')
            esmModelGridElement.set('numTiles','1')
            esmModelGridElement.set('numMosaics','0')
            gridTileElement=ET.SubElement(esmModelGridElement,"gridTile",{"discretizationType":mappingHorizDiscretizationType[HorizGridDiscretization]}) #,"verticalGridDiscretization":vertCoordType})
            self.addGridTileDescription(gridTileElement,horizontalPropertiesObject,verticalPropertiesObject)
            self.addGridExtent(gridTileElement,HorizExtentLatMin,HorizExtentLatMax,HorizExtentLonMin,HorizExtentLonMax)
            self.addGridTileHorizRes(gridTileElement,HorizGridResolution,HorizGridRefinement,HorizResProps)
            self.addGridTileVertRes(gridTileElement,VertResProps,VertDomain)
            self.addGridTileVertCoords(gridTileElement,vertCoordType,vertCoord,vertCoordProps)
            if HorizGridMnemonic!="" :
                ET.SubElement(gridTileElement,'mnemonic').text=HorizGridMnemonic
        else : # HorizGridDiscretization=="composite"
            esmModelGridElement.set('isLeaf','false')
            esmModelGridElement.set('numTiles','0')
            esmModelGridElement.set('numMosaics','1')
            gridMosaicElement=ET.SubElement(esmModelGridElement,'gridMosaic',{'gridType':HorizGridDiscretization,'isLeaf':'true','numMosaics':'0','id':''})
            if HorizGridCompositeName!="" :
                ET.SubElement(gridMosaicElement,'description').text=HorizGridCompositeName

            self.addGridExtent(gridMosaicElement,HorizExtentLatMin,HorizExtentLatMax,HorizExtentLonMin,HorizExtentLonMax)
            if HorizGridMnemonic!="" :
                ET.SubElement(gridMosaicElement,'mnemonic').text=HorizGridMnemonic
            if HorizGridType=="ying yang":
                gridMosaicElement.set('numTiles','2')
                # ying yang is represented as a gridMosaic with two gridTiles
                for i in range(2):
                    gridTileElement=ET.SubElement(gridMosaicElement,"gridTile",{"discretizationType":'half_torus'})
                    self.addGridTileDescription(gridTileElement,horizontalPropertiesObject,verticalPropertiesObject)
                    self.addGridTileHorizRes(gridTileElement,HorizGridResolution,HorizGridRefinement,HorizResProps)
                    self.addGridTileVertRes(gridTileElement,VertResProps,VertDomain)
                    self.addGridTileVertCoords(gridTileElement,vertCoordType,vertCoord,vertCoordProps)
            elif HorizGridType=="icosahedral":
                gridMosaicElement.set('numTiles','10')
                # icosahedral is represented as a gridMosaic with ten logically rectangular gridTiles
                for i in range(10):
                    gridTileElement=ET.SubElement(gridMosaicElement,"gridTile",{"discretizationType":'logically_rectangular'})
                    self.addGridTileDescription(gridTileElement,horizontalPropertiesObject,verticalPropertiesObject)
                    self.addGridTileHorizRes(gridTileElement,HorizGridResolution,HorizGridRefinement,HorizResProps)
                    self.addGridTileVertRes(gridTileElement,VertResProps,VertDomain)
                    self.addGridTileVertCoords(gridTileElement,vertCoordType,vertCoord,vertCoordProps)
            elif HorizGridType=="other":
                numTiles=len(HorizGridChildNames)
                if numTiles : # make sure some values are provided
                    gridMosaicElement.set('numTiles',str(numTiles))
                    # we have a composite grid
                    for gridTileName in HorizGridChildNames :
                        gridTileElement=ET.SubElement(gridMosaicElement,"gridTile",{"discretizationType":mappingHorizDiscretizationType[gridTileName]})
                        self.addGridTileDescription(gridTileElement,horizontalPropertiesObject,verticalPropertiesObject)
                        self.addGridTileHorizRes(gridTileElement,HorizGridResolution,HorizGridRefinement,HorizResProps)
                        self.addGridTileVertRes(gridTileElement,VertResProps,VertDomain)
                        self.addGridTileVertCoords(gridTileElement,vertCoordType,vertCoord,vertCoordProps)
            #else : output nothing

        self.addDocumentInfo(gridObject,gridElement)

    def addGridTileDescription(self,rootElement,horizontalPropertiesObject,verticalPropertiesObject) :
        description=""
        if horizontalPropertiesObject.description :
            description="Horizontal properties: "+horizontalPropertiesObject.description
        if horizontalPropertiesObject.description and verticalPropertiesObject.description :
            description+=" "
        if verticalPropertiesObject.description :
            description+="Vertical properties: "+verticalPropertiesObject.description
        if description!="" :
            ET.SubElement(rootElement,'description').text=description

    def addGridTileHorizRes(self,gridTileElement,HorizGridResolution,HorizGridRefinement,HorizResProps) :
        description=HorizGridResolution
        if HorizGridRefinement!="" :
            description+=". Refinement details: "+HorizGridRefinement
        horizResElement=ET.SubElement(gridTileElement,"horizontalResolution",{"description":description})
        for attrib in HorizResProps.keys() :
            propElement=ET.SubElement(horizResElement,"property")
            ET.SubElement(propElement,"value").text=HorizResProps[attrib]
            ET.SubElement(propElement,"name").text=attrib

    def addGridTileVertCoords(self,gridTileElement,vertCoordType,vertCoord,vertCoordProps) :
        vertCoordsElement=ET.SubElement(gridTileElement,"zcoords",{'coordinateType':vertCoordType, 'coordinateForm':vertCoord})
        for attrib in vertCoordProps.keys() :
            propElement=ET.SubElement(vertCoordsElement,"property")
            ET.SubElement(propElement,"value").text=vertCoordProps[attrib]
            ET.SubElement(propElement,"name").text=attrib

    def addGridTileVertRes(self,gridTileElement,VertResProps,VertDomain) :
        gridTileElement.append(ET.Comment('Vertical Domain specified as : '+VertDomain))
        if VertResProps:
            vertResElement=ET.SubElement(gridTileElement,"verticalResolution")
            for attrib in VertResProps.keys() :
                propElement=ET.SubElement(vertResElement,"property")
                ET.SubElement(propElement,"value").text=VertResProps[attrib]
                ET.SubElement(propElement,"name").text=attrib

    def addGridExtent(self,gridTileElement,HorizExtentLatMin,HorizExtentLatMax,HorizExtentLonMin,HorizExtentLonMax) :
        horizResElement=ET.SubElement(gridTileElement,"extent")
        ET.SubElement(horizResElement,"latMin").text=HorizExtentLatMin
        ET.SubElement(horizResElement,"latMax").text=HorizExtentLatMax
        ET.SubElement(horizResElement,"lonMin").text=HorizExtentLonMin
        ET.SubElement(horizResElement,"lonMax").text=HorizExtentLonMax

    def add_ensemble(self,simClass,rootElement):

        ensembleClassSet=Ensemble.objects.filter(simulation=simClass)
        assert(len(ensembleClassSet)==1,'Simulation %s should have one and only one associated ensembles class'%simClass)
        ensembleClass=ensembleClassSet[0]

        ensembleElement=ET.SubElement(rootElement,'ensemble')
        ''' responsibleParty [0..inf] '''
        self.addResp(simClass.centre.party,ensembleElement,'centre')
        ''' fundingSource [0..inf] '''
        ''' rationale [0..inf] '''
        ''' project [0->inf] '''
        ''' shortName [1] '''
        ET.SubElement(ensembleElement,'shortName').text=simClass.abbrev
        ''' longName [1] '''
        ET.SubElement(ensembleElement,'longName').text=simClass.title
        ''' description [0..1] '''
        ET.SubElement(ensembleElement,'description').text=ensembleClass.description
        ''' dataHolder [0..inf] '''
        ''' supports [1..inf] '''
        supportsElement=ET.SubElement(ensembleElement,'supports')
        self.addCIMReference(simClass.experiment,supportsElement)
        ''' output [0..inf] '''
        ''' ensembleType [1..inf] '''
        if ensembleClass.etype :
            self.addCVValue(ensembleElement,'ensembleType',ensembleClass.etype.name)
        ''' ensembleMember [2..inf] '''    
        ensMemberClassSet=EnsembleMember.objects.filter(ensemble=ensembleClass)
        assert(len(ensembleClassSet)>0),'Ensemble %s should have at least two ensemble members'%ensembleClass
        # first add in our control member
        ensMemberElement=ET.SubElement(ensembleElement,'ensembleMember')
        simulationElement=ET.SubElement(ensMemberElement,'simulation')
        refElement=self.addCIMReference(simClass,simulationElement)
        self.addCVValue(ensMemberElement,'ensembleMemberID',simClass.drsMember,cvName='DRS_CMIP5_ensembleType')
        # now add in our modified members
        for ensMemberClass in ensMemberClassSet :
            if ensMemberClass.drsMember :
                ensMemberElement=ET.SubElement(ensembleElement,'ensembleMember')
                simulationElement=ET.SubElement(ensMemberElement,'simulation')
                refElement=self.addCIMReference(simClass,simulationElement)
                if ensMemberClass.cmod :
                    self.addModelMod(ensMemberClass.cmod,refElement)
                if ensMemberClass.imod :
                    self.addInputMod(ensMemberClass.imod,refElement)
                #extIDElement=ET.SubElement(ensMemberElement,'externalID')
                #ET.SubElement(extIDElement,'name').text=ensMemberClass.drsMember
                #ET.SubElement(extIDElement,'standard',{'value':'DRS'})
                self.addCVValue(ensMemberElement,'ensembleMemberID',ensMemberClass.drsMember,cvName='DRS_CMIP5_ensembleType',standard=True)

        myEnsembleDoc=ensembleClass.makeDoc()
        self.addDocumentInfo(myEnsembleDoc,ensembleElement)
        
    def addModelMod(self,modClass,rootElement):
        changeElement=ET.SubElement(rootElement,"change",{'type':modClass.mtype.name})
        ET.SubElement(changeElement,'name').text=modClass.mnemonic
        if modClass.component :
            targetElement=ET.SubElement(changeElement,"changeTarget")
            # if we define a property (parameter) in this modification
            # and this property already exists in the associated
            # component then reference the property, otherwise reference
            # the component. Note, we do a case insensitive search.
            componentClass=modClass.component
            found=False
            for pg in componentClass.paramGroup.all() :
                constraintSet=ConstraintGroup.objects.filter(parentGroup=pg)
                for con in constraintSet:
                    BaseParamSet=BaseParam.objects.filter(constraint=con)
                    for bp in BaseParamSet:
                        #ET.SubElement(targetElement,"DEBUG_PARAM_NAME").text=bp.name
                        # perform a case insensitive search
                        if bp.name.lower()==modClass.k.lower() :
                            found=True
                            break
                        if found : break
                    if found : break
                if found : break
            if found :
                self.addCIMReference(modClass.component,targetElement,argName=modClass.k,argType='componentProperty')
            else :
                self.addCIMReference(modClass.component,targetElement)

        detailElement=ET.SubElement(changeElement,'detail')
        if modClass.v :
            ET.SubElement(detailElement,'value').text=str(modClass.v)
        if modClass.k :
            ET.SubElement(detailElement,'name').text=modClass.k
        ET.SubElement(detailElement,'description').text=modClass.description

    def addInputMod(self,modClass,rootElement):
        changeElement=ET.SubElement(rootElement,"change",{'type':modClass.inputTypeModified.name})
        ET.SubElement(changeElement,'name').text=modClass.mnemonic
        #if modClass.memberStartDate :
        try:
            changeElement.append(modClass.memberStartDate.xml('changeDate'))
        except:
            logging.debug("input mod start date doesn't exist")
        detailElement=ET.SubElement(changeElement,'detail')
        ET.SubElement(detailElement,'description').text=modClass.description

    def add_simulation(self,simClass,rootElement):

            #single simulation
            simElement=ET.SubElement(rootElement,'simulationRun')
            ''' responsibleParty [0..inf] '''
            self.addResp(simClass.contact,simElement,'contact')
            self.addResp(simClass.author,simElement,'author')
            self.addResp(simClass.funder,simElement,'funder')
            self.addResp(simClass.centre.party,simElement,'centre')
            ''' fundingSource [0..inf] '''
            ''' rationale [0..inf] '''
            ''' project [0..inf] '''
            if QuestionniareConfiguration is 'cmip5':
                self.addCVValue(simElement,'project','CMIP5',isOpen=False)
            ''' longName [1] and shortName [1] '''
            if simClass.ensembleMembers>1 :
                # our simulation is really the base simulation of an ensemble
                ''' shortName [1] '''
                ET.SubElement(simElement,'shortName').text=simClass.abbrev
                ''' longName [1] '''
                ET.SubElement(simElement,'longName').text=simClass.title
            else :
                ''' shortName [1] '''
                if simClass.abbrev:
                    ET.SubElement(simElement,'shortName').text=simClass.abbrev
                ''' longName [1] '''
                # longName is optional in the Questionnaire but required in the CIM.
                # Therefore always provide the element even if it is empty.
                ET.SubElement(simElement,'longName').text=simClass.title
            ''' description [0..1] '''
            if simClass.description:
                ET.SubElement(simElement,'description').text=simClass.description
            ''' supports [1..inf] '''
            experimentElement=ET.SubElement(simElement,'supports')
            if QuestionniareConfiguration is 'cmip5':
                # split our experiment name into its component parts
                expName,sep,expShortName=simClass.experiment.abbrev.partition(' ')
                # check that the format is as expected
                assert sep!="", "Error, experiment short name does not conform to format 'id name'"
                assert expShortName and expShortName!='', "Error, experiment short name does not conform to format 'id name'"
                # treat some experiments as special cases
                if expShortName in ["decadal","noVolc"]:
                    # we need to append the user supplied simulation duration to get the required local experiment name
                    assert simClass.duration.startDate, "Error, simulation must have a start date specified"

                    # if start date is january 1st this will apply to a simulation
                    # for the year before
                    if str(simClass.duration.startDate.mon) == '1' and str(simClass.duration.startDate.day) == '1':
                        simStartDate = str(simClass.duration.startDate.year - 1)
                    else:
                        simStartDate=str(simClass.duration.startDate.year)
                    self.addCIMReference(simClass.experiment,experimentElement,argName=expShortName+simStartDate,argType="experiment",description="Reference to an Experiment called "+expShortName+" with experimentNumber "+expName+" which this simulation has specialised as "+expShortName+simStartDate)
                else:
                    # just use the experiment name
                    self.addCIMReference(simClass.experiment,experimentElement,argName=expShortName,argType="experiment",description="Reference to an Experiment called "+expShortName+" with experimentNumber "+expName)
            else:
                # we are not a cmip5 configuration
                self.addCIMReference(simClass.experiment,experimentElement)
            ''' simulationID [0..1] '''
            ''' calendar [1] '''
            if simClass.experiment.requiredCalendar :
                calendarElement=ET.SubElement(simElement,'calendar')
                ''' CIM choices : daily-360, realCalendar, perpetualPeriod '''
                calTypeElement=ET.SubElement(calendarElement,str(simClass.experiment.requiredCalendar.name))
            else :
                assert False, "Error, a calendar must exist"
            ''' input [0..inf] '''
            # add in our model bindings (couplings)
            couplings=simClass.numericalModel.couplings(simulation=simClass)
            for coupling in couplings:
                # output each link separately as the questionnaire keeps information
                # about transformations on a link by link basis
                if coupling.notInUse :
                    pass # the user has asked us to skip this binding
                else:
                    extclosures=ExternalClosure.objects.filter(coupling=coupling)
                    for closure in extclosures :
                        self.addCoupling(coupling,closure,simElement,elementName='input')
                    intclosures=InternalClosure.objects.filter(coupling=coupling)
                    for closure in intclosures :
                        self.addCoupling(coupling,closure,simElement,elementName='input')

            ''' output [0..inf] '''
            ''' restart [0..inf] '''
            ''' spinupDateRange [0..1] '''
            ''' spinupSimulation [0..1] '''
            relatedSimulations=SimRelationship.objects.filter(sfrom=simClass)
            assert len(relatedSimulations)==1, "Expecting related simulations to be of size 1"
            relatedSimulation=relatedSimulations[0]
            if relatedSimulation.value :
                if str(relatedSimulation.value)=='usesSpinup':
                    #capture relationship as a spinup reference
                    spinupElement=ET.SubElement(simElement,'spinupSimulation')
                    self.addCIMReference(relatedSimulation.sto,spinupElement,description=relatedSimulation.description)
            ''' controlSimulation [0..1]'''
            relatedSimulations=SimRelationship.objects.filter(sfrom=simClass)
            assert len(relatedSimulations)==1, "Expecting related simulations to be of size 1"
            relatedSimulation=relatedSimulations[0]
            if relatedSimulation.value :
                if str(relatedSimulation.value)=='hasControlSimulation':
                    #capture relationship as a control reference
                    controlElement=ET.SubElement(simElement,'controlSimulation')
                    self.addCIMReference(relatedSimulation.sto,controlElement,description=relatedSimulation.description)
            ''' authorsList [0..1] '''
            alElement=ET.SubElement(simElement,'authorsList')
            assert simClass.authorList!='', "Error authorList must have some content"
            ET.SubElement(alElement,'list').text=simClass.authorList
            ''' conformance [0..inf] '''
            confClassSet=Conformance.objects.filter(simulation=simClass)
            for confClass in confClassSet:
                if (confClass.ctype) : # I have a conformance specified
                    conf1Element=ET.SubElement(simElement,'conformance')
                    if confClass.ctype.name=='Not Conformant' :
                        conformant='false'
                    else :
                        conformant='true'
                    
                    ''' description [0..1] '''
                    mappedConformanceType=string.lower(confClass.ctype.name)
                    
                    if mappedConformanceType=='via combination' :
                        mappedConformanceType='combination'
                    confElement=ET.SubElement(conf1Element,'conformance',{'conformant':conformant,'type':mappedConformanceType})
                    ET.SubElement(confElement,'description').text=confClass.description
                    ''' frequency [0..1] '''
                    ''' requirement [1..inf] '''
                    reqElement=ET.SubElement(confElement,'requirement')
                    # get experiment class as the reference
                    ExperimentSet=Experiment.objects.filter(requirements=confClass.requirement).filter(isDeleted=False)
                    assert len(ExperimentSet)==1, 'A requirement should have one and only one parent experiment.'
                    experiment=ExperimentSet[0]
                    assert confClass.requirement, 'There should be a requirement associated with a conformance'
                    
                    if confClass.option :
                        #we have chosen a requirement option so use this ID in our reference
                        if confClass.option.docid:
                            reqID=confClass.option.docid
                    else :
                        # we have chosen a requirement so use this ID in our reference
                        reqID=confClass.requirement.docid
                    
                    # below to deal with situations where a user marks a 
                    # conformance as 'not applicable' and does not choose one 
                    # of the requirement options      
                    #if len(reqID) == 0:
                    if mappedConformanceType == 'not applicable' and len(reqID) == 0:
                        reqID = GenericNumericalRequirement.objects.get(id=confClass.requirement.id).options.all()[0].docid
                        
                    self.addCIMReference(experiment, reqElement, argName=reqID, argType='NumericalRequirement')
                    # for each modelmod modification
                    for modClassBase in confClass.mod.all() :
                        modClass=modClassBase.get_child_object()
                        assert modClass._child_name=='codemod','Found a class type other than codemod'
                        sourceElement=ET.SubElement(confElement,'source')
                        if modClass._child_name=='codemod' :
                            # add a reference with the associated modification
                            self.addCIMReference(modClass.component,sourceElement,mod=modClass)
                        #    #elif im:
                        #    #    assert False, 'for some reason, modclass is never an input mod so I should not be called.'
                        #else:
                        #    assert False, 'modelmod must be an inputmod or a modelmod'  # error

                    # for each modelmod modification
                    # for some reason this is where we get the external couplings
                    for couplingClass in confClass.coupling.all():
                        sourceElement=ET.SubElement(confElement,'source')
                        assert couplingClass.targetInput, 'Error, couplingclass should have a targetinput'
                        self.addCIMReference(couplingClass.targetInput.owner,sourceElement,argName=couplingClass.targetInput.abbrev,argType="componentProperty")

                    #ET.SubElement(confElement,'description').text='Conformance type: "'+confClass.ctype.name+'". Notes: "'+confClass.description+'".'

                elif (confClass.description and confClass.description!='') or len(confClass.mod.all())>0 or len(confClass.coupling.all())>0 :
                    # confClass.ctype is mot mandatory in the CIM but is required for a conformance so output something purely for validation purposes if other fields have been set without confClass.ctype being set
                    ET.SubElement(conf1Element,"conformance",{'type':'invalid'})
            ''' deployment [0..1] '''
            dep2Element=ET.SubElement(simElement,'deployment')
            ET.SubElement(dep2Element,'description').text='The resources(deployment) on which this simulation ran'
            platElement=ET.SubElement(dep2Element,'platform')
            self.addCIMReference(simClass.platform,platElement)
            ''' dateRange [1]'''
            self.addDateRange(simClass.duration,simElement)
            ''' model [1] '''
            modelElement=ET.SubElement(simElement,'model')
            refElement=self.addCIMReference(simClass.numericalModel,modelElement)
            # now add in all mods associated with the simulation
            # to the model reference
            for modelMod in simClass.codeMod.all() :
                self.addModelMod(modelMod,refElement)
            # input mods are not relevant here as they are included directly in the model description as composition information
            ''' documentAuthor, documentCreationDate, documentID, documentVersion, externalID, metadataID and metadataVersion '''
            externalIDs=[]
            
            #drsOutput was introduced post simulations already existing, so in the short term we need to add drs info in those 
            # cases where the simulation already exists. Usually this info will be generated upon creation of a simulation.
            #if len(simClass.drsOutput.all())==0:
                #d=DRSOutput(institute=self.centre,model=self.numericalModel,member=self.drsMember,experiment=self.experiment)
                #d.save()
                #self.drsOutput.add(d)
            
            assert len(simClass.drsOutput.all())==1,"One and only one DRS string expected"
            for drsOutput in simClass.drsOutput.all():
                assert drsOutput, "Expecting a value for the DRS string"
                externalIDs.append((str(drsOutput),'QN_DRS',
                   '''
                      The QN_DRS value allows mapping from data files to metadata 
                      being exported from the metadata questionnaire, and contains 
                      the institution name, the model name on which the simulation 
                      was run, the experiment name to which the simulation 
                      conforms, the simulation level base rip value, and finally 
                      the given start year for the simulation. The format of the string will thus be: 
                      institute_model_experiment_rip_startyear. Also note, that in particular cases, 
                      i.e. decadal and noVolc exps, the start date and expdate 
                      may differ - this will occur in those cases where the simulation 
                      start date is 1st january but still refers to an experiment 
                      for the year before. - (see cmip5 experiment design document) 
                      ''', True))
            # add detail about the identifying 'rip' value used for this 
            # simulation. Used in tandem with the QN_DRS value as an identifer 
            externalIDs.append((simClass.drsMember,'DRS_CMIP5_ensembleType','',True))
            self.addDocumentInfo(simClass,simElement,externalIDs=externalIDs)
            ''' documentGenealogy [0..inf] '''
            #relatedSimulations=simClass.relatedSimulations.all()
            relatedSimulations=SimRelationship.objects.filter(sfrom=simClass)
            assert len(relatedSimulations)==1, "Expecting related simulations to be of size 1"
            relatedSimulation=relatedSimulations[0]
            if relatedSimulation.value :
                if str(relatedSimulation.value)=='usesSpinup':
                    #already captured the relationship as a spinup reference
                    pass
                elif str(relatedSimulation.value)=='hasControlSimulation':
                    #already captured the relationship as a control reference
                    pass
                else:
                    #capture relationship using the genealogy class
                    docGenElement=ET.SubElement(simElement,'documentGenealogy')
                    relationshipElement=ET.SubElement(docGenElement,'relationship')
                    # toTarget means that this relationship is about how I
                    # relate to the target
                    simRelationshipElement=ET.SubElement(relationshipElement,'simulationRelationship',{'type':str(relatedSimulation.value),'direction':'toTarget'})
                    ET.SubElement(simRelationshipElement,"description").text=relatedSimulation.description
                    targetElement=ET.SubElement(simRelationshipElement,"target")
                    self.addCIMReference(relatedSimulation.sto,targetElement)
            ''' quality [0..inf] '''
            return rootElement

    def addDateRange(self,dateObject,rootElement,topName='dateRange'):
        if dateObject:
            dateElement=ET.SubElement(rootElement,topName)
            startDate=dateObject.startDate
            endDate=dateObject.endDate
            period=""
            units=""
            if dateObject.length:
                period=dateObject.length.period
                units=dateObject.length.units
            if startDate and endDate or startDate and period:
                # closed date range
                drElement=ET.SubElement(dateElement,'closedDateRange')
            else:
                # open date range
                drElement=ET.SubElement(dateElement,'openDateRange')
            if period:
                # we are using the standard schema duration type in the CIM here,
                # see http://www.w3schools.com/Schema/schema_dtypes_date.asp for
                # more details
                mappingUnits={'Years':'Y','Days':'D','years':'Y'}
                length='P'+str(int(period))+mappingUnits[units]
                ET.SubElement(drElement,'duration').text=length
            if endDate!=None:
                ET.SubElement(drElement,'endDate').text=str(endDate)
            if startDate!=None:
                ET.SubElement(drElement,'startDate').text=str(startDate)

    def addRequirement(self,reqClass,rootElement):
        if reqClass :
            reqElement=ET.SubElement(rootElement,'numericalRequirement')
            assert reqClass.ctype,"Error, requirement must have ctype set"
            mapping={'BoundaryCondition':'boundaryCondition','InitialCondition':'initialCondition','SpatioTemporalConstraint':'spatioTemporalConstraint'}
            typeElement=ET.SubElement(reqElement,mapping[reqClass.ctype.name])
            ''' numericalRequirement [0..inf] '''
            ''' description [0,1] '''
            if reqClass.description:
                ET.SubElement(typeElement,'description').text=reqClass.description
            ''' id [0..1] '''
            if reqClass.docid:
                ET.SubElement(typeElement,"id").text=reqClass.docid
            ''' name [1] '''
            ET.SubElement(typeElement,'name').text=reqClass.name
            if reqClass.ctype.name=='SpatioTemporalConstraint':
                stcObject=reqClass.get_child_object()
                #rdElement=ET.SubElement(typeElement,'requiredDuration')
                if stcObject.requiredDuration:
                    self.addDateRange(stcObject.requiredDuration,typeElement,topName='requiredDuration')
                    #startDate=stcObject.requiredDuration.startDate
                    #endDate=stcObject.requiredDuration.endDate
                    #period=""
                    #units=""
                    #if stcObject.requiredDuration.length:
                    #    period=stcObject.requiredDuration.length.period
                    #    units=stcObject.requiredDuration.length.units
                    #if startDate and endDate or startDate and period:
                    #    # closed date range
                    #    drElement=ET.SubElement(rdElement,'closedDateRange')
                    #else:
                    #    # open date range
                    #    drElement=ET.SubElement(rdElement,'openDateRange')
                    #if period:
                    #    # we are using the standard schema duration type in the CIM here#,
                    #    # see http://www.w3schools.com/Schema/schema_dtypes_date.asp for
                    #    # more details
                    #    mappingUnits={'Years':'Y','Days':'D','years':'Y'}
                    #    length='P'+str(int(period))+mappingUnits[units]
                    #    ET.SubElement(drElement,'duration').text=length
                    #if endDate!=None:
                    #    ET.SubElement(drElement,'endDate').text=str(endDate)
                    #if startDate!=None:
                    #    ET.SubElement(drElement,'startDate').text=str(startDate)

    def add_experiment(self,expClass,rootElement, startyear=None):
        expElement=expClass.toXML(startyear=startyear)
        self.addDocumentInfo(expClass,expElement)
        # experiment documentGenealogy goes here
        expName,sep,expShortName=expClass.abbrev.partition(' ')
        assert sep!="", "Error, experiment short name does not conform to format 'id name'"
        assert expName and expName!='', "Error, expecting an experiment name"
        expRoot,sep,expID=expName.partition('-')
        # if something ...
        if expID :
            relationshipMap={'E':'increaseEnsembleOf','I':'modifiedInputMethodOf','S':'shorterVersionOf','L':'extensionOf'}
            assert expRoot, "We should have an experiment root if we have extracted an experiment id"
            assert expID in relationshipMap.keys(), 'Error, unknown experiment keyword. Expecting '+expID.keys()+' but found '+expID
            docGenElement=ET.SubElement(expElement,'documentGenealogy')
            relationshipElement=ET.SubElement(docGenElement,'relationship')
            # toTarget means that this relationship is about how I relate to the target
            expRelationshipElement=ET.SubElement(relationshipElement,'experimentRelationship',{'type':relationshipMap[expID],'direction':'toTarget'})
            relatedExperimentName=expRoot+' '+expShortName
            ET.SubElement(expRelationshipElement,"description").text="My experimentID '"+expName+"' indicates that I am a modification of the Experiment with experimentID '"+expRoot+"' (and the same shortName '"+expShortName+"') with the relationship '"+relationshipMap[expID]+"'"
            targetElement=ET.SubElement(expRelationshipElement,"target")
            # create the name of the experiment we are related to
            relatedExperiments=Experiment.objects.filter(abbrev=relatedExperimentName)
            assert len(relatedExperiments)==1, "Expecting to find one experiment"
            relatedExperiment=relatedExperiments[0]
            self.addCIMReference(relatedExperiment,targetElement,argName=expShortName,argType="experiment")

        rootElement.append(expElement)

    def setComponentOptions(self,recurse,composition):

        self.recurse=recurse
        self.outputComposition=composition
    
    def add_component(self,compClass,rootElement):

        assert compClass, "add_component compClass is false"
        if compClass :
            self.addChildComponent(compClass,rootElement,1,self.recurse)
        return rootElement

    def add_platform(self,platClass,rootElement):

        if platClass :
            platformElement=ET.SubElement(rootElement,'platform')
            if platClass.compiler :
                shortName=platClass.abbrev+"_"+platClass.compiler.name
                longName="Machine "+platClass.abbrev+" and compiler "+platClass.compiler.name
            else :
                shortName=platClass.abbrev+"CompilerUnspecified"
                longName="Machine "+platClass.abbrev+" and an unspecified compiler"
            ''' shortname [1] '''
            ET.SubElement(platformElement,'shortName').text=shortName
            ''' longName [0..1] '''
            ET.SubElement(platformElement,'longName').text=longName
            ''' description [0..1] '''
            if platClass.description :
                ET.SubElement(platformElement,'description').text=platClass.description
            ''' contact [0..inf] '''
            self.addResp(platClass.contact,platformElement,'contact','contact')
            ''' unit [1..inf] '''
            unitElement=ET.SubElement(platformElement,'unit')
            ''' unit/machine [1] '''
            machineElement=ET.SubElement(unitElement,'machine')
            ''' unit/machine/machineName [1] '''
            ET.SubElement(machineElement,'machineName').text=platClass.abbrev
            ''' unit/machine/machineSystem [0..1] '''
            if platClass.hardware:
                ET.SubElement(machineElement,'machineSystem').text=platClass.hardware.name
            ''' unit/machine/machineLibrary [0..inf] '''
            ''' unit/machine/machineDescription [0..1] '''
            ''' unit/machine/machineLocation [0..1] '''
            ''' unit/machine/machineOperatingSystem [0..1] '''
            if platClass.operatingSystem :
                self.addCVValue(machineElement,'machineOperatingSystem',platClass.operatingSystem.name)
            ''' unit/machine/machineVendor [0..1] '''
            if platClass.vendor :
                self.addCVValue(machineElement,'machineVendor',platClass.vendor.name)
            ''' unit/machine/machineInterconnect [0..1] '''
            if platClass.interconnect :
                self.addCVValue(machineElement,'machineInterconnect',platClass.interconnect.name)
            ''' unit/machine/machineMaximumProcessors [0..1] '''
            if platClass.maxProcessors :
                ET.SubElement(machineElement,'machineMaximumProcessors').text=str(platClass.maxProcessors)
            ''' unit/machine/machineCoresPerProcessor [0..1] '''
            if platClass.coresPerProcessor :
                ET.SubElement(machineElement,'machineCoresPerProcessor').text=str(platClass.coresPerProcessor)
            ''' unit/machine/machineProcessorType [0..1] '''
            if platClass.processor :
                self.addCVValue(machineElement,'machineProcessorType',platClass.processor.name)
            ''' unit/compiler [0..inf] '''
            compilerElement=ET.SubElement(unitElement,'compiler')
            ''' unit/compiler/compilerName [1] '''
            if platClass.compiler :
                ET.SubElement(compilerElement,'compilerName').text=platClass.compiler.name
            else :
                ET.SubElement(compilerElement,'compilerName').text='unspecified'
            ''' unit/compiler/compilerVersion [1] '''
            if platClass.compilerVersion :
                ET.SubElement(compilerElement,'compilerVersion').text=platClass.compilerVersion
            else :
               ET.SubElement(compilerElement,'compilerVersion').text='unspecified' 
            ''' unit/compiler/compilerLanguage [0..1] '''
            ''' unit/compilerType [0..1] '''
            ''' unit/compiler/compilerOptions [0..1] '''
            ''' unit/compiler/compilerEnvironmentVariables [0..1] '''
            ''' documentAuthor, documentCreationDate, documentID, documentVersion, externalID, metadataID and metadataVersion '''
            self.addDocumentInfo(platClass,platformElement)
            ''' documentGenealogy [0..inf] '''
            ''' quality [0..inf] '''
        return rootElement

    def addCVValue(self,root,elementName,value,controlled=True,isOpen=True,cvName='',description='',cvURL='http://proj.badc.rl.ac.uk/svn/metafor/cmip5q/trunk',standard=False) :
        # "controlled" means that the value is a new value in a controlled vocab
        # "standard" means this is a standard rather than a CV.
        if isOpen: open='true'
        else : open='false'
        # open must be true for some reason
        open='true'
        if cvName=='' : cvName=elementName
        if controlled :
            type=ET.SubElement(root,elementName,{'value':value,'open':open})
        else :
            type=ET.SubElement(root,elementName,{'value':'Other','open':open})
        if not standard :
            sub=ET.SubElement(type,'controlledVocabulary')
        else:
            sub=ET.SubElement(type,'standard')
        ET.SubElement(sub,'name').text=cvName
        if not standard and cvURL :
            ET.SubElement(sub,'server').text=cvURL
        if description:
            ET.SubElement(sub,'description').text=description
        if not controlled :
          type.text=value

    def addDocumentInfo1(self,rootClass,rootElement) :
        ''' documentAuthor [0..1] '''
        authorElement=ET.SubElement(rootElement,'documentAuthor')
        self.addSimpleResp('Metafor Questionnaire',authorElement,'documentAuthor')
        ''' documentCreationDate [1] '''
        ET.SubElement(rootElement,'documentCreationDate').text=datetime.datetime.isoformat(datetime.datetime.today())
        
    def addDocumentInfo2(self,rootClass,rootElement) :
        try :
            ''' documentID [1] '''
            ET.SubElement(rootElement,'documentID').text=rootClass.uri
            ''' documentVersion [1] '''
            ET.SubElement(rootElement,'documentVersion').text=str(rootClass.documentVersion)
            ''' externalID [0..inf]'''
            ''' metadataID [0..1]'''
            ''' metadataVersion [0..1] '''
        except :
            assert False, "Document is not of type Doc"

    def addDocumentInfo(self,rootClass,rootElement,externalIDs=[]) :
        try :
            ''' documentID [1] '''
            ET.SubElement(rootElement,'documentID').text=rootClass.uri
            ''' documentVersion [1] '''
            ET.SubElement(rootElement,'documentVersion').text=str(rootClass.documentVersion)
        except :
            #try :
            #    if (rootClass.doc) :
            #        ''' documentID [1] '''
            #        ET.SubElement(rootElement,'documentID').text=rootClass.doc.uri
            #        ''' documentVersion [1] '''
            #        ET.SubElement(rootElement,'documentVersion').text=str(rootClass.doc.documentVer#sion)
            #    else :
            #        ET.SubElement(rootElement,'documentID').text='[TBD]'
            #        ET.SubElement(rootElement,'documentVersion').text='[TBD]'
            #except :

            assert False, "Document is not of type Doc"
            #ET.SubElement(rootElement,'documentID').text='[TBD]'
            #ET.SubElement(rootElement,'documentVersion').text='[TBD]'

        ''' metadataID [0..1] '''
        ''' metadataVersion [0..1] '''
        ''' externalID [0..inf] '''
        for externalID in externalIDs :
            self.addCVValue(rootElement,'externalID',externalID[0],cvName=externalID[1],description=externalID[2],standard=externalID[3])
        ''' documentAuthor [0..1] '''
        authorElement=ET.SubElement(rootElement,'documentAuthor')
        self.addSimpleResp('Metafor Questionnaire',authorElement,'documentAuthor')
        ''' documentCreationDate [1] '''
        ET.SubElement(rootElement,'documentCreationDate').text=datetime.datetime.isoformat(datetime.datetime.today())
        


    def constraintValid(self,con,constraintSet,root) :
        if con.constraint=='' : # there is no constraint
            return True
        else : # need to check the constraint
            # constraint format is : if <ParamName> [is|has] [not]* "<Value>"[ or "<Value>"]*
            #ET.SubElement(root,"DEBUG_Constraint").text=str(con.constraint)
            parsed=con.constraint.split()
            assert(parsed[0]=='if','Error in constraint format')
            assert(parsed[2]=='is' or parsed[2]=='has','Error in constraint format')
            paramName=parsed[1]
            #ET.SubElement(root,"DEBUG_Constraint_parameter").text=paramName
            if parsed[2]=='is' :
                singleValueExpected=True
            else:
                singleValueExpected=False
            #ET.SubElement(root,"DEBUG_Constraint_single_valued_parameter").text=str(singleValueExpected)
            if parsed[3]=='not' :
                negation=True
                idx=4
            else :
                negation=False
                idx=3
            #ET.SubElement(root,"DEBUG_Constraint_negation").text=str(negation)
            nValues=0
            valueArray=[]
            parsedQuote=con.constraint.split('"')
            #ET.SubElement(root,"DEBUG_Constraint_String_NSplit").text=str(len(parsedQuote))
            #for name in parsedQuote :
            #    ET.SubElement(root,"DEBUG_Constraint_String_Split").text=name
            idx2=2 # ignore the first load of text
            while idx2<len(parsedQuote) :
                #ET.SubElement(root,"DEBUG_Adding").text=parsedQuote[idx2-1]
                valueArray.append(parsedQuote[idx2-1])
                nValues+=1
                if (idx2+1)<len(parsedQuote) :
                    assert(parsed[idx2+1]=='or','Error in constraint format')
                idx2+=2
            assert(nValues>0)
            #ET.SubElement(root,"DEBUG_Constraint_nvalues").text=str(nValues)
            #for value in valueArray :
            #    ET.SubElement(root,"DEBUG_Constraint_value").text=value
            # now check if the constraint is valid or not
            # first find the value(s) of the parameter that is referenced
            found=False
            refValue=''
            for con in constraintSet:
                if not(found):
                    # see if it is a Xor
                    pset=XorParam.objects.filter(constraint=con)
                    for p in pset:
                        if (p.name==paramName) :
                            found=True
                            if p.value:
                                refValue=p.value.name
                    if not found:
                        # see if it is an or
                        pset=OrParam.objects.filter(constraint=con)
                        for p in pset:
                            if (p.name==paramName) :
                                found=True
                                if p.value:
                                    valset=p.value.all()
                                    counter=0
                                    for value in valset :
                                        counter+=1
                                        refValue+=value.name
                                        if counter != len(valset) :
                                            refValue+=", "
                    if not found:
                        # see if it is a keyboard value
                        pset=KeyBoardParam.objects.filter(constraint=con)
                        for p in pset:
                            if (p.name==paramName) :
                                found=True
                                refValue=p.value
            assert found,'Error, can not find property that is referenced by constraint'
            #ET.SubElement(root,"DEBUG_Constraint_refvalues").text=refValue
            if refValue=='' : # the reference parameter does not have any values set
                return True # output constraint parameters if the reference parameter is not set. This is an arbitrary decision, I could have chosen not to.
            match=False
            for value in refValue.split(','):
                if not(match) :
                    stripSpaceValue=value.strip()
                    if stripSpaceValue != '' :
                        if stripSpaceValue in valueArray :
                            match=True
            #ET.SubElement(root,"DEBUG_Constraint_match").text=str(match)
            if negation :
                match=not(match)
            return match

    def addProperties(self,componentObject,rootElement):

        if componentObject.implemented :
            componentProperty=None
            if componentObject.isParamGroup :
                # I am a parameter dressed as a component
                newRootElement=ET.SubElement(rootElement,'componentProperty',{'represented':'true'})
                '''shortName [1]'''
                if componentObject.abbrev:
                    ET.SubElement(newRootElement,'shortName').text=componentObject.abbrev
                '''longName [0..1]'''
                if componentObject.title:
                    ET.SubElement(newRootElement,'longName').text=componentObject.title
                '''description [0..1]'''
                if componentObject.description :
                    ET.SubElement(newRootElement,'description').text=componentObject.description
            else :
                newRootElement=rootElement

            # add in any properties dressed as child components
            for childComponentObject in componentObject.components.all():
                if childComponentObject.isParamGroup and childComponentObject.implemented:
                    self.addProperties(childComponentObject,newRootElement)

            # add in properties associated with this component
            for pg in componentObject.paramGroup.all():
              if pg.name != u"Model development path" and pg.name != u"Tuning Section" and pg.name != u"Conservation of integral quantities": # Not exporting 'new questions' to cim - these will pnly be used in explorer tables:
                  componentProperty={}
                  if pg.name=="General Attributes" or pg.name=="Attributes": # skip general attributes as this is just a container for grouping properties in the Questionnaire. The Attributes test is due to "top level" components using this for some reason. I've created a ticket (716) for this.
                    componentProperty=newRootElement
                  else:
                    componentProperty=ET.SubElement(newRootElement,'componentProperty',{'represented':'true'})
                    '''shortName [1]'''
                    if pg.name:
                        ET.SubElement(componentProperty,'shortName').text=pg.name
                    '''longName [0..1]'''
                    if pg.name:
                        ET.SubElement(componentProperty,'longName').text=pg.name
    
                  # the internal questionnaire representation is that all parameters
                  # are contained in a constraint group
                  constraintSet=ConstraintGroup.objects.filter(parentGroup=pg)
                  for con in constraintSet:
                    if con.constraint!='' :
                        componentProperty.append(ET.Comment('Constraint start: '+con.constraint))
                    if not(self.constraintValid(con,constraintSet,componentProperty)) :
                        componentProperty.append(ET.Comment('Constraint is invalid'))
                    else :
                        #
                        # RF: one can now get at a child object (get_child)
                        # so we could simplify the code below, but as it works ...
                        #
                        # Needed to add .order_by('id') as the database does not guarantee
                        # to return objects in the same order, hence the order of the baseclass
                        # objects might not be the same as the Xor, Or, or KeyBoard objects
                        # whereas the code assumes the same order.
                        #
                        BaseParamSet=BaseParam.objects.filter(constraint=con).order_by('id')
                        XorParamSet=XorParam.objects.filter(constraint=con).order_by('id')
                        OrParamSet=OrParam.objects.filter(constraint=con).order_by('id')
                        KeyBoardParamSet=KeyBoardParam.objects.filter(constraint=con).order_by('id')
                        XorIDX=0
                        OrIDX=0
                        KeyBoardIDX=0
                        for bp in BaseParamSet:
                            found=False
                            if not(found) and XorIDX<XorParamSet.count() :
                                if bp.name == XorParamSet[XorIDX].name :
                                    found=True
                                    p=XorParamSet[XorIDX]
                                    XorIDX+=1
                                    ptype="XOR"
                            if not(found) and OrIDX<OrParamSet.count() :
                                if bp.name == OrParamSet[OrIDX].name :
                                    found=True
                                    p=OrParamSet[OrIDX]
                                    OrIDX+=1
                                    ptype="OR"
                            if not(found) and KeyBoardIDX<KeyBoardParamSet.count() :
                                if bp.name == KeyBoardParamSet[KeyBoardIDX].name :
                                    found=True
                                    p=KeyBoardParamSet[KeyBoardIDX]
                                    KeyBoardIDX+=1
                                    ptype="KeyBoard"
                            assert found, "Found must be true at this point"
    
                            # skip CV output if the value is "n/a" for XOR or OR and if (for OR) there is only one value chosen. The validation step will flag the existence of N/A with other values
                            if (ptype=='XOR' and p.value and p.value.name=='N/A') :
                                componentProperty.append(ET.Comment('Value of XOR property called '+p.name+' is N/A so skipping'))
                            elif (ptype=='OR' and p.value and len(p.value.all())==1 and ('N/A' in str(p.value.all()))) : # last clause is messy as we turn the value into a string in a nasty way but I don't know how to do it another way
                                componentProperty.append(ET.Comment('Value of OR property called '+p.name+' is N/A so skipping'))
                            else :
                                property=ET.SubElement(componentProperty,'componentProperty',{'represented': 'true'})
                                '''shortName [1]'''
                                if p.name:
                                    ET.SubElement(property,'shortName').text=p.name
                                '''longName [0..1]'''
                                if p.name:
                                    ET.SubElement(property,'longName').text=p.name
                                '''value'''
                                if ptype=='KeyBoard':
                                    #removing illegal xml characters 
                                    legalstr = re.sub(RE_XML_ILLEGAL, "", unicode(p.value))
                                    ET.SubElement(property,'value').text=legalstr
                                elif ptype=='XOR':
                                    value=''
                                    if p.value:
                                        value=p.value.name
                                    ET.SubElement(property,'value').text=value
                                elif ptype=='OR':
                                    if p.value :
                                        valset=p.value.all()
                                        for value in valset :
                                            ET.SubElement(property,'value').text=value.name
                    if con.constraint!='' :
                        componentProperty.append(ET.Comment('Constraint end: '+con.constraint))
    
                  if componentProperty:
                      if componentProperty.tag=="componentProperty" :
                          # I should not be a leaf property
                          if not componentProperty.find("componentProperty"):
                              # All children must have been declared as N/A so remove me
                              parent=componentProperty.getparent()
                              parent.remove(componentProperty)
                              parent.append(ET.Comment('Property '+pg.name+' removed as it has no children'))

    def addChildComponent(self,c,root,nest,recurse=True):

      if c.implemented or nest==1:
        comp=ET.SubElement(root,'modelComponent')
        '''shortName [1]'''
        ET.SubElement(comp,'shortName').text=c.abbrev
        '''longName [0..1]'''
        ET.SubElement(comp,'longName').text=c.title
        '''description [0..1]'''
        if c.description:
            ET.SubElement(comp,'description').text=c.description
        '''license [0..1]'''
        '''componentProperties [0..1]'''
        componentProperties=ET.SubElement(comp,'componentProperties')
        self.addProperties(c,componentProperties)
        # Add any coupling inputs that have been defined for this component
        Inputs=ComponentInput.objects.filter(owner=c)
        for CompInpClass in Inputs :
            cp=ET.SubElement(componentProperties,'componentProperty',{'represented':'true'})
            '''shortName'''
            ET.SubElement(cp,'shortName').text=CompInpClass.abbrev
            '''longName'''
            ET.SubElement(cp,'longName').text=CompInpClass.abbrev
            '''description'''
            if CompInpClass.description :
                ET.SubElement(cp,'description').text=CompInpClass.description
            '''units'''
            if CompInpClass.units :
                self.addCVValue(cp,'units',CompInpClass.units,cvName='units')
                #ET.SubElement(cp,'units',{'value' : CompInpClass.units})
            '''standardName'''
            if CompInpClass.cfname :
                self.addCVValue(cp,'standardName',CompInpClass.cfname.name,cvName='cfName')
        # Check whether we actually have any component properties.
        # If not, then remove this element as it is optional in the CIM
        # and if it exists it expects at least one property within it.
        if len(componentProperties)==0:
            comp.remove(componentProperties)
        '''scientificProperties [0..1]'''
        '''numericalProperties [0..1]'''
        '''responsibleParty [0..inf]'''
        self.addResp(c.author,comp,'PI')
        self.addResp(c.funder,comp,'funder')
        self.addResp(c.contact,comp,'contact')
        self.addResp(c.centre.party,comp,'centre')
        '''releaseDate [0..1] type:dateTime'''
        if c.yearReleased :
            ET.SubElement(comp,'releaseDate').text=str(c.yearReleased)
        '''previousVersion [0..1]'''
        '''fundingSource [0..inf]'''
        '''citation [0..inf]'''
        self.addReferences(c.references,comp)
        '''onlineResource [0..1]'''
        '''componentLanguage [0..1]'''
        '''grid [0..1]'''
        '''composition [0..1]'''
        self.addComposition(c,comp)
        if recurse:
            '''childComponent [0..inf]'''
            for child in c.components.all():
                if child.isParamGroup:
                    # skip as I am a parameter dressed as a component
                    pass
                elif child.implemented:
                    comp2=ET.SubElement(comp,'childComponent')
                    self.addChildComponent(child,comp2,nest+1)
                else : # child is not implemented
                    comp.append(ET.Comment('Component '+child.abbrev+' has implemented set to false'))
        '''parentComponent [0..1]'''
        '''dependencies [0..1]'''
        '''deployment [0..inf]'''
        '''type [1..inf]'''
        # always output the metafor sciencetype
        self.addCVValue(comp,'type',c.scienceType,controlled=c.controlled,cvName='metafor')
        # if it is a realm type then output the relevant drs realm type as well
        mapping={'Atmosphere':'atmos','Ocean':'ocean','LandSurface':'land','LandIce':'landIce','SeaIce':'seaIce','OceanBiogeoChemistry':'ocnBgchem','AtmosphericChemistry':'atmosChem','Aerosols':'aerosol'}
        if c.scienceType in mapping :
            self.addCVValue(comp,'type',mapping[c.scienceType],cvName='DRS_CMIP5_componentType',isOpen=False)
        '''timing [0..1]'''
        '''activity [0..1]'''
        ''' documentAuthor, documentCreationDate, documentID, documentVersion, externalID, metadataID and metadataVersion '''
        self.addDocumentInfo(c,comp)
        '''documentGenealogy [0..1] '''
        if c.otherVersion or c.geneology :
            GenEl=ET.SubElement(comp,'documentGenealogy')
            RelEl=ET.SubElement(GenEl,'relationship')
            DocEl=ET.SubElement(RelEl,'documentRelationship',{'type' : 'previousVersionOf', 'direction' : 'toTarget'})
            if c.geneology :
                ET.SubElement(DocEl,'description').text=c.geneology
            TargEl=ET.SubElement(DocEl,'target')
            RefEl=ET.SubElement(TargEl,'reference')
            if c.otherVersion :
                ET.SubElement(RefEl,'name').text=c.otherVersion
        '''quality [0..inf] '''
      else:
          root.append(ET.Comment('Component '+c.abbrev+' has implemented set to false'))
      return

    def addReferences(self,references,rootElement,parentName='citation'):
        for ref in references.all():
            self.addReference(ref,rootElement,parentName)

    def addReference(self,refInstance,rootElement,parentName='citation'):
        if refInstance :
                refElement=ET.SubElement(rootElement,parentName)
                #we no longer output CI_Citation
                #citeElement=ET.SubElement(refElement,self.GMD_NAMESPACE_BRACKETS+'CI_Citation')
                citeElement=refElement
                titleElement=ET.SubElement(citeElement,self.GMD_NAMESPACE_BRACKETS+'title')
                ET.SubElement(titleElement,self.GCO_NAMESPACE_BRACKETS+'CharacterString').text=refInstance.name
                # CIM expects a date element even if it is empty
                ET.SubElement(citeElement,self.GMD_NAMESPACE_BRACKETS+'date')
                presElement=ET.SubElement(citeElement,self.GMD_NAMESPACE_BRACKETS+'presentationForm')
                ET.SubElement(presElement,self.GMD_NAMESPACE_BRACKETS+'CI_PresentationFormCode',{'codeList':'','codeListValue':str(refInstance.refType)})
                ociteElement=ET.SubElement(citeElement,self.GMD_NAMESPACE_BRACKETS+'otherCitationDetails')
                ET.SubElement(ociteElement,self.GCO_NAMESPACE_BRACKETS+'CharacterString').text=refInstance.link
                ctElement=ET.SubElement(citeElement,self.GMD_NAMESPACE_BRACKETS+'collectiveTitle')
                #removing illegal xml characters 
                legalstr = re.sub(RE_XML_ILLEGAL, "", unicode(refInstance.citation))
                ET.SubElement(ctElement,self.GCO_NAMESPACE_BRACKETS+'CharacterString').text = legalstr


    def addSimpleResp(self,respName,rootElement,respType) :
        #we no longer have a CI_ResponsibleParty element
        #ciresp=ET.SubElement(rootElement,self.GMD_NAMESPACE_BRACKETS+'CI_ResponsibleParty')
        ciresp=rootElement
        name=ET.SubElement(ciresp,self.GMD_NAMESPACE_BRACKETS+'individualName')
        ET.SubElement(name,self.GCO_NAMESPACE_BRACKETS+'CharacterString').text=respName
        role=ET.SubElement(ciresp,self.GMD_NAMESPACE_BRACKETS+'role')
        ET.SubElement(role,self.GMD_NAMESPACE_BRACKETS+'CI_RoleCode',{'codeList':'', 'codeListValue':respType})


    def addResp(self,respClass,rootElement,respType,parentElement='responsibleParty'):
        if (respClass) :
                if respClass.name == 'Unknown' : # skip the default respobject
                    rootElement.append(ET.Comment('responsibleParty '+respType+ ' is set to unknown. No CIM output will be generated.'))
                    return
                respElement=ET.SubElement(rootElement,parentElement)
                respElement.append(ET.Comment('responsibleParty uri :: '+respClass.uri))
                #we no longer have a CI_ResponsibleParty element
                #ciresp=ET.SubElement(respElement,self.GMD_NAMESPACE_BRACKETS+'CI_ResponsibleParty')
                ciresp=respElement
        #http://www.isotc211.org/2005/gmd
        #CI_ResponsibleParty referenced in citation.xsd
        # <gmd:individualName>
        #name=ET.SubElement(resp,'gmd:individualName')
        #ET.SubElement(name,'gco:CharacterString').text=c.contact
                if respClass.isOrganisation :
                    name=ET.SubElement(ciresp,self.GMD_NAMESPACE_BRACKETS+'organisationName')
                else :
                    name=ET.SubElement(ciresp,self.GMD_NAMESPACE_BRACKETS+'individualName')
                ET.SubElement(name,self.GCO_NAMESPACE_BRACKETS+'CharacterString').text=respClass.name
        #</gmd:individualName/>
        # <gmd:organisationName/>
        # <gmd:positionName/>
        # <gmd:contactInfo>
        #contact=ET.SubElement(ciresp,'gmd:contactInfo')
                contact=ET.SubElement(ciresp,self.GMD_NAMESPACE_BRACKETS+'contactInfo')
                cicontact=ET.SubElement(contact,self.GMD_NAMESPACE_BRACKETS+'CI_Contact')
        #     <gmd:phone/>
        #     <gmd:address>
        #address=ET.SubElement(cicontact,'gmd:address')
                address=ET.SubElement(cicontact,self.GMD_NAMESPACE_BRACKETS+'address')
                ciaddress=ET.SubElement(address,self.GMD_NAMESPACE_BRACKETS+'CI_Address')
        #         <gmd:deliveryPoint/>
                address=ET.SubElement(ciaddress,self.GMD_NAMESPACE_BRACKETS+'deliveryPoint')
                ET.SubElement(address,self.GCO_NAMESPACE_BRACKETS+'CharacterString').text=respClass.address
        #         <gmd:city/>
        #         <gmd:administrativeArea/>
        #         <gmd:postalCode/>
        #         <gmd:country/>
        #         <gmd:electronicMailAddress>
        #email=ET.SubElement(ciaddress,'gmd:electronicMailAddress')
        #ET.SubElement(email,'gco:CharacterString').text=c.email
                email=ET.SubElement(ciaddress,self.GMD_NAMESPACE_BRACKETS+'electronicMailAddress')
                ET.SubElement(email,self.GCO_NAMESPACE_BRACKETS+'CharacterString').text=respClass.email
        #         </gmd:electronicMailAddress>
        #     </gmd:address>
        #     <gmd:onlineResource/>
                resource=ET.SubElement(cicontact,self.GMD_NAMESPACE_BRACKETS+'onlineResource')
                ciresource=ET.SubElement(resource,self.GMD_NAMESPACE_BRACKETS+'CI_OnlineResource')
                linkage=ET.SubElement(ciresource,self.GMD_NAMESPACE_BRACKETS+'linkage')
                url=ET.SubElement(linkage,self.GMD_NAMESPACE_BRACKETS+'URL').text=respClass.webpage
        #     <gmd:hoursOfService/>
        #     <gmd:contactInstructions/>
        # </gmd:contactInfo>
        # <gmd:role/>
                role=ET.SubElement(ciresp,self.GMD_NAMESPACE_BRACKETS+'role')
                ET.SubElement(role,self.GMD_NAMESPACE_BRACKETS+'CI_RoleCode',{'codeList':'', 'codeListValue':respType})
                if respClass.abbrev :
                    ET.SubElement(respElement,'abbreviation').text=respClass.abbrev

    def addComposition(self,c,comp):
        # couplings are all at the esm (root component) level
        couplings=[]
        if c.isModel:
            couplings=c.couplings(simulation=self.simClass)
        # see if I have any couplings. For some reason we can have couplings
        # without internal or external closures so need to check for closures
        coupled=False
        if len(couplings)>0 :
            for coupling in couplings :
                extclosures=ExternalClosure.objects.filter(coupling=coupling)
                if len(extclosures)>0 :
                    coupled=True
                intclosures=InternalClosure.objects.filter(coupling=coupling)
                if len(intclosures)>0 :
                    coupled=True
        if coupled :
            comp.append(ET.Comment('I am coupled'))
            # reset the value manually for the moment
            self.outputComposition=False
            assert not self.outputComposition, "binding information is output with the simulation not the model in CMIP5"
            if self.outputComposition :
                composeElement=ET.SubElement(comp,'composition')
                for coupling in couplings:
                    # output each link separately as the questionnaire keeps information
                    # about transformations on a link by link basis
                    extclosures=ExternalClosure.objects.filter(coupling=coupling)
                    for closure in extclosures :
                        self.addCoupling(coupling,closure,composeElement)
                    intclosures=InternalClosure.objects.filter(coupling=coupling)
                    for closure in intclosures :
                        self.addCoupling(coupling,closure,composeElement)
                ET.SubElement(composeElement,'description').text='Coupling details for component '+c.abbrev
            else :
                comp.append(ET.Comment('Coupling information exists but its output has been switched off for this CIM Object'))

    def addCoupling(self,coupling,closure,composeElement,elementName='coupling') :
        CompInpClass=coupling.targetInput
        assert CompInpClass,'A Coupling instance must have an associated ComponentInput instance'
        assert CompInpClass.owner,'A Coupling instance must have an associated ComponentInput instance with a valid owner'
        assert CompInpClass.ctype,'A Coupling instance must have an associated ctype value'
        couplingType=CompInpClass.ctype.name
        if couplingType=='BoundaryCondition' :
            couplingType='boundaryCondition'
        elif couplingType=='AncillaryFile' :
            couplingType='ancillaryFile'
        elif couplingType=='InitialCondition' :
            couplingType='initialCondition'
        couplingFramework=''
        # fully specified is true if we are referencing data in a file, otherwise it is not fully specified (as we are either referencing a file or a component)
        if closure.ctype=='external' and closure.target :
            couplingElement=ET.SubElement(composeElement,elementName,{'purpose':couplingType,'fullySpecified':'true'})
        else :
            couplingElement=ET.SubElement(composeElement,elementName,{'purpose':couplingType,'fullySpecified':'false'})
        '''description'''
        ET.SubElement(couplingElement,'description').text=coupling.manipulation
        '''type [0..1] '''
        if coupling.inputTechnique and couplingType=='boundaryCondition' :
            if coupling.inputTechnique.name!='' :
                #ET.SubElement(couplingElement,'type',{'value':coupling.inputTechnique.name})
                self.addCVValue(couplingElement,'type',coupling.inputTechnique.name,cvName="CouplingType")
        '''timeProfile'''
        units=''
        if coupling.FreqUnits :
            units=str(coupling.FreqUnits.name)
        if units!='' or coupling.couplingFreq!=None :
            tpElement=ET.SubElement(couplingElement,'timeProfile',{'units':units,'variableRate':'false'})
            #ET.SubElement(tpElement,'start')
            #ET.SubElement(tpElement,'end')
            ET.SubElement(tpElement,'rate').text=str(coupling.couplingFreq)
        '''timeLag'''
        '''spatialRegridding'''
        if closure.spatialRegrid :
            regridValue=closure.spatialRegrid.name
            if not regridValue=='None Used' :
                sr=ET.SubElement(couplingElement,'spatialRegridding')
                ET.SubElement(sr,'spatialRegriddingStandardMethod').text=regridValue.lower()
            # else do nothing as the value is 'None Used'
        '''timeTransformation'''
        if closure.temporalTransform :
            tt=ET.SubElement(couplingElement,'timeTransformation')
            self.addCVValue(tt,'mappingType',closure.temporalTransform.name)
        '''couplingSource'''
        sourceElement=ET.SubElement(couplingElement,'couplingSource')
        sourceElement=ET.SubElement(sourceElement,'dataSource')
        if closure.ctype=='internal' and closure.target :
            # reference to component
            self.addCIMReference(closure.target,sourceElement)
        elif closure.ctype=='external' and closure.target :
            # reference to a field in a file
            # we reference the file here and the field in the "connection"
            self.addCIMReference(closure.targetFile,sourceElement)
        elif closure.ctype=='external' and closure.targetFile :
            # reference directly to a file
            self.addCIMReference(closure.targetFile,sourceElement)
        else :
            sourceElement.append(ET.Comment('error: couplingSource closure has no target and (for ExternalClosures) no targetFile'))

        '''couplingTarget'''          
        targetElement=ET.SubElement(couplingElement,'couplingTarget')
        targetElement=ET.SubElement(targetElement,'dataSource')
        self.addCIMReference(CompInpClass.owner,targetElement)
        '''priming'''
        '''connection'''
        connectionElement=ET.SubElement(couplingElement,'connection')
        if closure.ctype=='external' and closure.target :
            # we are referencing data in a file
            sourceElement=ET.SubElement(connectionElement,'connectionSource')
            sourceElement=ET.SubElement(sourceElement,'dataSource')
            self.addCIMReference(closure.targetFile,sourceElement,argName=closure.target.variable,argType='fileVariable')
        else :
            connectionElement.append(ET.Comment('this coupling has no connection source specified'))
        # we know that we always have a connectionTarget as we create it
        # we know that we never have a connectionSource as there is no such concept in the Questionnaire
        targetElement=ET.SubElement(connectionElement,'connectionTarget')
        targetElement=ET.SubElement(targetElement,'dataSource')
        self.addCIMReference(CompInpClass.owner,targetElement,argName=CompInpClass.abbrev,argType='componentProperty')


    def addCIMReference(self,rootClass,rootElement,argName='',argType='',mod=None, description=''):

        if argName!='' :
            assert argType!='', 'If argName is specified then argType must also be specified'
        if argType!='' :
            assert argName!='', 'If argType is specified then argName must also be specified'
        try :
            myURI=rootClass.uri
            myDocumentVersion=rootClass.documentVersion
            myName=rootClass.abbrev
            myType=rootClass._meta.module_name
            if myType=='datacontainer' :
                 myType='dataObject'
                 # hack as pre-loaded files do not have an abbreviation
                 if myName=='' :
                     myName=rootClass.title
            elif myType=='component' :
                myType='modelComponent'

        except :
            # temporary hack before we make the ensemble class a doc
            assert False, "Document is not of type Doc"
            #myURI="[TBD]"
            #myDocumentVersion="[TBD]"
            #myName="[TBD]"
            #myType="[TBD]"

        targetRef=ET.SubElement(rootElement,'reference',{self.XLINK_NAMESPACE_BRACKETS+'href':'#//CIMRecord/'+myType+'[id=\''+myURI+'\']'})
        ''' id [0..1] '''
        ET.SubElement(targetRef,'id').text=myURI
        ''' name [0..1] '''
        if argName!='' :
            ET.SubElement(targetRef,'name').text=argName
        else :
            ET.SubElement(targetRef,'name').text=myName
        ''' type [0..1] '''
        if argType!='' :
            ET.SubElement(targetRef,'type').text=argType
        else :
            ET.SubElement(targetRef,'type').text=myType
        ''' version [0..1] '''
        ET.SubElement(targetRef,'version').text=str(myDocumentVersion)
        ''' externalID [0..inf] '''
        ''' description [0..1] '''
        if description!='' :
            ET.SubElement(targetRef,'description').text=description
        elif argType!='' and argName!='' :
            ET.SubElement(targetRef,'description').text='Reference to a '+argType+' called '+argName+' in a '+myType+' called '+myName
        else :
            ET.SubElement(targetRef,'description').text='Reference to a '+myType+' called '+myName
        ''' change [0..inf] '''
        if mod :
            modElement=ET.SubElement(targetRef,'change')
            ET.SubElement(modElement,'name').text=mod.mnemonic
            detailElement=ET.SubElement(modElement,'detail',{'type':mod.mtype.name})
            ET.SubElement(detailElement,'description').text=mod.description
        return targetRef

    def add_dataobject(self,fileClass,rootElement):

        if fileClass :
            doElement=ET.SubElement(rootElement,'dataObject',{'dataStatus':'complete'})
            ''' acronym [1]'''
            ET.SubElement(doElement,'acronym').text=fileClass.abbrev
            ''' description [0..1]'''
            if fileClass.description!='' :
                ET.SubElement(doElement,'description').text=fileClass.description
            ''' hierarchyLevelName [0..1]'''
            ''' hierarchyLevelValue [0..1]'''
            ''' keyword [0..1]'''
            ''' geometryModel [0..1]'''
            ''' restriction [0..inf]'''
            ''' storage [0..1]'''
            storeElement=ET.SubElement(doElement,'storage')
            lfElement=ET.SubElement(storeElement,'ipStorage')
            #ET.SubElement(lfElement,'dataSize').text='0'
            if fileClass.format :
                if fileClass.format.name=='Text' :
                    name='ASCII'
                else :
                    name=fileClass.format.name
                self.addCVValue(lfElement,'dataFormat',name,cvName='dataFormatType')
            ''' protocol [0..1] '''
            #ET.SubElement(lfElement,'protocol')
            ''' host [0..1] '''
            #ET.SubElement(lfElement,'host')
            if fileClass.link :
                ET.SubElement(lfElement,'path').text=fileClass.link
            ''' fileName [1]'''
            ET.SubElement(lfElement,'fileName').text=fileClass.title
            ''' distribution [1] '''
            distElement=ET.SubElement(doElement,'distribution')
            if fileClass.format :
                if fileClass.format.name=='Text' :
                    name='ASCII'
                else :
                    name=fileClass.format.name
                self.addCVValue(distElement,'distributionFormat',name,cvName='dataFormatType')
            ''' childObject [0..inf]'''
            ''' parentObject [0..1]'''
            ''' citation [0..inf]'''
            if fileClass.reference:
                citationElement=ET.SubElement(doElement,'citation')
                self.addReference(fileClass.reference,citationElement)
            ''' content [0..inf]'''
            for variable in DataObject.objects.filter(container=fileClass) :
                contentElement=ET.SubElement(doElement,'content')
                ''' topic [1] '''
                topicElement=ET.SubElement(contentElement,'topic')
                '''    name [1] '''
                if variable.variable!='' :
                    ET.SubElement(topicElement,'name').text=variable.variable
                '''    standardName [0..1] '''
                if variable.cfname :
                    self.addCVValue(topicElement,'standardName',variable.cfname.name,cvName='CF')
                '''    description [0..1] '''
                if variable.description :
                    ET.SubElement(topicElement,'description').text=variable.description
                '''    unit [0..1] '''
                ''' aggregation [0..1] '''
                ''' frequency [0..1] '''
                ''' citation [0..inf] '''
                if variable.reference:
                    citationElement=ET.SubElement(contentElement,'citation')
                    self.addReference(variable.reference,citationElement)
            ''' extent [0..1]'''
            ''' generic document elements '''
            self.addDocumentInfo(fileClass,doElement)
            ''' documentGenealogy [0..1] '''
            ''' quality [0..1] '''

'''
Created on 25 Aug 2011

@author: gerarddevine

Module containing generic helpers for the expgenapp application 
(borrows heavily from Translator.py, written by Rupert Ford for the cmip5 
questionnaire app)
'''

import uuid
from lxml import etree as ET
from pimms.apps.exp.models import Experiment, NumericalRequirement


# CIM document attributes: namespaces, schema locations etc..
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
#NSMAP = {None    : CIM_NAMESPACE,             \
#             "xsi"   : SCHEMA_INSTANCE_NAMESPACE, \
#             "gml"   : GML_NAMESPACE,             \
#             "gmd"   : GMD_NAMESPACE,             \
#             "gco"   : GCO_NAMESPACE,             \
#             "xlink" : XLINK_NAMESPACE}


def getCIMXML(expid):
    '''
    Function to create CIM xml document from a experiment instance
    '''
    
    #Pull in experiment to be rendered in CIM xml
    exp = Experiment.objects.get(id=expid)
    
    #Set out the root information of the experiment cim xml document
    root = ET.Element("numericalExperiment")
    root.set("documentVersion","1")
    root.set("control", str(exp.control))
    
    #Append experiment rationale
    rationale = ET.SubElement(root, "rationale")
    rationale.text = exp.rationale
    
    #Append experiment description
    description = ET.SubElement(root, "description")
    description.text = exp.description
    
    #Append experiment shortname
    shortname = ET.SubElement(root, "shortName")
    shortname.text = exp.abbrev
    
    #Append experiment longname
    longname = ET.SubElement(root, "longName")
    longname.text = exp.title
    
    #Append experiment author
    auth = ET.SubElement(root, "author")
    RP = ET.SubElement(auth, GMD_NAMESPACE_BRACKETS+"CI_ResponsibleParty")
    IN = ET.SubElement(RP, GMD_NAMESPACE_BRACKETS+"individualName")
    CS = ET.SubElement(IN, GCO_NAMESPACE_BRACKETS+"CharacterString")
    # TODO - Add the User first name and last name
    CS.text = "To be done"
    
    #Append documentID
    docID = ET.SubElement(root, "documentID")
    docID.set(SCHEMA_INSTANCE_NAMESPACE_BRACKETS+"type", "Identifier")
    docID.text = str(uuid.uuid1())
    
        
    reqs = NumericalRequirement.objects.filter(experiment__id=exp.id)
    
    for req in reqs:
        numreq = ET.SubElement(root, "numericalRequirement")
        numreq.set(SCHEMA_INSTANCE_NAMESPACE_BRACKETS+"type", str(req.reqtype))
        numreq.set(SCHEMA_INSTANCE_NAMESPACE_BRACKETS+"type", str(req.reqtype))
        #numreq.set("{http://www.w3.org/2001/XMLSchema-instance}type", str(req.reqtype))
        
        #Append requirement id
        docid = ET.SubElement(numreq, "id")
        docid.set(SCHEMA_INSTANCE_NAMESPACE_BRACKETS+"type", "Identifier")
        docid.text = req.docid
        
        #Append requirement name
        docname = ET.SubElement(numreq, "name")
        docname.set(SCHEMA_INSTANCE_NAMESPACE_BRACKETS+"type", "Identifier")
        docname.text = req.name
        
        #Append requirement description
        description = ET.SubElement(numreq, "description")
        description.text = req.description
        
        #Append requirement creation date
        description = ET.SubElement(numreq, "creationDate")
        description.text = str(req.created)
    
    tree = ET.ElementTree(element=root)
    return ET.tostring(tree, pretty_print=True)
    
    
    
    
    

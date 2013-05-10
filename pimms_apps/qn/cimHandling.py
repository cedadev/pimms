import os,tempfile
from lxml import etree as ET
from django.conf import settings
#from cimViewer import *
import sys
import StringIO
logging=settings.LOG
import pkg_resources

#http://peak.telecommunity.com/DevCenter/PkgResources#resourcemanager-api
XSLDIR=pkg_resources.resource_filename("pimms","xsl")  # TODO: do we need to worry about cleanup?
XSDDIR=pkg_resources.resource_filename("pimms","xsd")  # TODO: do we need to worry about cleanup?

def shellcommand(command):
    ''' lightweight wrapper to os.system that logs the return and handles errors '''
    logging.debug('Executing '+command)
    r=os.system(command)
    logging.debug(r)
    return r

def viewer(xml):
    ''' Rupert's xslt view, xml is an element tree instance '''
    # we need the xml in a temporary file
    tmpfname=tempfile.mktemp('.xml')
    tmpf=open(tmpfname,'w')
    tmpf.write(ET.tostring(xml))
    tmpf.close()
    # prettify the xml file with an xsl stylesheet
    outfname=tempfile.mktemp('.tmp')
    formatter=os.path.join(XSLDIR,'xmlformat.xsl')
    r=shellcommand('xsltproc %s %s > %s'%(formatter,tmpfname,outfname))
    r=shellcommand("mv %s %s"%(outfname,tmpfname))

    # create and return html rendered xml using an xsl stylesheet
    formatter=os.path.join(XSLDIR,'xmlverbatim.xsl')
    shellcommand('xsltproc %s %s > %s'%(formatter,tmpfname,outfname))

    # read html file
    outf=open(outfname, 'r')
    linestring=outf.read()
    outf.close()
    os.remove(outfname)
    return linestring

class Validator:
    ''' This is used to validate CIM documents '''
    def __init__(self,schemaValidate=False,contentValidate=True):
        ''' Setup validation tools etc '''
        self.XSLdir=XSLDIR
        self.XSDdir=XSDDIR
        self.CIMschema=os.path.join(self.XSDdir,'cim.xsd')
        self.schemaValidate=schemaValidate
        self.contentValidate=contentValidate
        self.nInvalid=0
        self.nChecks=0
        self.valid=True
        self.percentComplete=100.0
        self.cimHtml={}
        self.report={}

    def errorsAsHtml(self) :
        #return self.report
        HTMLresponse = ""

        if self.nInvalid > 0:
            HTMLresponse += "<h3>Status: <font class='red'>INVALID</font></h3>    {0} error{1} from {2} check{3}:<br/>".format(self.nInvalid, \
                         "s" if (self.nInvalid != 1) else "", self.nChecks, \
                         "s" if (self.nChecks != 1) else "" )

            i = 1
            for err in self.errlist:
                displayText = (err.text).replace("::  ::", "::")
                #HTMLresponse += "[{0}] {1}<br/>".format(i, err.text)
                HTMLresponse += "[{0}] {1}<br/>".format(i, displayText.replace("componentProperty   ::","componentProperty ") )
                i += 1

        else:
           HTMLresponse += "<h3>Status: <font class='green'>VALID</font></h3> ({0} error{1} from {2} check{3})<br/>".format(self.nInvalid, \
                         "s" if (self.nInvalid != 1) else "", self.nChecks, \
                         "s" if (self.nChecks != 1) else "" )


        return HTMLresponse
        
    
    def xmlAsHtml(self) :
        return self.cimHtml

    
    def __validationStep(self,CIMdoc,specificSchematronFile=None):
        ''' Common validation steps '''
        
        # perform any common validation
        #report,nChecks,nInvalid=self.__SchematronValidate(CIMdoc,"CommonChecks.sch")
        checks, invalids, errorlist = self.applyXSLT(CIMdoc, "CommonChecks.sch")
        #checks, invalids, errorlist = self.applyXSLT(CIMdoc, "quest.ruleset.sch")
        #self.report=report
        self.errlist = errorlist
        self.nChecks = checks
        self.nInvalid = invalids
    
        #print "CIMdoc: {0}        self.report: {1}".format(type(CIMdoc), type(self.report) )

        if specificSchematronFile:
            # perform any specific validations
            #report,nChecks,nInvalid=self.__SchematronValidate(CIMdoc,specificSchematronFile)
            checks, invalids, errorlist=self.applyXSLT(CIMdoc,specificSchematronFile)
            
            # add these results to the existing results
            #reportRoot=self.report.getroot()
            #reportRoot.append(report.getroot())
            self.errlist += errorlist
            self.nChecks += checks
            self.nInvalid += invalids
        
        # calculate any derived state
        self.__updateState()

    def __updateState(self):

        if self.nChecks>0:
            self.percentComplete=str(((self.nChecks-self.nInvalid)*100.0)/self.nChecks)
        else:
            self.percentComplete=100.0
        if self.nInvalid>0:
            self.valid=False
        else:
            self.valid=True

    def __CimAsHtml(self,CIMdoc):
        ''' generate the cim as html '''

        # first format it using xmlformat.xsl
        xslt_doc = ET.parse(os.path.join(self.XSLdir,"xmlformat.xsl"))
        transform = ET.XSLT(xslt_doc)
        formattedCIMdoc = transform(CIMdoc)
        # next translate it into html using verbid.xsl
        xslt_doc = ET.parse(os.path.join(self.XSLdir,"verbid.xsl"))
        transform = ET.XSLT(xslt_doc)
        cimHtml = transform(formattedCIMdoc)
        return cimHtml

    """
    def __SchematronValidate(self,CIMdoc,SchematronFile,SchematronReport="schematron-report.xsl"):
        ''' Validation common to both Component and Simulation '''
        sct_doc = ET.parse(os.path.join(self.XSLdir,SchematronFile))
        #obtain schematron error report in html
        xslt_doc = ET.parse(os.path.join(self.XSLdir,SchematronReport))
        transform = ET.XSLT(xslt_doc)
        xslt_doc = transform(sct_doc)
        transform = ET.XSLT(xslt_doc)
        report = transform(CIMdoc)
        # find out how many errors and checks there were
        nChecks = len(report.xpath('//check'))
        nInvalid = len(report.xpath('//invalid'))
        return report,nChecks,nInvalid
    """

    def validateFile(self,fileName):
        tmpDoc=ET.parse(file)
        self.validateDoc(tmpDoc)

    def validateDoc(self,CIMdoc,cimtype=''):
        ''' This method validates a CIM document '''
        #validate against schema
        if self.schemaValidate:
            #CIM currently fails the schema parsing
            xmlschema_doc = ET.parse(self.CIMschema)
            xmlschema = ET.XMLSchema(xmlschema_doc)
            if xmlschema.validate(CIMdoc):
                logging.debug("CIM Document validates against the cim schema")
            else:
                logging.debug("CIM Document fails to validate against the cim schema")
            log = xmlschema.error_log
            logging.debug("CIM Document schema errors are "+log)
            return log,

        if self.contentValidate:
            #validate against schematron checks
            if cimtype=='component':
                self.__validationStep(CIMdoc,"ComponentChecks.sch")
            elif cimtype=='simulation':
                self.__validationStep(CIMdoc,"SimulationChecks.sch")
            else:
                logging.info('Invalid validation type %s found - calling it valid for now'%cimtype)
                self.__validationStep(CIMdoc)

        # create an html representation of our document
        self.cimHtml=''#self.__CimAsHtml(CIMdoc)
        # don't really want to see the HTML for now ...


    def __markup_rules_tree(self, stTree):
        stRoot = stTree.getroot()
        stxmlns  = stRoot.nsmap[None]
        stxmlns_string = "{" + "{0}".format(stxmlns) + "}"

        stRule = None
        for elem in stRoot.iter():
            #print "{0}elem[0] (len: {1}): {2}".format(type(elem), len(elem), elem.tag)
            if len(elem) == 0:
                continue
            if type(elem) == ET._Comment:
                continue

            if elem.tag.endswith("rule") and len(elem) > 0:
                    stRule = elem
                    context = stRule.attrib["context"]

                    repFlag = ET.Element(stxmlns_string + "report", nsmap=stRoot.nsmap)
                    repFlag.attrib["test"] = "true()"
                    #repFlag.text = "{0}: {1}".format(rule_count_flag, context)
                    repFlag.text = "{0}:".format(rule_count_flag)

                    stRule.append(repFlag)


    def __markup_line_attr(self, stTree):

        for elem in stTree.iter():
            if type(elem) == ET._Comment:
                continue
            if elem.tag.endswith("report") or elem.tag.endswith("assert"):
                lineelem = ET.fromstring('<value-of select="@__src_line_number_"/>')
                lineelem.tail = ":" + elem.text
                elem.text = "Line "
                elem.insert(0, lineelem)


    def applyXSLT(self, CIMdoc, rulesFile, xsltFile="schematron-report.xsl"):

        try:
            rulesTree = ET.parse(os.path.join(self.XSLdir, rulesFile))
            xsltSource = open(os.path.join(self.XSLdir, xsltFile), 'r').read()
            xsltTree = ET.parse(StringIO.StringIO(xsltSource))
        except IOError,e:
            print "IO error: Unable to read XSLT source file {0}".format(xsltFile)
            sys.exit(1)
        except ET.XMLSyntaxError,e:
            print "XML Syntax error: Unable to parse source file {0}".format(xsltFile)
            sys.exit(1)

        i=1
        for elem in CIMdoc.iter():
            #elem.attrib["__src_line_number_"] = str(elem.sourceline)
            elem.attrib["__src_line_number_"] = str(i)
            i += 1

        #self.__markup_line_attr(rulesTree)

        xslt = ET.XSLT(xsltTree)
        #self.__dumpTree()
        xslt_schematron = xslt(rulesTree)
        schematron = ET.XSLT(xslt_schematron)

        #print "-=========: CIMdoc :==========-"
        #print ET.tostring(CIMdoc)
        #print "-===============================-"
        #print "-=====: Transformed Output :=====-"
        #print ET.tostring(xslt_schematron, pretty_print=True)
        #print "=================================="

        xml_output = schematron(CIMdoc)

        #print "-=====: XML-Schematron Output :=====-"
        #print ET.tostring(xml_output, pretty_print=True)
        #print "-===================================-"

        count = ET.XPath("count(//*[name() = $arg])")
        checks = int(count(xml_output, arg="check"))
        invalids = int(count(xml_output, arg="invalid"))

        list_elements = ET.XPath("//*[name() = $arg]")
        error_list = list_elements(xml_output, arg="li")

        print "Checks: {0}  Invalids: {1}".format(checks, invalids)
        return (checks, invalids, error_list)
    

class CIMViewer:
    ''' View CIM documents in the CIM viewer interface '''
    def __init__(self):
        ''' Setup the CIMViewer tools etc '''
        self.blank={}
    
    def cimViewDoc(self,CIMdoc):
        ''' This method views the CIM info in the view interface '''
        # create an html representation of our document
        #parser = ET.XMLParser(ns_clean=True)
        #etree=ET.parse(CIMdoc, parser)
        #root=CIMdoc.getroot() # "CIMRecordSet" or "CIMRecord" element
        if CIMdoc.tag=='CIMDocumentSet':
            qnModels = CIMdoc.findall('modelComponent')
            #qnExps = CIMdoc.findall('CIMRecord/CIMRecord/numericalExperiment')
            #qnSims = CIMdoc.findall('CIMRecord/CIMRecord/simulationRun')
            #qnData = root.findall('{%s}CIMRecord/{%s}CIMRecord/{%s}dataObject' %(cimns,cimns,cimns))
        
            #first, get nav headings
            mods=[]
            #exps=[]
            #sims=[]
            #datas=[]
            
            for model in qnModels:
                m = modelView(model, 'model')
                m.getnavname(model)
                mods.append(m)
            
            #if viewtype == 'model':
            #m=modelView(CIMfile, viewtype)
            #m=modelView(CIMdoc,'model')
            m=modelView(qnModels[0],'model')
            m.genhtml(qnModels[0])
            #return render_to_response('ModelView.html',{'mods':mods,'exps':exps,'sims':sims,'datas':datas, 'code':m.code})
            
            #cimHtml=''
        
            #return cimHtml
            return m.code

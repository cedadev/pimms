from lxml import etree as et
import os
import time
import hashlib
import StringIO

rule_count_flag = "__rule_count_flag"

class XMLreport(object):

    __slots__ = ("__isValid", "__file", "__ts",\
                 "__filesize", "__hashhex", "__tree",\
                 "__parseErrors", "__schemaErrors", \
                 "__schemafile")



    def __init__(self, schema=""):
        self.status = False
#        self.__file = ufile
        self.__ts = time.localtime()
        self.__filesize = 0
        self.__hashhex = ""
        self.__schemafile = schema
        self.__tree = None

#        filedata = open(filename, 'r').read()
#        self.__filesize = os.path.getsize(filename)
#        self.__filesize = len(ufile.value)
#        self.hexdigest = hashlib.sha1(ufile.value).hexdigest()

        self.__parseErrors = []
        self.__schemaErrors = []


    @property
    def hexdigest(self):
        return self.__hashhex

    @hexdigest.setter
    def hexdigest(self, hashhex):
        if len(hashhex) != 40:
            self.__hashhex = "Invalid SHA-1 digest."
        else:
            self.__hashhex = hashhex

    @property
    def timestamp(self):
         return self.__ts

    @property
    def uri(self):
        return self.__file.filename

    @property
    def parseErrors(self):
        return self.__parseErrors

    @property
    def schemaErrors(self):
        return self.__schemaErrors

    @property
    def filesize(self):
        return self.__filesize

    @property
    def status(self):
        return "Valid" if self.__isValid else "Invalid"

    @status.setter
    def status(self, value):
        if isinstance(value, bool):
            self.__isValid = value
        else:
            raise Exception("Incompatible type assignment: .__isValid")

    def makeXMLParseReport(self):
        self.parse()

        root = et.Element("CVR")
        root.append(et.Element("report"))
        report = root[0]
        
	children = ["URI", "bytes", "SHA1", "date", "rtype", "status"]

        for child in children:
            report.append(et.Element(child))

        report[children.index("URI")].text = self.__file.filename
        report[children.index("bytes")].text = str(self.__filesize)
        report[children.index("SHA1")].text = self.hexdigest

	date = report[children.index("date")]

        timetitles = ["year", "month", "day", "hour", "minute", "second"]

        for title in timetitles:
           elem = et.Element(title)
           elem.text = str(self.timestamp[timetitles.index(title)])
           date.append(elem)

        report[children.index("status")].text = self.status

        if len(self.__parseErrors) != 0:
            error = et.Element("error")
            report.append(error)

            errtext = et.Element("text")
            errline = et.Element("line")
            errcol = et.Element("column")

            pe = self.__parseErrors.pop()
            errtext.text = pe.msg
            errline.text = str(pe.position[0])
            errcol.text = str(pe.position[1])

            error.append(errtext)
            error.append(errline)
            error.append(errcol)
        else:
            report[children.index("rtype")].text = str((self.__tree).getroot().tag)

#        print(et.tostring(root, pretty_print=True))
#        return(et.tostring(root, pretty_print=True))
        return et.tostring(root, pretty_print=True)

    def parse(self):
        try:
#            self.__tree = et.parse(self.__filename)
            self.__tree = et.parse(self.__file.file)
            self.status = True
            self.__file.file.close()

        except et.XMLSyntaxError,e:
            self.__parseErrors.append(e)
            self.status = False

    def writeXMLParseReport(self):
        #root = self.makeReport()
        #return(et.tostring(root, pretty_print=True))
        return self.makeXMLParseReport()

    def makeHTMLParseReport(self, xmlbuffer):
        try:
            xmlroot = et.fromstring(xmlbuffer)
        except et.XMLSyntaxError, e:
            return "Invalid XML input: Unable to generate HTML."

        report = xmlroot[0]

        children = ["URI", "bytes", "SHA1", "date", "rtype", "status", "error"]
        timetitles = ["year", "month", "day", "hour", "minute", "second"]
        errlines = ["text", "line", "column" ]

        htmlresponse = "<html><title>XML Validation Report</title>\
                        <body><h3>XML Validation Report</h3><hr/>"

        filename = report[children.index("URI")].text
        bytes = report[children.index("bytes")].text
        hexdigest = report[children.index("SHA1")].text
        status = report[children.index("status")].text

        statustext = "<font color=#"
        if status=="Valid":
            statustext += "00FF00>Valid</font>"
        else:
            statustext += "FF0000>Invalid</font>"

        dateroot = report[children.index("date")]
        datelist = []

        for t in timetitles:
            datelist.append(int(dateroot[timetitles.index(t)].text))

        datestring = "{0}-{1:02}-{2:02} {3:02}:{4:02}:{5:02}".format(*datelist)

        htmlresponse += "File: <code>{0}</code><br/>Size: <code>{1}</code><br/>\
                         SHA-1: <code>{2}</code><br/>Generated at: <code>{3}</code><br/><br/>\
                         Status: <b><code>{4}</code></b><br/>".format(filename, bytes, hexdigest, datestring, statustext)

        if status=="Invalid":
            errorroot = report[children.index("error")]
            etext = errorroot[errlines.index("text")].text
            eline = errorroot[errlines.index("line")].text
            ecol = errorroot[errlines.index("column")].text
            htmlresponse += "<pre>    "
            #htmlresponse += "<pre>    {0}</pre>".format(etext)

        htmlresponse += "</body></html>"
        return htmlresponse

    def writeHTMLParseReport(self):
        """Returns HTML string containing parse report."""
        xmlbuffer = self.makeXMLParseReport()
        htmlresponse = self.makeHTMLParseReport(xmlbuffer)
        return htmlresponse

    def setSchema(self, schema):
        if os.path.exists(schema):
            self.__schemafile = schema
        else:
            raise Excpetion("Unable to access schema file.")


    def schemaValidate(self, schema=""):
        schema = et.XMLSchema(et.parse(self.__schemafile))

        if not self.__tree:
            self.parse()

        schema.validate(self.__tree)

        log = schema.error_log
        if len(log) == 0:
            self.status = True
        else:
            self.status = False

        return self.makeXMLValidationReport(log)

    def makeXMLValidationReport(self, log):
        root = et.Element("CSVR")
        root.append(et.Element("report"))
        report = root[0]

        children = ["URI", "bytes", "SHA1", "schema", "date", "status"]

        for child in children:
            report.append(et.Element(child))

        report[children.index("URI")].text = self.__file.filename
        report[children.index("bytes")].text = str(self.__filesize)
        report[children.index("SHA1")].text = self.hexdigest
        report[children.index("schema")].text = self.__schemafile

        date = report[children.index("date")]

        timetitles = ["year", "month", "day", "hour", "minute", "second"]

        for title in timetitles:
           elem = et.Element(title)
           elem.text = str(self.timestamp[timetitles.index(title)])
           date.append(elem)

        report[children.index("status")].text = self.status

        if(self.status == "Invalid"):
            errorlist = et.Element("errorlist")

            for e in log:
                err = et.Element("error")

                err_filename = et.Element("file")
                err_line = et.Element("line")
                err_message = et.Element("message")

                err_filename.text = e.filename
                err_line.text = str(e.line)
                err_message.text = e.message

                err.append(err_filename)
                err.append(err_line)
                err.append(err_message)

                errorlist.append(err)

            report.append(errorlist)


        return et.tostring(root, pretty_print=True)


    def writeHTMLValidationReport(self, xmlbuffer):
        try:
            xmlroot = et.fromstring(xmlbuffer)
        except et.XMLSyntaxError,e:
            return "Invalid XML input: Unable to generate validation report."

        report = xmlroot[0]

        children = ["URI", "bytes", "SHA1", "schema", "date", "status", "errorlist"]
        timetitles = ["year", "month", "day", "hour", "minute", "second"]
        errlines = ["file", "line", "message" ]

        htmlresponse = "<html><title>CIM Schema Validation Report</title>\
                        <body><h3>CIM Schema Validation Report</h3><hr/>"

        filename = report[children.index("URI")].text
        bytes = report[children.index("bytes")].text
        hexdigest = report[children.index("SHA1")].text
        schemafile = report[children.index("schema")].text
        status = report[children.index("status")].text

        statustext = "<font color=#"
        if status=="Valid":
            statustext += "00FF00>Valid</font>"
        else:
            statustext += "FF0000>Invalid</font>"

        dateroot = report[children.index("date")]
        datelist = []

        for t in timetitles:
            datelist.append(int(dateroot[timetitles.index(t)].text))

        datestring = "{0}-{1:02}-{2:02} {3:02}:{4:02}:{5:02}".format(*datelist)

        htmlresponse += "File: <code>{0}</code><br/>Size: <code>{1}</code><br/> \
                         SHA-1: <code>{2}</code><br/>Schema: <code>{3}</code><br/> \
                         Generated at: <code>{4}</code><br/><br/>Status: <b><code>{5}</code></b> \
                         <br/>".format(filename, bytes, hexdigest, schemafile, datestring, statustext)

        if status == "Invalid":
            htmlresponse += "<br/>The following validation errors were detected:<br/><br/>"
            errorlist = report[children.index("errorlist")]

            i=1
            for err in errorlist:
#                err_file = err[errlines.index("file")].text
                err_file = filename
                err_line = err[errlines.index("line")].text
                err_message = err[errlines.index("message")].text

                htmlresponse += "[{0}]<code>    {1}:{2}</code>".format(i, err_file, err_line)
                htmlresponse += "<pre>        {0}</pre><br/>".format(err_message)
                i += 1


        htmlresponse += "</body></html>"
        return htmlresponse


    def Schematron(self, stFile, CIMdoc=""):

        try:
            stSource = open(stFile, 'r').read()
            stTree = et.parse(StringIO.StringIO(stSource) )
            #stTree = et.XML(stSource)
            #print StringIO.StringIO(stSource).getvalue()
            #print et.tostring(stTree)
        except IOError, e:
            print "IO Error: Unable to open file {0}".format(e.filename)
            sys.exit(1)
        except et.XMLSyntaxError, e:
            print "XML Syntax Error: Unable to parse Schematron source file {0}".format(stFile)
            sys.exit(1)

        if CIMdoc:
            self.__tree = CIMdoc

        self.__markup_rules_tree(stTree)
          
        #print "================"
        #print et.tostring(stTree)
        #print "================"

        try:

            schematron = et.Schematron(stTree)
            schematron.validate(self.__tree)
#        except et.SchematronParseError as e:
#            print "Schematron Parse Error: {0}".format(e) 
#            sys.exit(1)
        except et.SchematronValidateError, e:
            print e
            sys.exit(1)

        #self.__dump_rule_flags(schematron.error_log)

        status = True
        check_count = 0
        errlist = []
        for err in schematron.error_log:
            if rule_count_flag in err.message:
                check_count += 1
            else:
                errlist.append(err)

        if len(errlist) > 0:
            status = False

        return (status, errlist, check_count)


    def __markup_rules_tree(self, stTree):
        stRoot = stTree.getroot()
        stxmlns  = stRoot.nsmap[None]
        stxmlns_string = "{" + "{0}".format(stxmlns) + "}"

        stRule = None
        for elem in stRoot.iter():
            #print "{0}elem[0] (len: {1}): {2}".format(type(elem), len(elem), elem.tag)
            if len(elem) == 0:
                continue
            if type(elem) == et._Comment:
                continue

            if elem.tag.endswith("rule") and len(elem) > 0:
                    stRule = elem
                    context = stRule.attrib["context"]

                    repFlag = et.Element(stxmlns_string + "report", nsmap=stRoot.nsmap)
                    repFlag.attrib["test"] = "true()"
                    #repFlag.text = "{0}: {1}".format(rule_count_flag, context)
                    repFlag.text = "{0}:".format(rule_count_flag)

                    stRule.append(repFlag)

 
        #print "stRoot.nsmap: {0}".format(stRoot.nsmap)
        #print "stxmlns: {0}".format(stxmlns)
        #print "stRule.tag: {0}".format(stRule.tag)
        #print "repFlag.nsmap: {0}".format(repFlag.nsmap)
        #print "repFlag.tag: {0}".format(repFlag.tag)
        #print "context = {0}".format(stRule.attrib["context"])
        #print "================"
        #print et.tostring(stTree)
        #print "================"


    def __markup_line_attr(self, stTree):

        for elem in stTree.iter():
            if type(elem) == et._Comment:
                continue
            if elem.tag.endswith("report") or elem.tag.endswith("assert"):
                lineelem = et.fromstring('<value-of select="@__src_line_number_"/>')
                lineelem.tail = ":" + elem.text 
                elem.text = "Line "
                elem.insert(0, lineelem)
                #elem.text = "Line {0}:  {1}".format('<value-of select="@__src_line_number_"/>', elem.text)
                #print et.tostring(elem, method="text")



    def __dump_rule_flags(self, error_log):

        i = 1
        for err in error_log:
            if rule_count_flag in err.message:
                if i==1: print "-=======: Rule Flags Start :=======-"
                print "[{0}] {1}".format(i, err.message)
                i += 1

        if i>1: print "-========: Rule Flags End :========-"


    def __dumpTree(self):
        print "-========: self.__tree BEGINS :=========-"
        print et.tostring(self.__tree)
        print "-=========: self.__tree ENDS :==========-"


    def applyXSLT(self, xsltFile, rulesFile):

        try:
            rulesTree = et.parse(rulesFile)
            xsltSource = open(xsltFile, 'r').read()
            xsltTree = et.parse(StringIO.StringIO(xsltSource))
        except IOError, e:
            print "IO error: Unable to read XSLT source file {0}".format(xsltFile)
            sys.exit(1)
        except et.XMLSyntaxError, e:
            print "XML Syntax error: Unable to parse source file {0}".format(xsltFile)
            sys.exit(1)

#        for elem in xmlTree.iter():
        for elem in self.__tree.iter():
            elem.attrib["__src_line_number_"] = str(elem.sourceline)

        self.__markup_line_attr(rulesTree)

        xslt = et.XSLT(xsltTree)
        #self.__dumpTree()
        xslt_schematron = xslt(rulesTree)
        schematron = et.XSLT(xslt_schematron)


        #print "-=========: XML Tree :==========-"
        #print et.tostring(xmlTree)
        #print "-===============================-"
        #print "-=====: Transformed Output :=====-"
        #print et.tostring(xslt_schematron, pretty_print=True)
        #print "=================================="

        xml_output = schematron(self.__tree)

        #print "-=====: XML-Schematron Output :=====-"
        #print et.tostring(xml_output, pretty_print=True)
        #print "-===================================-"

        count = et.XPath("count(//*[name() = $arg])")
        checks = int(count(xml_output, arg="check"))
        invalids = int(count(xml_output, arg="invalid"))

        list_elements = et.XPath("//*[name() = $arg]")
        error_list = list_elements(xml_output, arg="li")

        return (checks, invalids, error_list)

from django.http import HttpResponse,HttpResponseRedirect,HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render_to_response
import os
from lxml import etree as ET
class XMLDocumentHandler(object):
    def __init__(self,documentType,docID):
        self.documentType=documentType
        self.docID=docID
    def xml(self,request):
        return HttpResponse('Not Implemented')
        
NS='http://www.metaforclimate.eu/cim/1.1'
class XMLExperimentHandler(XMLDocumentHandler):
    
    def __init__(self,documentType,docID):
        ''' Read appropriate document from disk '''
        # This is a complete hack, gets the wrong document '''
        XMLDocumentHandler.__init__(self,documentType,docID)
        experimentDir = './data/experiments'
        tmp=os.listdir(experimentDir)
        files=[]
        for f in tmp:
            if f.endswith('.xml'): files.append(os.path.join(experimentDir, f)) 
        doc=files[int(docID)]
        etree=ET.parse(doc)
        self.xmlv=etree.getroot()
        
    def xml(self,request):
        return render_to_response('xml.html',{'x':self.xmlv,'NS':NS})
                
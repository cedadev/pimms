import re
import os
from lxml import etree

from subprocess import *

from django.conf import settings
logging=settings.LOG


#get location of this directory for path setting
thisDir = os.path.dirname(__file__)
 
  
def checkMM(mmfile):
    ''' Checks that a mindmap file is valid and returns an 
    error list and warning list if not.
    
    In--
    > mmfile - Freemind generated mindmap file
    
    Out--
    > errorlist - List of errors encountered during xslt translation
    > warninglist - List of warnings encountered during xslt translation
    '''
    
    logging.debug("INTO checkMM")
    #pull in the xsl transformation file
    XSLFileName = os.path.join(thisDir, 'xslt', 'mmcheck_0.9.0_bdl.xsl')
    #set the fpre file
    fpre = open(os.path.join(thisDir,'xslt', str(mmfile)+'.pre'), 'w')
    #begin reading through each line in the mm file, and....
    for line in mmfile:
        # make necessary mods to richcontent symbols
        if re.match("^<richcontent", line):
            line = line.replace('[','<')
            line = line.replace(']','>') 
            #write edited line to pre file 
        fpre.write(line)
    #close the pre file
    fpre.close()
    
    # pull in the xml and xslt files
    xml_input = etree.parse(fpre.name)
    xslt_root = etree.parse(XSLFileName)
    #set up the transformation
    transform = etree.XSLT(xslt_root)
    
    # make the transformation and collect any errors
    transform(xml_input)    
    errorlog = transform.error_log
    
    #cleanup of temporary files
    os.remove(fpre.name)
    
    # separate out warnings and errors
    errorlist = []
    warninglist = []
    for entry in errorlog:
      if entry.message.startswith('*ERROR'):
        errorlist.append(entry.message.replace('*ERROR',''))
      if entry.message.startswith('*WARNING'):
        warninglist.append(entry.message.replace('*WARNING',''))
        
    #Return the collection of errors and warnings
    return errorlist, warninglist
  
  
def translateMM(mmfile):
    ''' translate mindmap to qn xml
    
    '''
  
    #pull in the xsl transformation file
    XSLFileName = os.path.join(thisDir, 'xslt', 'mm2q_bdl.xsl')

    #pull in the mindmap file to be translated
    fin = mmfile

    fpre = open(os.path.join(thisDir,'xslt', str(mmfile)+'.pre'), 'w')

    for line in fin:
      if re.match("^<text>",line) or re.match("^<richcontent TYPE=",line):
        line=line.replace('[','<')
        line=line.replace(']','>')
      fpre.write(line)
    fpre.close()

    xslt_root = etree.parse(XSLFileName)
    xml_input = etree.parse(fpre.name)
    transform = etree.XSLT(xslt_root)
    strResult = transform(xml_input)

    os.remove(os.path.join(thisDir,'xslt', str(mmfile)+'.pre'))

    return strResult
  
  
  
  

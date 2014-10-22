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
    
    logging.debug("BEGIN checkMM")
    #pull in the xsl transformation file
    XSLFileName = os.path.join(thisDir, 'xslt', 'mmcheck_0.9.0_bdl.xsl')
    #set the fpre file

    if not os.path.exists(settings.PIMMS_TMP_DIR):
       os.makedirs(settings.PIMMS_TMP_DIR)
    fpre = open(os.path.join(settings.PIMMS_TMP_DIR, str(mmfile)+'.pre'), 'w')
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
    logging.debug('END checkMM')
    return errorlist, warninglist
  
  
def translateMM(mmfile):
    ''' translate mindmap to qn xml
    
    '''
  
    logging.debug('BEGIN translateMM')
    #pull in the xsl transformation file
    XSLFileName = os.path.join(thisDir, 'xslt', 'mm2q_bdl.xsl')

    #pull in the mindmap file to be translated
    fin = mmfile

    fpre = open(os.path.join(settings.PIMMS_TMP_DIR, str(mmfile)+'.pre'), 'w')

    for line in fin:
      if re.match("^<text>",line) or re.match("^<richcontent TYPE=",line):
        line=line.replace('[','<')
        line=line.replace(']','>')
      fpre.write(line)
    fpre.close()

    logging.debug('  parse xslt')
    xslt_root = etree.parse(XSLFileName)
    logging.debug('  parse input')
    xml_input = etree.parse(fpre.name)
    logging.debug('  create transform')
    transform = etree.XSLT(xslt_root)
    logging.debug('  apply transform')
    strResult = transform(xml_input)
    logging.debug('  done')

    os.remove(os.path.join(settings.PIMMS_TMP_DIR, str(mmfile)+'.pre'))

    logging.debug('END translateMM')
    return strResult
  
  
  
  

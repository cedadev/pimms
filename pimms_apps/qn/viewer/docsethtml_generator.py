"""
HTML generator for different sections of a CIMDocumentSet CIM instance.
"""

# Module imports.
from pimms_apps.qn.viewer.modelhtml_generator import get_modelhtml
from pimms_apps.qn.viewer.simhtml_generator import get_simrunhtml
from pimms_apps.qn.viewer.gridhtml_generator import get_gridhtml
from pimms_apps.qn.viewer.datahtml_generator import get_datahtml
from pimms_apps.qn.viewer.plathtml_generator import get_plathtml


#namespaces used within the CIM
cimns = 'http://www.purl.org/org/esmetadata/cim/1.5/schemas'
gmdns = 'http://www.isotc211.org/2005/gmd'
gcons = 'http://www.isotc211.org/2005/gco'
xsins = 'http://www.w3.org/2001/XMLSchema-instance'


def find_models(elemroot):
    """
    Find any modelComponent documents embedded within elemroot
    """
    return elemroot.findall('modelComponent')

def find_simulationruns(elemroot):
    """
    Find any simulationRun documents embedded within elemroot
    """
    return elemroot.findall('simulationRun')

def find_gridspecs(elemroot):
    """
    Find any gridspec documents embedded within elemroot
    """
    return elemroot.findall('gridSpec')

def find_dataobjs(elemroot):
    """
    Find any dataObject documents embedded within elemroot
    """
    return elemroot.findall('dataObject')

def find_platforms(elemroot):
    """
    Find any platform documents embedded within elemroot
    """
    return elemroot.findall('platform')


def get_docsethtml(cimxml):
    """
    Generate a block of html code to render a CIMDocumentSet view.
    """

    #Find the model(s) in the document set
    models = find_models(cimxml)
    #Find the simulationRun(s) in the document set
    simruns = find_simulationruns(cimxml)
    #Find the gridspec(s) in the document set
    gridspecs = find_gridspecs(cimxml)
    #Find the dataObject(s) in the document set
    dataobjs = find_dataobjs(cimxml)
    #Find the platform(s) in the document set
    platforms = find_platforms(cimxml)
    
    #begin html text generation
    docsethtml=[]

    for s in simruns:
        simrunhtml = get_simrunhtml(s)
        docsethtml += simrunhtml
    
    for m in models:
        modelhtml = get_modelhtml(m)
        docsethtml += modelhtml
    
    for p in platforms:
        plathtml = get_plathtml(p)
        docsethtml += plathtml
        
    #we want an outer wrapper around the potential of many gridspecs
    docsethtml.append('<div id="acc_wrapper">')
    docsethtml.append('    <div id="content">')
    docsethtml.append('        <div id="container">')
    docsethtml.append('            <div id="main">')
    docsethtml.append('<ul class="accordion" id="acc1">')
    docsethtml.append('<li>')
    docsethtml.append('<h4 class="acc_docheader">Gridspecs</h4>')
    docsethtml.append('<div class="inner">')

    for g in gridspecs:
        gridhtml = get_gridhtml(g)
        docsethtml += gridhtml

    #Complete the outer html code
    docsethtml.append('</div>')
    docsethtml.append('</li>')
    docsethtml.append('</ul>')
    docsethtml.append('</div>')
    docsethtml.append('</div>')
    docsethtml.append('</div>')
    docsethtml.append('</div>')
    docsethtml.append('<br/>')
    
    #we want an outer wrapper around the potential of many dataObjects
    docsethtml.append('<div id="acc_wrapper">')
    docsethtml.append('    <div id="content">')
    docsethtml.append('        <div id="container">')
    docsethtml.append('            <div id="main">')
    docsethtml.append('<ul class="accordion" id="acc1">')
    docsethtml.append('<li>')
    docsethtml.append('<h4 class="acc_docheader">Data Files</h4>')
    docsethtml.append('<div class="inner">')

    for d in dataobjs:
        datahtml = get_datahtml(d)
        docsethtml += datahtml

    #Complete the outer html code
    docsethtml.append('</div>')
    docsethtml.append('</li>')
    docsethtml.append('</ul>')
    docsethtml.append('</div>')
    docsethtml.append('</div>')
    docsethtml.append('</div>')
    docsethtml.append('</div>')
    docsethtml.append('<br/>')
           
    return docsethtml
"""
HTML generator for different sections of a modelComponent CIM instance.
"""

# Module imports.
import lxml
from lxml import etree as et


#namespaces used within the CIM
cimns = 'http://www.purl.org/org/esmetadata/cim/1.5/schemas'
gmdns = 'http://www.isotc211.org/2005/gmd'
gcons = 'http://www.isotc211.org/2005/gco'
xsins = 'http://www.w3.org/2001/XMLSchema-instance'


def get_component_shortname(cimxml):
    """
    Get the component shortname.
    """
    return cimxml.find('shortName')


def get_mihtml(elemroot):
    """
    Manage html markup of main component level info
    """
    mihtml = []
    mihtml.append('<ul>')
    mihtml.append('<li>')
    mihtml.append('<h5>Overview Information</h5>')
    mihtml.append('<div class="inner">')

    #First get non-attribute information
    modshortname = elemroot.find('shortName')
    modlongname = elemroot.find('longName')
    moddescription = elemroot.find('description')

    for mi in [modshortname, modlongname, moddescription]:
        if mi is not None:
            mihtml.append('            <table width=100%>')
            mihtml.append('                <tr class="acc_row">')
            mihtml.append('                    <td width = 20%>')
            mihtml.append('                        <p class="titletext">%s</p>' %mi.tag)
            mihtml.append('                    </td>')
            mihtml.append('                    <td><p class="bodytext">%s</p></td>'  %mi.text)
            mihtml.append('                </tr> ')
            mihtml.append('            </table>')

    #and now attribute info
    modtype = elemroot.find('type').get('value')
    if modtype is not None:
        mihtml.append('            <table width = 100%>')
        mihtml.append('                <tr class="acc_row">')
        mihtml.append('                    <td width = 20%>')
        mihtml.append('                        <p class="titletext">type</p>')
        mihtml.append('                    </td>')
        mihtml.append('                    <td><p class="bodytext">%s</p></td>'  %modtype)
        mihtml.append('                </tr> ')
        mihtml.append('            </table>')

    mihtml.append('</div>')
    mihtml.append('</li>')
    mihtml.append('</ul>')

    return mihtml


def rp_iter(elemroot, rphtml):
    """
    Iterate through and harvest information on responsible parties
    """
    cl = elemroot.find('{%s}role/{%s}CI_RoleCode' %(gmdns, gmdns))
    role = cl.get('codeListValue')

    #get individual name or organisation name
    ind_org_name = '{%s}individualName/{%s}CharacterString' %(gmdns, gcons)
    
    if elemroot.findtext(ind_org_name):
        name = elemroot.findtext(ind_org_name)
    else:
        name = elemroot.findtext('{%s}organisationName/{%s}CharacterString' %(gmdns, gcons))
       
    address = elemroot.findtext('{%s}contactInfo/{%s}CI_Contact/{%s}address/{%s}CI_Address/{%s}deliveryPoint/{%s}CharacterString' %(gmdns, gmdns, gmdns, gmdns, gmdns, gcons))
    email = elemroot.findtext('{%s}contactInfo/{%s}CI_Contact/{%s}address/{%s}CI_Address/{%s}electronicMailAddress/{%s}CharacterString' %(gmdns, gmdns, gmdns, gmdns, gmdns, gcons))
    
    rphtml.append('            <table width=100%>')
    rphtml.append('                <tr class="acc_row">')
    rphtml.append('                    <td width = 20%>')
    rphtml.append('                        <p class="titletext">Role</p>')
    rphtml.append('                    </td>')
    rphtml.append('                    <td>')
    rphtml.append('                      <p class="bodytext">%s</p>' %role)
    rphtml.append('                    </td>')
    rphtml.append('                </tr> ')
    rphtml.append('                <tr height="5px" class="acc_row">')
    rphtml.append('                    <td width = 20%>')
    rphtml.append('                        <p class="titletext">Name</p>')
    rphtml.append('                    </td>')
    rphtml.append('                    <td>')
    rphtml.append('                      <p class="bodytext">%s</p>' %name)
    rphtml.append('                    </td>')
    rphtml.append('                </tr> ')
    rphtml.append('                <tr height="5px" class="acc_row">')
    rphtml.append('                    <td width = 20%>')
    rphtml.append('                        <p class="titletext">Address</p>')
    rphtml.append('                    </td>')
    rphtml.append('                    <td>')
    rphtml.append('                      <p class="bodytext">%s</p>' %address)
    rphtml.append('                    </td>')
    rphtml.append('                </tr> ')
    rphtml.append('                <tr height="5px" class="acc_row">')
    rphtml.append('                    <td width = 20%>')
    rphtml.append('                        <p class="titletext">Email</p>')
    rphtml.append('                    </td>')
    rphtml.append('                    <td>')
    rphtml.append('                      <p class="bodytext">%s</p>' %email)
    rphtml.append('                    </td>')
    rphtml.append('                </tr> ')
    rphtml.append('            </table>')
    rphtml.append('            <br/>')

    return rphtml


def get_rphtml(elemroot):
    """
    Manage html markup of responsible party info
    """
    respParties = elemroot.findall('responsibleParty')
    rphtml = []
    if respParties:
        rphtml.append('<ul>')
        rphtml.append('<li>')
        rphtml.append('<h5>Responsible Parties</h5>')
        rphtml.append('<div class="inner">')
        for party in respParties:
            rp_iter(party, rphtml)
        rphtml.append('</div>')
        rphtml.append('</li>')
        rphtml.append('</ul>')

    return rphtml


def cp_iter(elemroot, cphtml):
    """
    Iterate through and harvest information on component properties
    """
    cpshortname = elemroot.find('shortName')
    cpvalue = elemroot.find('value')
    cpdesc = elemroot.find('description')
    unit = elemroot.find('units')
    if unit is not None:
        cpunit = unit.get('value')
    cpprops = elemroot.findall('componentProperty')

    # First, check if this is/isn't a 'parent' componentProperty by searching for a value and render appropriately
    if cpvalue is not None or cpdesc is not None:
        cphtml.append('            <table width=100%>')
        cphtml.append('                <tr class="acc_row">')
        cphtml.append('                    <td width = 30%>')
        cphtml.append('                        <p class="titletext">Property Name</p>')
        cphtml.append('                    </td>')
        cphtml.append('                    <td>')
        cphtml.append('                        <p class="bodytext">%s</p>' %cpshortname.text)
        cphtml.append('                    </td>')
        cphtml.append('                </tr> ')
        if cpvalue is not None:
            cphtml.append('                <tr class="acc_row">')
            cphtml.append('                    <td width = 30%>')
            cphtml.append('                        <p class="titletext">Property Value</p>')
            cphtml.append('                    </td>')
            cphtml.append('                    <td>')
            cphtml.append('                        <p class="bodytext">%s</p>' %cpvalue.text)
            cphtml.append('                    </td>')
            cphtml.append('                </tr> ')
        if unit is not None:
            cphtml.append('                <tr class="acc_row">')
            cphtml.append('                    <td width = 30%>')
            cphtml.append('                        <p class="titletext">Property Units</p>')
            cphtml.append('                    </td>')
            cphtml.append('                    <td>')
            cphtml.append('                        <p class="bodytext">%s</p>' %cpunit)
            cphtml.append('                    </td>')
            cphtml.append('                </tr> ')
        if cpdesc is not None:
            cphtml.append('                <tr class="acc_row">')
            cphtml.append('                    <td width = 30%>')
            cphtml.append('                        <p class="titletext">Property Description</p>')
            cphtml.append('                    </td>')
            cphtml.append('                    <td>')
            cphtml.append('                        <p class="bodytext">%s</p>' %cpdesc.text)
            cphtml.append('                    </td>')
            cphtml.append('                </tr> ')
        cphtml.append('                  <br/>')
        cphtml.append('            </table>')
        #for cp in cpprops:
        #    cp_iter(cp, cphtml)
    else:
        cphtml.append('<ul>')
        cphtml.append('<li>')
        cphtml.append('<h5>%s</h5>' %cpshortname.text)
        cphtml.append('<div class="inner">')
        for cp in cpprops:
            cp_iter(cp, cphtml)
        cphtml.append('</div>')
        cphtml.append('</li>')
        cphtml.append('</ul>')
           
    return cphtml


def get_cphtml(elemroot):
    """
    Manage html markup of component property info
    """
    compProps = elemroot.findall('componentProperties/componentProperty')
    cphtml = []
    if compProps:
        cphtml.append('<ul>')
        cphtml.append('<li>')
        cphtml.append('<h5>Component Properties</h5>')
        cphtml.append('<div class="inner">')
        for cp in compProps:
            cp_iter(cp, cphtml)
        cphtml.append('</div>')
        cphtml.append('</li>')
        cphtml.append('</ul>')

    return cphtml


def cit_iter(elemroot, cithtml):
    """
    Iterate through and harvest information on citations
    """
    #get citation title
    cit_title = elemroot.findtext('{%s}title/{%s}CharacterString' %(gmdns, gcons))
    #get citation type
    pfc = elemroot.find('{%s}presentationForm/{%s}CI_PresentationFormCode' %(gmdns, gmdns))
    cit_type = pfc.get('codeListValue')
    #get citation reference
    cit_ref = elemroot.findtext('{%s}collectiveTitle/{%s}CharacterString' %(gmdns, gcons))
    #get citation location
    cit_loc = elemroot.findtext('{%s}otherCitationDetails/{%s}CharacterString' %(gmdns, gcons))

    #create html block for citation information
    cithtml.append('            <table width=100%>')
    cithtml.append('                <tr class="acc_row">')
    cithtml.append('                    <td width = 20%>')
    cithtml.append('                        <p class="titletext">Title</p>')
    cithtml.append('                    </td>')
    cithtml.append('                    <td>')
    cithtml.append('                      <p class="bodytext">%s</p>' %cit_title)
    cithtml.append('                    </td>')
    cithtml.append('                </tr> ')
    cithtml.append('                <tr height="5px" class="acc_row">')
    cithtml.append('                    <td width = 20%>')
    cithtml.append('                        <p class="titletext">Type</p>')
    cithtml.append('                    </td>')
    cithtml.append('                    <td>')
    cithtml.append('                      <p class="bodytext">%s</p>' %cit_type)
    cithtml.append('                    </td>')
    cithtml.append('                </tr> ')
    cithtml.append('                <tr height="5px" class="acc_row">')
    cithtml.append('                    <td width = 20%>')
    cithtml.append('                        <p class="titletext">Reference</p>')
    cithtml.append('                    </td>')
    cithtml.append('                    <td>')
    cithtml.append('                      <p class="bodytext">%s</p>' %cit_ref)
    cithtml.append('                    </td>')
    cithtml.append('                </tr> ')
    cithtml.append('                <tr height="5px" class="acc_row">')
    cithtml.append('                    <td width = 20%>')
    cithtml.append('                        <p class="titletext">Location</p>')
    cithtml.append('                    </td>')
    cithtml.append('                    <td>')
    cithtml.append('                      <p class="bodytext">%s</p>' %cit_loc)
    cithtml.append('                    </td>')
    cithtml.append('                </tr> ')
    cithtml.append('            </table>')
    cithtml.append('            <br/>')

    return cithtml


def get_cithtml(elemroot):
    """
    Manage html markup of citation info
    """
    citations = elemroot.findall('citation')
    cithtml = []
    if citations:
        cithtml.append('<ul>')
        cithtml.append('<li>')
        cithtml.append('<h5>Citations</h5>')
        cithtml.append('<div class="inner">')
        for citation in citations:
            cit_iter(citation, cithtml)
        cithtml.append('</div>')
        cithtml.append('</li>')
        cithtml.append('</ul>')

    return cithtml


def get_dihtml(elemroot):
    """
    Manage html markup of cim document info
    """
    doc_id = elemroot.find('documentID')
    doc_version = elemroot.find('documentVersion')
    doc_date = elemroot.find('documentCreationDate')
    doc_author = elemroot.find('documentAuthor/{%s}individualName/{%s}CharacterString' %(gmdns, gcons))
    
    dihtml = []
    dihtml.append('<ul>')
    dihtml.append('<li>')
    dihtml.append('<h5>Document Information</h5>')
    dihtml.append('<div class="inner">')
    for di in [doc_id, doc_version, doc_date]:
        if di is not None:
            #tagminns = di.tag.split(cimns + '}')[1]
            dihtml.append('            <table width=100%>')
            dihtml.append('                <tr class="acc_row">')
            dihtml.append('                    <td width = 20%>')
            dihtml.append('                        <p class="titletext">%s</p>' %di.tag)
            dihtml.append('                    </td>')
            dihtml.append('                    <td><p class="bodytext">%s</p></td>'  %di.text)
            dihtml.append('                </tr> ')
            dihtml.append('            </table>')
    for di in [doc_author]:
        if di is not None:
            tagminns = di.tag.split(gcons + '}')[1]
            dihtml.append('            <table width=100%>')
            dihtml.append('                <tr class="acc_row">')
            dihtml.append('                    <td width = 20%>')
            dihtml.append('                        <p class="titletext">%s</p>' %tagminns)
            dihtml.append('                    </td>')
            dihtml.append('                    <td><p class="bodytext">%s</p></td>'  %di.text)
            dihtml.append('                </tr> ')
            dihtml.append('            </table>')
    dihtml.append('</div>')
    dihtml.append('</li>')
    dihtml.append('</ul>')

    return dihtml


def get_cchtml(elemroot):
    """
    Manage html markup of child components info
    """
    childComponents=elemroot.findall('childComponent/modelComponent')
    cchtml=[]
    if childComponents:
        cchtml.append('<ul>')
        cchtml.append('<li>')
        cchtml.append('<h5>Child Components</h5>')
        cchtml.append('<div class="inner">')
        for cc in childComponents:
            modshortname = cc.find('shortName')
            cchtml.append('<ul>')
            cchtml.append('<li>')
            cchtml.append('<h5>%s</h5>' %modshortname.text)
            cchtml.append('<div class="inner">')
            main_model_iter(cc, cchtml)
            cchtml.append('</div>')
            cchtml.append('</li>')
            cchtml.append('</ul>')
        cchtml.append('</div>')
        cchtml.append('</li>')
        cchtml.append('</ul>')

    return cchtml


def main_model_iter(elemroot, modelhtml):
    """
    Manage the iteration through and harvesting of CIM modelComponent sections
    """
    # find and mark up top level component info
    mihtml = get_mihtml(elemroot)
    modelhtml += mihtml

    # find and mark up responsible party info
    rphtml = get_rphtml(elemroot)
    modelhtml += rphtml

    # find and mark up component properties
    cphtml = get_cphtml(elemroot)
    modelhtml += cphtml

    # find and mark up citation information
    cithtml = get_cithtml(elemroot)
    modelhtml += cithtml

    # find and mark up document information
    dihtml = get_dihtml(elemroot)
    modelhtml += dihtml

    # find and mark up child component information
    cchtml = get_cchtml(elemroot)
    modelhtml += cchtml
    
    return modelhtml

def get_modelhtml(cimxml):
    """
    Generate a block of html code to render a modelComponent view.
    """
    #Get the model name for the html heading
    modshortname = get_component_shortname(cimxml)

    #Generate the outer html code
    modelhtml=[]
    modelhtml.append('<div id="acc_wrapper">')
    modelhtml.append('    <div id="content">')
    modelhtml.append('        <div id="container">')
    modelhtml.append('            <div id="main">')
    modelhtml.append('<ul class="accordion" id="acc1">')
    modelhtml.append('<li>')
    modelhtml.append('<h4 class="acc_docheader">Model: %s</h4>' %modshortname.text)
    modelhtml.append('<div class="inner">')

    #Iterate through the model xml and harvest all required information
    main_model_iter(cimxml, modelhtml)

    #Complete the outer html code
    modelhtml.append('</div>')
    modelhtml.append('</li>')
    modelhtml.append('</ul>')
    modelhtml.append('</div>')
    modelhtml.append('</div>')
    modelhtml.append('</div>')
    modelhtml.append('</div>')
    modelhtml.append('<br/>')

    return modelhtml
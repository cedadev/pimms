# -*- coding: utf-8 -*-
# provides unit tests for some questionnaire models

from pimms_apps.qn.models import *
from lxml import etree as ET
import unittest

class TestFunctions(unittest.TestCase): 

    def testhackRP(self):
        ''' Test my nasty metadata maintainer hack '''
        xml='''<ns0:author xmlns:ns0="http://www.metaforclimate.eu/cim/1.1" xmlns:gmd="http://foo.bar"
               xmlns:gco="http://foo1.bar">
        <gmd:CI_ResponsibleParty>
            <gmd:individualName>
                <gco:CharacterString> Charlotte Pascoe </gco:CharacterString>
            </gmd:individualName>
            <gmd:organisationName>
                <gco:CharacterString> BADC, CEDA, STFC </gco:CharacterString>
            </gmd:organisationName>
            <gmd:contactInfo>
                <gmd:CI_Contact>
                    <gmd:address>
                        <gmd:CI_Address>
                            <gmd:electronicMailAddress>
                                <gco:CharacterString> charlotte.pascoe@stfc.ac.uk
                                </gco:CharacterString>
                            </gmd:electronicMailAddress>
                        </gmd:CI_Address>
                    </gmd:address>
                </gmd:CI_Contact>
            </gmd:contactInfo>
            <gmd:role>
                <gmd:CI_RoleCode
                    codeListValue="http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#CI_RoleCode"
                    codeList="originator"/>
            </gmd:role>
        </gmd:CI_ResponsibleParty>
        </ns0:author>
        '''
        e=ET.fromstring(xml)
        rp=ResponsibleParty.fromXML(e)
        self.assertEqual(rp.email,'Charlotte.Pascoe@stfc.ac.uk')

    def testCalender(self):
        ''' test calendar class '''
        xml='''
        <ns0:calendar xmlns:ns0="http://www.metaforclimate.eu/cim/1.1">
        <ns0:perpetualPeriod/>
        </ns0:calendar>
        '''
        e=ET.fromstring(xml)
        c=Calendar(e)
        self.assertEqual(c.name,'perpetualPeriod')

    def testSimDate(self):
        ''' Simple zero date test, no calendar '''
        sd='0000-01-01T00:00:00Z'
        d=SimDateTime(sd)
        self.assertEqual(str(sd),sd)
        sd='-19000-01-01T00:00:00Z'
        d=SimDateTime(sd)
        self.assertEqual(d.year,-19000)
        sd='-19000-01-01'
        d=SimDateTime(sd)
        self.assertEqual(d.year,-19000)
    
    def testDateRange2(self):
        ''' Complex date range from a constraint (Hansen experiment) '''
        cxml='''
        <ns0:calendar xmlns:ns0="http://www.metaforclimate.eu/cim/1.1">
        <ns0:perpetualPeriod/>
        </ns0:calendar>
        '''
        xml='''
        <outputPeriod>
        <startDate>0000-01-01T00:00:00Z</startDate>
        <length units="years">1</length>
        <description>For one year between year 0 and year 25</description>
        </outputPeriod>
        '''
        e=ET.fromstring(xml)
        x=DateRange.fromXML(e)
        self.assertEqual(str(x.length),'1.0 years')

    def testDateRange3(self):
        ''' Complex date range from a constraint (Hansen experiment) with namespace'''
        cxml='''
        <ns0:calendar xmlns:ns0="http://www.metaforclimate.eu/cim/1.1">
        <ns0:perpetualPeriod/>
        </ns0:calendar>
        '''
        xml='''
        <outputPeriod xmlns="http://www.metaforclimate.eu/cim/1.1">
        <startDate>0000-01-01T00:00:00Z</startDate>
        <length units="years">1</length>
        <description>For one year between year 0 and year 25</description>
        </outputPeriod>
        '''
        e=ET.fromstring(xml)
        x=DateRange.fromXML(e)
        # currently we expect this to fail with a namespace in it 
        self.assertEqual(str(x.length),'1.0 years')
        
    def testRoundTripDateRange(self):
        ''' Interested in what happens with round tripping into and out of python classes for storage '''
        xml='''
        <outputPeriod xmlns="http://www.metaforclimate.eu/cim/1.1">
        <startDate>0000-01-01T00:00:00Z</startDate>
        <length units="years">1</length>
        <description>For one year between year 0 and year 25</description>
        </outputPeriod>
        '''
        d0=DateRange.fromxml(xml)
        ds0=d0.startDate
        e=d0.xml()
        print '==\n',ET.tostring(e),'\n==\n'
        d1=DateRange.fromXML(e)
        ds1=d1.startDate
        self.assertEqual(str(ds0),str(ds1))
        
    def testExperiment(self):
        ''' Just test the Hansen experiment by itself '''
        f='data/experiments/6.2a.HansenBaseline.xml'
        x=Experiment.fromXML(f)
        
    def testExpt2(self):
        ''' Bryan's play example '''
        f='data/experiments/bryanPlay.xml'
        x=Experiment.fromXML(f)
        
    def NOtestExperiments(self):
        import os
        d='data/experiments/'
        for f in os.listdir(d):
            if f.endswith('.xml'):
                x=Experiment.fromXML(os.path.join(d, f)) 

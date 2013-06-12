# -*- coding: utf-8 -*-
# convenience stuff for XML handling 

import unittest
from lxml import etree as ET

cimv='http://www.metaforclimate.eu/cim/1.1'
gmd='http://www.isotc211.org/2005/gmd'
gco="http://www.isotc211.org/2005/gco"
typekey='{http://www.w3.org/2001/XMLSchema-instance}type'

class etTxt:
    ''' Simplify handling getting text values out of an element tree element, in the situation where you expect
    to see them using a namespace ... or not '''
    def __init__(self,e=None):
        ''' Initialise and guess namespaces '''
        if e is None:
            self.ns=cimv
        else:
            if e.nsmap=={}:
                self.ns=''
            else:
                self.ns=e.nsmap[None]
        if self.ns: self.ns='{%s}'%self.ns
    def get(self,elem,path):
        e=elem.find('%s%s'%(self.ns,path))
        if e is None:
            return ''
        else: 
            r=(e.text or '')
        return r.strip()
    def getN(self,elem,path):
        r=self.get(elem,path)
        if r=='': return None
        return r
    def find(self,elem,path):
        return elem.find('%s%s'%(self.ns,path))
        
class TestFunctions(unittest.TestCase): 

    def testwithns(self):
        s='<foo xmlns="http://name.space"><bar>value</bar></foo>'
        e=ET.fromstring(s)
        self.assertEqual(e.find('{http://name.space}bar').text,'value')
        g=etTxt(e)
        self.assertEqual(g.get(e,'bar'),'value')
        
    def testnons(self):
        s='<foo><bar>value</bar></foo>'
        e=ET.fromstring(s)
        self.assertEqual(e.find('bar').text,'value')
        g=etTxt(e)
        self.assertEqual(g.get(e,'bar'),'value')
    
    def test1(self):
       s='<foo xmlns="%s"><bar>value</bar></foo>'%cimv
       e=ET.fromstring(s)
       g=etTxt(e)
       self.assertEqual(g.get(e,'bar'),'value')

if __name__=="__main__":
    unittest.main()

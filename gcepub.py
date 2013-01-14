#-------------------------------------------------------------------------------
# Name:        gcepub
# Purpose:      extract the catalog from epub string
#
# Author:      Hu Jun
#
# Created:     29/01/2011
# Copyright:   (c) Hu Jun 2011
# Licence:     Apache2
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import xml.parsers.expat
import re
import HTMLParser




class GCEPUB:
    def __init__(self,instr):
        self.ecount=0
        self.start_e=False
        self.rlist={}
        self.start_txt=False
        self.cur_txt=''
        self.cur_url=''
        self.instr=instr
        self.Parser = xml.parsers.expat.ParserCreate()
        self.Parser.CharacterDataHandler = self.getdata
        self.Parser.StartElementHandler = self.start_ef
        self.Parser.EndElementHandler = self.end_ef
##        self.Parser.SetParamEntityParsing(xml.parsers.expat.XML_PARAM_ENTITY_PARSING_UNLESS_STANDALONE)
        self.h=HTMLParser.HTMLParser()
        self.instr=self.instr.replace('&lt;','')
        self.instr=self.instr.replace('&gt;','')


    def start_ef(self,name,attrs):

        if name.lower()=='navpoint':
            self.start_e=True
        if name.lower()=='text' and self.start_e:
            self.start_txt=True
        if name.lower()=='content' and self.start_e:
            self.cur_url=attrs['src']


    def getdata(self,data):
        if self.start_txt:
            self.cur_txt=data

    def end_ef(self,name):
        if name.lower()=='navpoint':
            self.start_e=False
            self.start_txt=False
            self.rlist[self.cur_url]=self.h.unescape(self.cur_txt)
            self.ecount+=1
        if name.lower()=='text':
            self.start_txt=False

    def parser(self):
        self.Parser.Parse(self.instr,1)

    def GetRList(self):
        return self.rlist


if __name__ == '__main__':
    f=open('toc.ncx','r')
    m=GetCatalogFromEPUB(f.read())
    for x in m:
        print x[0],":::::",x[1]
    f.close()

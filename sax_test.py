#!env python
from __future__ import with_statement
from xml.sax import parse
from xml.sax.handler import ContentHandler

class PrintTags(ContentHandler):
    def startElement(self, name, attrs):
        print name

with open("Table_Coefficients.xml") as fi:
    parse(fi, PrintTags())
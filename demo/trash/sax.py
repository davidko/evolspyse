#!/usr/bin/env python

"""Spyse sax demo"""

from xml.sax import make_parser
from xml.sax.handler import ContentHandler

class BookHandler(ContentHandler):
    book = {}
    inside_tag = 0
    data = ""

    def startDocument(self):
            print "<html>"

    def endDocument(self):
            print "</html>"

    def startElement(self, el, attr):
        if el == "pythonbooks":
            print "<table border='1'>"
            print "<tr>"
            print "<th>Author(s)</th><th>Title</th><th>Publisher</th>"
            print "</tr>"
        elif el == "book": 
            self.book = {}
        elif el in ["author","publisher","title"]:
            self.inside_tag = 1

    def endElement(self, el):
        if el == "pythonbooks":
            print "</table>"
        elif el == "book":
            print "<tr>"
            print "<td>%s</td><td>%s</td><td>%s</td>" % \
                (self.book['author'], 
                self.book['title'], 
                self.book['publisher'])
            print "</tr>"
        elif el in ["author","publisher","title"]:
            self.book[el] = self.data
            self.data = ''
            self.inside_tag = 0

    def characters(self, chars):
        if self.inside_tag:
            self.data+=chars

# Content handler
bh = BookHandler()

# Instantiate parser
parser = make_parser()

# Register content handler
parser.setContentHandler(bh)

# Parse XML file
fp = open('pythonbooks.xml','r')
parser.parse(fp)


__author__ = 'geekscruff'

"""Handles adding different types of triple to the repository, function names should be self explanatory"""

from franz.openrdf.vocabulary.rdf import RDF
from franz.openrdf.vocabulary.rdfs import RDFS
import rfc3987
import logging

logger = logging.getLogger(__name__)

# TODO there is built in support for RDF RDFS AND OWL, could add classes for common namespaces

class AddTriple():
    def __init__(self, conn):  # conn is the repository connection
        logger.debug('DEBUG add_triple.py - object instantiated')
        self.conn = conn
        self.sub = ""
        self.contexts = []

    # Predefine the subject - we may want to add multiple triples for the same subject
    def setupsubject(self, sub):
        logger.info('INFO add_triple.py - setup subject %s', sub)
        try:
            if str(rfc3987.match(sub, rule='URI')) != 'None':
                self.sub = sub
            else:
                raise Exception("This is not a valid URI")
        except Exception as e:
            logger.error("ERROR! add_triple.py - " + e.message)

    def setcontexts(self, contexts):
        self.contexts = contexts

    def addliteral(self, p, o):
        try:
            s = self.conn.createURI(self.sub)
            if str(rfc3987.match(p, rule='URI')) != 'None':
                p = self.conn.createURI(p)
            else:
                raise Exception("This is not a valid URI")
            o = self.conn.createLiteral(o)
            logger.debug("DEBUG add_triple.py - add literal <%s> %s '%s'", self.sub, p, o)
            if len(self.contexts) > 0:
                self.conn.add(s, p, o, contexts=self.contexts)
            else:
                self.conn.add(s, p, o)
        except Exception as e:
            logger.error("ERROR! add_triple.py - " + e.message)

    def adduri(self, p, o):

        try:
            s = self.conn.createURI(self.sub)
            if str(rfc3987.match(p, rule='URI')) != 'None':
                p = self.conn.createURI(p)
            else:
                raise Exception("This is not a valid URI")
            if str(rfc3987.match(o, rule='URI')) != 'None':
                o = self.conn.createURI(o)
            else:
                raise Exception("This is not a valid URI")
            logger.info("INFO add_triple.py - add uri <%s> %s %s", self.sub, p, o)
            if len(self.contexts) > 0:
                self.conn.add(s, p, o, contexts=self.contexts)
            else:
                self.conn.add(s, p, o)
        except Exception as e:
            logger.error("ERROR! add_triple.py - " + e.message)

    def addrdftype(self, o):
        try:
            s = self.conn.createURI(self.sub)
            if str(rfc3987.match(o, rule='URI')) != 'None':
                o = self.conn.createURI(o)
            else:
                raise Exception("This is not a valid URI")
            logger.info("INFO add_triple.py - add rdf type <%s> <rdf:type> %s", self.sub, o)
            if len(self.contexts) > 0:
                self.conn.add(s, RDF.TYPE, o, contexts=self.contexts)
            else:
                self.conn.add(s, RDF.TYPE, o)
        except Exception as e:
            logger.error("ERROR! add_triple.py - " + e.message)

    def addrdflabel(self, o):
        logger.info("INFO add_triple.py - add rdf type <%s> <rdfs:label> %s", self.sub, o)
        if len(self.contexts) > 0:
            self.conn.add(self.conn.createURI(self.sub), RDFS.LABEL, o, contexts=self.contexts)
        else:
            self.conn.add(self.conn.createURI(self.sub), RDFS.LABEL, o)
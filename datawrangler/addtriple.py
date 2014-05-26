__author__ = 'geekscruff'

from franz.openrdf.vocabulary.rdf import RDF
from franz.openrdf.vocabulary.rdfs import RDFS
import rfc3987
import logging

logger = logging.getLogger(__name__)

# TODO there is built in support for RDF RDFS AND OWL, could add classes for common namespaces
# Handles adding different types of triple to the repository, most of the def names should be self explanatory


class AddTriple():
    def __init__(self, conn):  # conn is the repository connection
        logger.debug('DEBUG addtriple.py - object instantiated', sub)
        self.conn = conn
        self.sub = ""

    # Predefine the subject - we may want to add multiple triples for the same subject
    def setupsubject(self, sub):
        logger.info('INFO addtriple.py - setup subject %s', sub)
        try:
            if str(rfc3987.match(sub, rule='URI')) != 'None':
                self.sub = sub
            else:
                raise Exception("This is not a valid URI")
        except Exception as e:
            logger.error("ERROR! addtriple.py - " + e.message)

    def addliteral(self, p, o):
        try:
            s = self.conn.createURI(self.sub)
            if str(rfc3987.match(p, rule='URI')) != 'None':
                p = self.conn.createURI(p)
            else:
                raise Exception("This is not a valid URI")
            o = self.conn.createLiteral(o)
            logger.debug("DEBUG addtriple.py - add literal <%s> %s '%s'", self.sub, p, o)
            self.conn.add(s, p, o)
        except Exception as e:
            logger.error("ERROR! addtriple.py - " + e.message)

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
            logger.info("INFO addtriple.py - add uri <%s> %s %s", self.sub, p, o)
            self.conn.add(s, p, o)
        except Exception as e:
            logger.error("ERROR! addtriple.py - " + e.message)

    def addrdftype(self, o):
        try:
            s = self.conn.createURI(self.sub)
            if str(rfc3987.match(o, rule='URI')) != 'None':
                o = self.conn.createURI(o)
            else:
                raise Exception("This is not a valid URI")
            logger.info("INFO addtriple.py - add rdf type <%s> <rdf:type> %s", self.sub, o)
            self.conn.add(s, RDF.TYPE, o)
        except Exception as e:
            logger.error("ERROR! addtriple.py - " + e.message)

    def addrdflabel(self, o):
        s = self.conn.createURI("http://dbpedia.org/void/Dataset")
        o = self.conn.createLiteral("http://rdfs.org/ns/void#Dataset")
        logger.info("INFO addtriple.py - add rdf type <%s> <rdfs:label> %s", self.sub, o)
        self.conn.add(s, RDFS.LABEL, o)
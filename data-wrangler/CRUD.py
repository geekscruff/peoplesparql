__author__ = 'geekscruff'

from rdfalchemy.sparql.sesame2 import SesameGraph
from rdfalchemy.rdfSubject import rdfSubject
from rdflib.term import Literal, URIRef

rdfSubject.db = SesameGraph('http://geekscruff.me/openrdf-sesame/repositories/SYSTEM')

#it fucking worked!!!

#rdfSubject.db.add((URIRef('http://example.com/book5'),URIRef('http://purl.org/dc/elements/1.1/creator'),Literal('another thing')))
#rdfSubject.db.set((URIRef('http://example.com/book5'),URIRef('http://purl.org/dc/elements/1.1/creator'),Literal('summinkelse the second')))
#rdfSubject.db.add((URIRef('http://example.com/book5'),URIRef('http://purl.org/dc/elements/1.1/publisher'),Literal('the wrong publisher')))
#rdfSubject.db.remove((URIRef('http://example.com/book5'),URIRef('http://purl.org/dc/elements/1.1/publisher'),Literal('the wrong publisher')))
#rdfSubject.db.add((URIRef('http://example.com/book5'),URIRef('http://purl.org/dc/elements/1.1/publisher'),Literal('the right publisher number 2')))

rdfSubject.db.add((URIRef(':node18i7ivai3x5'),URIRef('http://www.ontotext.com/trree/owlim#flush'),Literal('True')))

#responses = {}
#x = set(list(rdfSubject.db.query(q1, resultMethod='xml')))
#print(x)
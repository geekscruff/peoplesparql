__author__ = 'geekscruff'

from rdflib import Graph
from rdflib.graph import ConjunctiveGraph

import json
import urllib


for s, p, o in g:
  print s, p, o

# BadSyntax boo

#g = Graph()

# g.parse('http://dbpedia.org/resource/Philippe_Mercier')
# g.parse("http://yago-knowledge.org/resource/Philippe_Mercier")
# g.parse("http://rdf.freebase.com/ns/m.05q8cn7")
# g.parse("http://www.wikidata.org/entity/Q3380372")
# g.parse("http://viaf.org/viaf/7657501/rdf")
#print(len(g))

# import pprint
# for stmt in g:
    # pprint.pprint(stmt)
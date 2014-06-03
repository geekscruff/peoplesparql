__author__ = 'geekscruff'

from unittest import TestCase
from querybuilder import sparql_query
import json

class TestSparqlQuery(TestCase):
    def setUp(self):
        r = sparql_query.SparqlQuery('AND', 'http://factforge.net/sparql')
        return r

    #'http://data.archiveshub.ac.uk/sparql'

    def test_endpointnamesearch(self):
        r = self.setUp()
        results = str(r.namesearch('T. E. Lawrence'))
        self.assertIn("Beatrice", results)

    # def test_endpointallsearch(self):
    #     r = sparql_query.SparqlQuery('AND', 'http://data.archiveshub.ac.uk/sparql')
    #     r.buildtypeandlabel()
    #     self.assertIn('webbmarthabeatrice1858-1943socialreformer', str(r.allsearch('http://data.archiveshub.ac.uk/id/person/nra/webbmarthabeatrice1858-1943socialreformer')))
    #
    # def test_endpointallsearch_dbpedia(self):
    #     r = self.setUp()
    #     r.buildtypeandlabel()
    #     self.assertIn('Charles_Darwin', str(r.allsearch('http://dbpedia.org/resource/Charles_Darwin')))

    # def test_getendpoint(self):
    #     r = self.setUp()
    #     res = r.getendpointdetails()
    #     print(res)
    #     self.assertIn('Charles_Darwin', res)
__author__ = 'geekscruff'

from unittest import TestCase
from querybuilder import sparql_query
import json

class TestSparqlQuery(TestCase):
    def setUp(self):
        r = sparql_query.SparqlQuery('AND', 'http://localhost:10035/catalogs/public-catalog/repositories/artworldppl')
        return r

    #'http://data.archiveshub.ac.uk/sparql'

    def test_endpointnamesearch(self):
        r = self.setUp()
        results = str(r.namesearch('Lely'))
        self.assertIn("Lely", results)

    def test_endpointallsearch(self):
        r = self.setUp()
        results = str(r.allsearch('http://dlib.york.ac.uk/id/person/35403', 'all'))
        self.assertIn("Maingaud", results)

    def test_endpointallsearchuri(self):
        r = self.setUp()
        results = str(r.allsearch('http://dlib.york.ac.uk/id/person/35403', 'uri'))
        self.assertNotIn("Maingaud", results)

    def test_endpointallsearchliteral(self):
        r = self.setUp()
        results = str(r.allsearch('http://dlib.york.ac.uk/id/person/35403', 'literal'))
        self.assertIn("Maingaud", results)

    # def test_endpointallsearch_dbpedia(self):
    #     r = self.setUp()
    #     r.buildtypeandlabel()
    #     self.assertIn('Charles_Darwin', str(r.allsearch('http://dbpedia.org/resource/Charles_Darwin')))

    # def test_getendpoint(self):
    #     r = self.setUp()
    #     res = r.getendpointdetails()
    #     print(res)
    #     self.assertIn('Charles_Darwin', res)
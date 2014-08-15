__author__ = 'geekscruff'

from unittest import TestCase
from querybuilder import sparql_select

class TestSelect(TestCase):

    def createep(self, ep):
        r = sparql_select.SparqlSelect("?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person>", ep, limit=1, sel="?s")
        return r

    def test_select_true(self):
        r = self.createep('http://bnb.data.bl.uk/sparql')
        results = r.select()
        self.assertNotIn("[]", str.lower(str(results)))

    def test_select_false(self):
        r = self.createep('http://collection.britishmuseum.org/sparql')
        results = r.select()
        self.assertIn("[]", str.lower(str(results)))

    def test_select_namedgraph(self):
        r = sparql_select.SparqlSelect('?s ?p ?o',
            'http://localhost:10035/catalogs/public-catalog/repositories/test2',
            dist=True, ng='<http://geekscruff.me/tmp#j.allinson@gmail.com>')
        results = r.select()
        self.assertIn("geekscruff", str.lower(str(results)))

    def test_select_inferredinbm(self):
        #select distinct ?o where { <http://collection.britishmuseum.org/id/object/ESA2078/find> a ?o }
        r = sparql_select.SparqlSelect('<http://collection.britishmuseum.org/id/object/ESA2078/find> a ?o',
            'http://collection.britishmuseum.org/sparql', sel='?o', dist=True)
        results = r.select()
        # this proves bm endpoint is returning inferred results
        self.assertIn('http://erlangen-crm.org/current/E5_Event', str(results))

    def test_select_inferredinDBP(self):
        r = sparql_select.SparqlSelect('<http://dbpedia.org/resource/John_Stevens_Henslow> a ?o',
            'http://dbpedia.org/sparql', sel='?o', dist=True)
        results = r.select()
        # this proves bm endpoint is returning inferred results
        print results
        self.assertIn('http://erlangen-crm.org/current/E5_Event', str(results))
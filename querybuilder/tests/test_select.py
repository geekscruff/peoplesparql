__author__ = 'geekscruff'

from unittest import TestCase
from querybuilder import sparql_select

class TestAsk(TestCase):
    def createep(self, ep):
        r = sparql_select.SparqlSelect("?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person>", ep, 1, "?s")
        return r

    def test_select_true(self):
        r = self.createep('http://bnb.data.bl.uk/sparql')
        results = r.select()
        self.assertNotIn("[]", str.lower(str(results)))

    def test_select_false(self):
        r = self.createep('http://collection.britishmuseum.org/sparql')
        results = r.select()
        self.assertIn("[]", str.lower(str(results)))
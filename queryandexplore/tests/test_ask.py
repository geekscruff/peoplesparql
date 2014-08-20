__author__ = 'geekscruff'

from unittest import TestCase
from queryandexplore import sparql_ask


class TestAsk(TestCase):
    def createep(self, ep):
        r = sparql_ask.SparqlAsk("?s rdf:type <http://xmlns.com/foaf/0.1/Person>", ep)
        self.ep = ep
        return r

    def test_ask_error(self):
        r = self.createep('http://bnb.data.bl.uk/sparql')
        results = r.ask()
        self.assertEqual("error", str.lower(str(results)))

    def test_ask_true(self):
        r = self.createep('http://dbpedia.org/sparql')
        results = r.ask()
        self.assertIn("true", str.lower(str(results)))

    def test_ask_false(self):
        r = self.createep('http://collection.britishmuseum.org/sparql')
        results = r.ask()
        self.assertIn("false", str.lower(str(results)))